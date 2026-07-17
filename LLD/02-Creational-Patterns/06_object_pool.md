# Object Pool

> **Reuse** a fixed set of expensive-to-create objects instead of allocating and destroying them repeatedly.

## Plain English

Creating a DB connection or a warm ML session is slow. Keep a pool of ready instances: borrow → use → return. Cap the pool so you don’t open 10,000 connections.

## Why seniors get asked this

Connection pools, thread/worker pools, buffer pools — seniors should mention **bounded size**, checkout timeouts, and returning resources in `finally` / `defer`.

## Real-world analogy

A **library of shared laptops** for a lab: limited machines, check out, use, return — you don’t buy a new laptop for every student every hour.

## Example

### Python

```python
from collections import deque
import threading


class Connection:
    def __init__(self, id: int) -> None:
        self.id = id

    def query(self, sql: str) -> str:
        return f"conn-{self.id}: {sql}"


class ConnectionPool:
    def __init__(self, size: int) -> None:
        self._available: deque[Connection] = deque(Connection(i) for i in range(size))
        self._cond = threading.Condition()

    def acquire(self) -> Connection:
        with self._cond:
            while not self._available:
                self._cond.wait()
            return self._available.popleft()

    def release(self, conn: Connection) -> None:
        with self._cond:
            self._available.append(conn)
            self._cond.notify()


pool = ConnectionPool(2)
c = pool.acquire()
print(c.query("SELECT 1"))
pool.release(c)
```

### Go

```go
type Connection struct{ ID int }

func (c Connection) Query(sql string) string {
    return fmt.Sprintf("conn-%d: %s", c.ID, sql)
}

type Pool struct {
    ch chan Connection
}

func NewPool(size int) *Pool {
    p := &Pool{ch: make(chan Connection, size)}
    for i := 0; i < size; i++ {
        p.ch <- Connection{ID: i}
    }
    return p
}

func (p *Pool) Acquire() Connection { return <-p.ch }

func (p *Pool) Release(c Connection) { p.ch <- c }

// usage
pool := NewPool(2)
c := pool.Acquire()
fmt.Println(c.Query("SELECT 1"))
pool.Release(c)
```

A buffered channel is a simple, idiomatic Go pool of tokens/objects.

## When to use

- Objects are expensive to create/destroy (DB, network, native handles).
- You need a hard cap on concurrent resource use.
- Burst traffic would otherwise thrash allocation.

## When not to use / pitfalls

- Cheap objects → pool overhead isn’t worth it.
- **Leaks**: forgetting to release under errors exhausts the pool (always `defer` / `try/finally`).
- Stale/broken connections returned to the pool without health checks.
- Unbounded “pool” that grows forever is not a pool — it’s a leak with extra steps.
- In production, prefer battle-tested pools (`database/sql`, connection poolers) over hand-rolled ones unless the interview asks you to design it.

## Interview trigger phrase

> “Connections are expensive — I’d bound a pool, acquire/release carefully, and time out when none are free.”

## Exercise

Design a pool of **3 workers** that run jobs.

1. Sketch acquire/release with a max of 3 concurrent jobs.
2. What happens if a job panics/throws before release?
3. Name one production library/feature you’d use instead of a custom pool for DB connections.
