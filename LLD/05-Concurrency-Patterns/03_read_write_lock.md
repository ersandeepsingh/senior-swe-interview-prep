# Read-Write Lock

> Allow **many concurrent readers** OR **one writer** — optimize for read-heavy shared data (caches, config snapshots).

## Plain English

A regular mutex: one person in the room at a time. A read-write lock: many people can **read** the whiteboard together, but **writing** requires everyone else to leave first.

## Simple analogy

Library reading room: many patrons browse catalogs; only one librarian updates the catalog at a time.

## Why seniors get asked this

In-memory caches, config reload, seat maps — interviewers probe whether you reach for a mutex when reads dominate and whether you prevent writer starvation.

## Good: many readers, exclusive writer

### Python

Python’s stdlib has no `RWLock`. A minimal correct pattern for interviews:

```python
import threading
from typing import Any


class ReadWriteLock:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._write_lock = threading.Lock()
        self._readers = 0

    def acquire_read(self) -> None:
        with self._lock:
            self._readers += 1
            if self._readers == 1:
                self._write_lock.acquire()

    def release_read(self) -> None:
        with self._lock:
            self._readers -= 1
            if self._readers == 0:
                self._write_lock.release()

    def acquire_write(self) -> None:
        self._write_lock.acquire()

    def release_write(self) -> None:
        self._write_lock.release()


class ConfigCache:
    def __init__(self) -> None:
        self._rw = ReadWriteLock()
        self._data: dict[str, Any] = {}

    def get(self, key: str) -> Any:
        self._rw.acquire_read()
        try:
            return self._data.get(key)
        finally:
            self._rw.release_read()

    def set(self, key: str, value: Any) -> None:
        self._rw.acquire_write()
        try:
            self._data[key] = value
        finally:
            self._rw.release_write()
```

Prefer `contextlib` wrappers in production; for interviews, show you understand reader counting + writer exclusion.

### Go

```go
package main

import (
    "fmt"
    "sync"
)

type ConfigCache struct {
    mu   sync.RWMutex
    data map[string]string
}

func (c *ConfigCache) Get(key string) (string, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    v, ok := c.data[key]
    return v, ok
}

func (c *ConfigCache) Set(key, value string) {
    c.mu.Lock() // exclusive write
    defer c.mu.Unlock()
    c.data[key] = value
}

func main() {
    cache := &ConfigCache{data: map[string]string{"region": "ap-south-1"}}
    fmt.Println(cache.Get("region"))
    cache.Set("region", "us-east-1")
}
```

Use `*ConfigCache` (pointer receiver) so the mutex inside the struct is not copied.

## Concurrency safety

| Concern | What to watch |
|---------|----------------|
| **Race** | Readers must not mutate shared data. Returning a mutable map/slice without a copy lets callers race with writers. |
| **Deadlock** | Upgrading read lock → write lock in the same thread (lock re-entrancy rules vary) — avoid nested lock dance. |
| **Starvation** | Continuous readers can starve writers — mention fair policies or occasional write priority if asked. |

**Python GIL:** does not replace an RWLock for correctness; two threads can still interleave read-modify-write on shared dicts.

## When to use / not use

**Use:** read-heavy, write-rare caches; config loaded occasionally; metrics snapshots.

**Don’t use:** write-heavy data (mutex is simpler and often faster); critical sections that are tiny (lock overhead dominates); when `atomic.Value` / immutable swap is enough (see immutability pattern).

## Pitfalls

- Returning internal mutable state to readers.
- Copying a Go struct that embeds `sync.RWMutex`.
- RWLock when a single `Mutex` + short critical section would do (premature optimization).
- Read lock held too long (I/O inside read lock blocks writers).

## Interview trigger phrase

> “Reads dominate here — I’d use a **read-write lock** so concurrent lookups don’t block each other, with exclusive writes on refresh.”

## Exercise

In-memory **product catalog**: 10k reads/sec, admin updates a SKU every few minutes.

1. RWLock vs plain mutex — defend your pick.
2. Should `get_product` return the stored dict or a copy?
3. How would you reload the whole catalog atomically for readers?
