# Monitor / Mutex / Semaphore

> **Synchronization primitives** that guard critical sections (mutex/monitor) or **limit concurrent access** to a resource (semaphore).

## Plain English

- **Mutex:** only one thread at a time in the critical section (bathroom key).
- **Monitor:** mutex + condition variable — wait until a condition is true (e.g. queue not empty).
- **Semaphore:** N permits — at most N threads use a resource (parking lot with N spots).

## Simple analogy

Mutex = single-stall restroom key. Semaphore = parking garage with 50 spaces. Monitor = “wait here until your order is ready” while holding the line organized.

## Why seniors get asked this

Connection pools, seat inventory, rate limiting, bounded parallelism — seniors pick the right primitive and explain deadlock avoidance (lock ordering).

## Good: mutex for invariant + semaphore for capacity

### Python

```python
import threading


class ConnectionPool:
    def __init__(self, size: int) -> None:
        self._sema = threading.Semaphore(size)
        self._lock = threading.Lock()
        self._in_use = 0

    def acquire(self) -> None:
        self._sema.acquire()  # blocks when pool exhausted
        with self._lock:
            self._in_use += 1

    def release(self) -> None:
        with self._lock:
            self._in_use -= 1
        self._sema.release()


class SeatInventory:
    def __init__(self, total: int) -> None:
        self._available = total
        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)

    def reserve(self, count: int) -> bool:
        with self._cond:
            while self._available < count:
                self._cond.wait(timeout=1.0)
                if self._available < count:
                    return False  # gave up waiting
            self._available -= count
            return True

    def release(self, count: int) -> None:
        with self._cond:
            self._available += count
            self._cond.notify_all()
```

### Go

```go
package main

import (
    "context"
    "fmt"
    "sync"
)

type ConnectionPool struct {
    slots chan struct{} // counting semaphore — stdlib only
    mu    sync.Mutex
    inUse int
}

func NewConnectionPool(size int) *ConnectionPool {
    return &ConnectionPool{slots: make(chan struct{}, size)}
}

func (p *ConnectionPool) Acquire(ctx context.Context) error {
    select {
    case <-ctx.Done():
        return ctx.Err()
    case p.slots <- struct{}{}:
    }
    p.mu.Lock()
    p.inUse++
    p.mu.Unlock()
    return nil
}

func (p *ConnectionPool) Release() {
    p.mu.Lock()
    p.inUse--
    p.mu.Unlock()
    <-p.slots
}

type SeatInventory struct {
    mu        sync.Mutex
    available int
    cond      *sync.Cond
}

func NewSeatInventory(total int) *SeatInventory {
    s := &SeatInventory{available: total}
    s.cond = sync.NewCond(&s.mu)
    return s
}

func (s *SeatInventory) Reserve(count int) bool {
    s.mu.Lock()
    defer s.mu.Unlock()
    for s.available < count {
        s.cond.Wait() // re-check after wakeup
    }
    s.available -= count
    return true
}

func (s *SeatInventory) Release(count int) {
    s.mu.Lock()
    s.available += count
    s.cond.Broadcast()
    s.mu.Unlock()
}

func main() {
    pool := NewConnectionPool(5)
    _ = pool.Acquire(context.Background())
    seats := NewSeatInventory(100)
    fmt.Println(seats.Reserve(2))
}
```

Go stdlib has `sync.Mutex` and `sync.Cond`; a buffered channel of tokens is an idiomatic counting semaphore. `golang.org/x/sync/semaphore.Weighted` is also common when you need weighted permits.

## Concurrency safety

| Concern | What to watch |
|---------|----------------|
| **Race** | Check-then-act outside the lock (`if available > 0: available -= 1`) — always mutate under the lock. |
| **Deadlock** | Lock ordering: if thread A locks `mu1` then `mu2` and B does reverse, you can deadlock. Always acquire in a fixed global order. |
| **Spurious wakeup** | `Condition.wait` / `sync.Cond.Wait` — re-check the condition in a loop. |

**Python GIL:** `threading.Lock` and `Semaphore` are implemented in C and are the correct tools for cross-thread invariants; never assume “GIL makes it safe.”

## When to use / not use

**Use:** protecting shared mutable state; bounding DB connections; throttling concurrent API calls; wait/notify for producer–consumer.

**Don’t use:** coarse lock around entire slow I/O; semaphores when a simple bounded channel expresses the same thing in Go; locks for cross-process sync (use OS primitives or a broker).

## Pitfalls

- Holding a lock during network I/O — blocks all other threads.
- Forgotten `release()` on exception — use `try/finally` or `defer`.
- Copying `sync.Mutex` or `sync.Cond` in Go — always use pointer receivers on the owning struct.
- `notify` vs `notify_all` — missed wakeups if only one waiter should proceed but you broadcast wrong.

## Interview trigger phrase

> “I’d guard the inventory with a **mutex** and **condition variable**, and cap outbound DB calls with a **semaphore** so we never exceed connection limits.”

## Exercise

**Movie booking:** 200 seats, 500 concurrent users trying to book 1–4 seats each.

1. Mutex only vs semaphore — what does each protect?
2. Two users grab the last seat — walk through the race without a lock.
3. How do you avoid deadlock if booking also locks a `Payment` object?
