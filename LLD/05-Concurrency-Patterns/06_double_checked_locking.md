# Double-Checked Locking

> **Lazy initialization** with minimal locking: check if initialized (no lock), then lock and **check again** before creating the singleton.

## Plain English

You want to create an expensive object only once, but you don’t want every reader to pay for a lock. First peek without the lock; only if it might be missing, take the lock and verify again before creating.

## Simple analogy

Conference room setup: glance in — if chairs are ready, walk in. If empty, one person gets the key, double-checks inside the locked room, then sets up once.

## Why seniors get asked this

Thread-safe singletons, lazy config clients, connection manager init — interviewers test whether you know the memory-model pitfalls and language idioms (`sync.Once` in Go).

## Good: safe lazy init

### Python

```python
import threading
from typing import Optional


class DatabaseClient:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        print(f"connected to {dsn}")


class DatabaseHolder:
    _instance: Optional[DatabaseClient] = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> DatabaseClient:
        if cls._instance is None:  # first check (no lock)
            with cls._lock:
                if cls._instance is None:  # second check (under lock)
                    cls._instance = DatabaseClient("postgres://localhost/app")
        return cls._instance
```

In Python, assignment to `_instance` under `Lock` is the safe pattern for interviews. The GIL does **not** excuse skipping the lock for lazy init of composite objects — another thread can observe a partially constructed object without proper publication.

**Simpler alternative:** module-level singleton or `@lru_cache` on a factory — often clearer in Python.

### Go

Prefer **`sync.Once`** — correct, readable, handles memory barriers:

```go
package main

import (
    "fmt"
    "sync"
)

type DatabaseClient struct {
    DSN string
}

var (
    dbOnce sync.Once
    dbInst *DatabaseClient
)

func GetDatabase() *DatabaseClient {
    dbOnce.Do(func() {
        dbInst = &DatabaseClient{DSN: "postgres://localhost/app"}
        fmt.Println("connected to", dbInst.DSN)
    })
    return dbInst
}

func main() {
    var wg sync.WaitGroup
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            _ = GetDatabase()
        }()
    }
    wg.Wait()
}
```

Manual double-checked locking in Go without `Once` requires `atomic` loads/stores and is easy to get wrong — say that in interviews.

## Concurrency safety

| Concern | What to watch |
|---------|----------------|
| **Race** | Two threads both see `nil`, both create — broken singleton without second check under lock. |
| **Partial construction** | Without proper publication, readers may see a half-built object (more acute in languages with reordering; `sync.Once` fixes this in Go). |
| **Deadlock** | Rare here unless init callback re-enters `get_instance()` on the same lock. |

**Python GIL:** still use `threading.Lock` for lazy init of non-trivial objects; don’t rely on “check outside lock” alone for correctness.

## When to use / not use

**Use:** expensive one-time init; rarely used shared clients; true singleton in a process.

**Don’t use:** when DI/container creates one instance at startup (simpler); distributed systems needing cluster-wide singleton (use leader election / external service); when `sync.Once` or a module singleton exists — use the idiomatic tool.

## Pitfalls

- Broken DCL in Java/C++ without `volatile` / atomics — classic interview trap.
- Implementing DCL by hand in Go instead of `sync.Once`.
- Singleton hiding testability — inject interfaces instead when designing for tests.
- Init failure cached forever in some `Once` usages — plan retry at a higher layer if needed.

## Interview trigger phrase

> “Lazy singleton with **double-checked locking** under a mutex — in Go I’d just use **`sync.Once`** so publication is safe.”

## Exercise

A **Snowflake ID generator** must initialize machine ID from config once at first use.

1. Why is “if not initialized: initialize” unsafe without a lock?
2. Python: `Lock` vs module-level init at import — trade-offs?
3. Go: write the `sync.Once` wrapper in one sentence.
