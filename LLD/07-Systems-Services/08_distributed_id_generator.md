# Distributed ID Generator

> Unique IDs (Snowflake-style) → **concurrency + bit packing**. 🟡

## Scope / Requirements

**In scope**
- Generate unique 64-bit (or string) IDs without a central DB auto-increment.
- Snowflake-style: timestamp | worker_id | sequence.
- Thread-safe next-id under load.

**Out of scope**
- Full Twitter Snowflake ops story, UUID v7 deep dive beyond mention, multi-region clock governance product.

**Domain invariants**
- IDs unique within the deployment **as long as** (worker_id unique) ∧ (clock doesn’t move backward unhandled) ∧ (sequence doesn’t overflow silently within same ms).
- Time component is non-decreasing for a worker (wait or throw on clock skew).
- Sequence resets when millisecond changes; increments within same ms.

## Core Entities & Responsibilities

| Entity | Responsibility |
|--------|----------------|
| `SnowflakeGenerator` | Pack bits; sync next id. |
| `Clock` | Current millis. |
| `WorkerID` config | 0..2^k-1 unique per process. |

## Key Interfaces / Patterns

- **Bit packing** as the design (not a GoF pattern) — senior signal is correctness under concurrency.
- Optional **Strategy** for UUID vs Snowflake vs DB segment.

## End-to-End Flow

1. Configure epoch, worker id.
2. `next_id()`: read time → if same ms, seq++ → if overflow, wait next ms → pack bits → return.
3. On clock rollback: wait until caught up or error.

## Python Skeleton

```python
from threading import Lock
import time


class SnowflakeGenerator:
    """
    64-bit: 1 sign unused | 41 timestamp_ms | 10 worker | 12 sequence
    """

    def __init__(self, worker_id: int, epoch_ms: int = 1_704_067_200_000):
        if not 0 <= worker_id < 1024:
            raise ValueError("worker_id 0..1023")
        self.worker_id = worker_id
        self.epoch = epoch_ms
        self.seq = 0
        self.last_ms = -1
        self._lock = Lock()

    def _now_ms(self) -> int:
        return int(time.time() * 1000)

    def _wait_next_ms(self, last: int) -> int:
        ms = self._now_ms()
        while ms <= last:
            ms = self._now_ms()
        return ms

    def next_id(self) -> int:
        with self._lock:
            ms = self._now_ms()
            if ms < self.last_ms:
                # clock moved backward — wait
                ms = self._wait_next_ms(self.last_ms)
            if ms == self.last_ms:
                self.seq = (self.seq + 1) & 0xFFF
                if self.seq == 0:
                    ms = self._wait_next_ms(self.last_ms)
            else:
                self.seq = 0
            self.last_ms = ms
            ts = ms - self.epoch
            return (ts << 22) | (self.worker_id << 12) | self.seq
```

## Go Skeleton

```go
package idgen

import (
    "sync"
    "time"
)

type Snowflake struct {
    mu       sync.Mutex
    workerID int64
    epoch    int64
    seq      int64
    lastMs   int64
}

func NewSnowflake(workerID int64) *Snowflake {
    return &Snowflake{
        workerID: workerID,
        epoch:    1704067200000, // 2024-01-01 UTC example
        lastMs:   -1,
    }
}

func (s *Snowflake) nowMs() int64 {
    return time.Now().UnixMilli()
}

func (s *Snowflake) waitNext(last int64) int64 {
    ms := s.nowMs()
    for ms <= last {
        ms = s.nowMs()
    }
    return ms
}

func (s *Snowflake) NextID() int64 {
    s.mu.Lock()
    defer s.mu.Unlock()
    ms := s.nowMs()
    if ms < s.lastMs {
        ms = s.waitNext(s.lastMs)
    }
    if ms == s.lastMs {
        s.seq = (s.seq + 1) & 0xFFF
        if s.seq == 0 {
            ms = s.waitNext(s.lastMs)
        }
    } else {
        s.seq = 0
    }
    s.lastMs = ms
    ts := ms - s.epoch
    return (ts << 22) | (s.workerID << 12) | s.seq
}
```

## Concurrency / Consistency

- One mutex per generator instance (per process).
- Worker ID assignment: config map, Zookeeper/etcd, or AWS instance bits — must be unique.
- NTP jump backward: wait or use logical time; never duplicate.

## Extensions / Trade-offs / Pitfalls

- DB ticket servers (Flickr); UUID v4 (no sort) / v7 (time-ordered).
- Pitfall: sharing worker_id across pods → collisions.
- Pitfall: sequence overflow without waiting → duplicates.
- Extract timestamp from id for debugging.

## Interview Discussion Points

- Why not `AUTO_INCREMENT`? (write hotspot, multi-region)
- How many IDs/ms/worker? (4096 with 12-bit seq)
- Trade-offs vs ULID/UUIDv7.

## Exercise

Generate 5000 IDs in one ms-simulated loop (mock clock) and assert uniqueness + monotonicity for one worker.

**Follow-ups**
1. Decode timestamp from an ID.
2. Handle clock rollback explicitly with an error mode.
3. Compare Snowflake vs Redis `INCR` segment allocator.
