# Singleton

> Ensure a class has **one shared instance** and a global access point to it — safely under concurrency when needed.

## Plain English

Sometimes you really want one config, one metrics registry, one connection manager for the process. Singleton is that “one of these exists” rule, not a license to make every service a global.

## Why seniors get asked this

Interviewers probe whether you reach for Singleton by habit (bad) or for a genuine shared resource (ok), and whether you mention **thread safety** / testability costs.

## Real-world analogy

There’s one **company Wi‑Fi password vault** for the office — everyone reads from the same place; you don’t mint a new vault per laptop.

## Example

### Python

```python
import threading


class AppConfig:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.env = "prod"
        return cls._instance


a, b = AppConfig(), AppConfig()
assert a is b
a.env = "staging"
assert b.env == "staging"
```

### Go

```go
package config

import "sync"

type AppConfig struct {
    Env string
}

var (
    instance *AppConfig
    once     sync.Once
)

func Get() *AppConfig {
    once.Do(func() {
        instance = &AppConfig{Env: "prod"}
    })
    return instance
}
```

`sync.Once` is the idiomatic Go singleton — prefer it over hand-rolled double-checked locking.

## When to use

- Truly process-wide shared state: config loaded once, metrics registry, logger sink.
- You need a single coordination point and alternatives (DI of one instance) feel heavier than the benefit.

## When not to use / pitfalls

- **Hidden global state** makes unit tests order-dependent and flaky.
- Overused for services that should be injected (`OrderService` is not a Singleton).
- Lazy init without locks → races; eager init or `sync.Once` / double-checked locking if you must.
- Prefer: create once in `main` and pass it down (DI) — same “one instance,” better test seams.

## Interview trigger phrase

> “If we truly need one shared instance, I’d use a safe lazy init — but I’d rather construct it in main and inject it so tests stay clean.”

## Exercise

Design a **DB connection manager** that the whole app shares.

1. Sketch Singleton vs “create in main + inject.”
2. Say which is easier to fake in tests and why.
3. Name one concurrency hazard if two threads both call `getInstance()` naively.
