# Task Scheduler / Cron

> Recurring & one-off jobs, priorities → **priority queue + Command**. 🔴

## Scope / Requirements

**In scope**
- Schedule one-shot at time T and recurring cron-like (simplified: every N seconds).
- Priority among due jobs; execute via workers.
- Cancel by job id.

**Out of scope**
- Distributed Quartz/cluster failover, full cron expression parser (can stub), calendar TZ edge hell.

**Domain invariants**
- A job runs only when `next_run_at <= now` and status is Scheduled.
- Cancelled jobs are never executed.
- Recurring job computes next run after successful schedule tick (define: after start vs after finish).
- Job id uniquely identifies schedule entry.

## Core Entities & Responsibilities

| Entity | Responsibility |
|--------|----------------|
| `Job` / `Task` | Command: `execute()`. |
| `ScheduledTask` | Id, next run, priority, interval, payload command. |
| `Scheduler` | Heap of tasks; `schedule`, `cancel`, `tick`. |
| `Executor` / thread pool | Run due commands. |
| `Clock` | Testable time. |

## Key Interfaces / Patterns

- **Command:** job as executable object (undo rare; serialization/replay more relevant).
- **Priority queue:** order by `(next_run_at, priority)`.
- **Thread pool** for execution so scheduling loop doesn’t block.

## End-to-End Flow

1. `schedule(job, run_at=now+5s, every=10s, priority=1)`.
2. Scheduler loop: peek heap; if due, pop → submit to executor → if recurring, push next.
3. `cancel(id)` marks cancelled / removes from heap.

## Python Skeleton

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import heapq
import itertools
import time
from typing import Callable, Optional


class Job(ABC):
    @abstractmethod
    def execute(self) -> None: ...


@dataclass
class FuncJob(Job):
    fn: Callable[[], None]
    def execute(self) -> None:
        self.fn()


@dataclass(order=True)
class ScheduledTask:
    next_run: float
    priority: int
    seq: int
    id: str = field(compare=False)
    job: Job = field(compare=False)
    interval: Optional[float] = field(default=None, compare=False)  # seconds
    cancelled: bool = field(default=False, compare=False)


class Scheduler:
    def __init__(self):
        self._heap: list[ScheduledTask] = []
        self._tasks: dict[str, ScheduledTask] = {}
        self._seq = itertools.count()

    def schedule(self, task_id: str, job: Job, run_at: float, priority: int = 0, interval: float | None = None) -> None:
        t = ScheduledTask(run_at, priority, next(self._seq), task_id, job, interval)
        self._tasks[task_id] = t
        heapq.heappush(self._heap, t)

    def cancel(self, task_id: str) -> None:
        if task_id in self._tasks:
            self._tasks[task_id].cancelled = True

    def tick(self, now: float | None = None) -> list[str]:
        now = now if now is not None else time.time()
        ran = []
        while self._heap and self._heap[0].next_run <= now:
            t = heapq.heappop(self._heap)
            if t.cancelled:
                continue
            t.job.execute()
            ran.append(t.id)
            if t.interval is not None and not t.cancelled:
                nxt = ScheduledTask(
                    t.next_run + t.interval, t.priority, next(self._seq),
                    t.id, t.job, t.interval,
                )
                self._tasks[t.id] = nxt
                heapq.heappush(self._heap, nxt)
        return ran
```

## Go Skeleton

```go
package scheduler

import (
    "container/heap"
    "sync"
    "time"
)

type Job interface{ Execute() }

type Task struct {
    ID       string
    NextRun  time.Time
    Priority int // lower = higher priority
    Interval time.Duration // 0 = one-shot
    Job      Job
    Cancelled bool
    index    int
}

type taskHeap []*Task

func (h taskHeap) Len() int { return len(h) }
func (h taskHeap) Less(i, j int) bool {
    if h[i].NextRun.Equal(h[j].NextRun) {
        return h[i].Priority < h[j].Priority
    }
    return h[i].NextRun.Before(h[j].NextRun)
}
func (h taskHeap) Swap(i, j int) { h[i], h[j] = h[j], h[i]; h[i].index, h[j].index = i, j }
func (h *taskHeap) Push(x any)  { *h = append(*h, x.(*Task)) }
func (h *taskHeap) Pop() any {
    old := *h
    n := len(old)
    item := old[n-1]
    *h = old[:n-1]
    return item
}

type Scheduler struct {
    mu    sync.Mutex
    heap  taskHeap
    tasks map[string]*Task
}

func New() *Scheduler {
    s := &Scheduler{tasks: map[string]*Task{}}
    heap.Init(&s.heap)
    return s
}

func (s *Scheduler) Schedule(t *Task) {
    s.mu.Lock()
    defer s.mu.Unlock()
    s.tasks[t.ID] = t
    heap.Push(&s.heap, t)
}

func (s *Scheduler) Cancel(id string) {
    s.mu.Lock()
    defer s.mu.Unlock()
    if t, ok := s.tasks[id]; ok {
        t.Cancelled = true
    }
}

func (s *Scheduler) Tick(now time.Time) {
    s.mu.Lock()
    defer s.mu.Unlock()
    for s.heap.Len() > 0 {
        t := s.heap[0]
        if t.NextRun.After(now) {
            break
        }
        heap.Pop(&s.heap)
        if t.Cancelled {
            continue
        }
        job := t.Job
        // unlock while running in production
        job.Execute()
        if t.Interval > 0 && !t.Cancelled {
            nxt := &Task{ID: t.ID, NextRun: t.NextRun.Add(t.Interval), Priority: t.Priority, Interval: t.Interval, Job: t.Job}
            s.tasks[t.ID] = nxt
            heap.Push(&s.heap, nxt)
        }
    }
}
```

## Concurrency / Consistency

- Separate schedule lock from execution; don’t hold heap lock while `Execute`.
- Missed fires while down: catch-up policy vs skip — **state it**.
- Distributed: leader election + DB `FOR UPDATE SKIP LOCKED` for due rows.

## Extensions / Trade-offs / Pitfalls

- Full cron parser; jitter; dead-letter on repeated failure.
- Pitfall: lazy cancel leaving stale heap entries — OK if cancelled flag checked.
- Pitfall: recurring schedule drifts if you use `now+interval` vs `next_run+interval`.

## Interview Discussion Points

- Heap key design: time then priority.
- At-least-once execution if process crashes mid-job — idempotent jobs.
- Cron vs interval — how would you store expressions?

## Exercise

Schedule a one-shot and a 2s recurring job; drive with manual `tick(now)`.

**Follow-ups**
1. Add priority so two due jobs run high-priority first.
2. Run `Execute` on a worker pool without blocking `Tick`.
3. Design DB schema for a multi-node scheduler.
