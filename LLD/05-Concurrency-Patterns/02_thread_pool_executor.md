# Thread Pool / Executor

> **Reuse** a fixed set of worker threads to run many short tasks — avoid per-task thread creation overhead and unbounded thread explosion.

## Plain English

Instead of hiring a new worker for every small job, you keep N workers on staff. Submit tasks to a queue; idle workers pick them up. You cap parallelism and control resource usage.

## Simple analogy

A taxi stand with 10 cabs, not “spawn a new cab company for every passenger.”

## Why seniors get asked this

Web servers, batch processors, rate-limited API callers — seniors size the pool, handle failures, and explain when threads vs processes vs goroutines fit.

## Good: fixed worker pool

### Python

```python
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch_user(user_id: int) -> dict:
    # pretend I/O-bound HTTP call
    return {"id": user_id, "name": f"user-{user_id}"}


def main() -> None:
    ids = range(1, 21)
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(fetch_user, uid) for uid in ids]
        for fut in as_completed(futures):
            print(fut.result())  # re-raises worker exceptions here


if __name__ == "__main__":
    main()
```

For **CPU-bound** Python work, prefer `ProcessPoolExecutor` — the GIL limits parallel CPU on threads.

### Go

```go
package main

import (
    "context"
    "fmt"
    "sync"
)

type Job struct {
    ID int
}

func worker(ctx context.Context, id int, jobs <-chan Job, wg *sync.WaitGroup) {
    defer wg.Done()
    for {
        select {
        case <-ctx.Done():
            return
        case job, ok := <-jobs:
            if !ok {
                return
            }
            fmt.Printf("worker %d handled job %d\n", id, job.ID)
        }
    }
}

func main() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    const workers = 4
    jobs := make(chan Job, 8)
    var wg sync.WaitGroup

    for i := 0; i < workers; i++ {
        wg.Add(1)
        go worker(ctx, i, jobs, &wg)
    }

    for id := 1; id <= 20; id++ {
        jobs <- Job{ID: id}
    }
    close(jobs)
    wg.Wait()
}
```

Go goroutines are cheap; a “pool” still helps when you must **cap** concurrency (DB connections, API rate limits).

## Concurrency safety

| Concern | What to watch |
|---------|----------------|
| **Race** | Workers sharing mutable state (counters, caches) need locks or confinement. The pool itself doesn’t make your task code thread-safe. |
| **Deadlock** | Pool exhaustion: submitting from a worker and waiting on another task on the **same** pool can deadlock if all workers are busy. |
| **Backpressure** | Unbounded submit queues grow forever. Use bounded queues or `Semaphore` to limit in-flight tasks. |

**Python GIL:** thread pools help **I/O-bound** work (releases GIL during I/O). They don’t multiply CPU throughput for pure Python compute.

## When to use / not use

**Use:** many small independent tasks; I/O-bound fan-out; limiting concurrent DB/API calls.

**Don’t use:** one long-lived sequential pipeline (producer–consumer may be clearer); CPU-heavy Python without `ProcessPoolExecutor`; when `asyncio` already fits your I/O model.

## Pitfalls

- `max_workers=1000` on I/O — may exhaust sockets/file descriptors.
- Swallowing exceptions in workers — always surface via `Future.result()` or logging.
- Copying a struct with `sync.Mutex` in Go — mutexes must not be copied; use pointers or confine the mutex to one goroutine (actor).
- Shutting down without waiting for in-flight tasks.

## Interview trigger phrase

> “I’d use a **fixed thread pool** sized to our I/O or connection limits, with bounded submission so we don’t queue unbounded work in memory.”

## Exercise

You must call 50 third-party APIs (mock), max 5 concurrent, 2s timeout each.

1. Thread pool size? How do you enforce 5 concurrent?
2. One API hangs — how does timeout propagate?
3. Python: threads or `asyncio`? When would you switch?
