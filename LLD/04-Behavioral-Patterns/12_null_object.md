# Null Object

> Provide a **do-nothing (neutral) implementation** of an interface so clients avoid special-case `null` checks.

## Plain English

Instead of `logger is None` everywhere, inject a `NullLogger` whose methods are no-ops. Same idea for optional discounts, optional notifiers, missing handlers.

## Why seniors get asked this

Cleaner call sites, fewer NPEs/panics. Seniors also know when null/optional is *more* honest (absence that must be handled differently).

## Real-world analogy

A **mute button**: the speaker interface is still there; mute is a speaker that produces silence — you don’t remove the speaker from the room.

## Example

### Python

```python
from abc import ABC, abstractmethod


class Logger(ABC):
    @abstractmethod
    def info(self, msg: str) -> None: ...


class ConsoleLogger(Logger):
    def info(self, msg: str) -> None:
        print(f"INFO {msg}")


class NullLogger(Logger):
    def info(self, msg: str) -> None:
        return  # deliberately nothing


class OrderService:
    def __init__(self, log: Logger) -> None:
        self._log = log

    def place(self) -> None:
        self._log.info("order placed")
        # business logic...


OrderService(ConsoleLogger()).place()
OrderService(NullLogger()).place()  # no null checks
```

### Go

```go
type Logger interface {
    Info(msg string)
}

type ConsoleLogger struct{}
func (ConsoleLogger) Info(msg string) { fmt.Println("INFO", msg) }

type NullLogger struct{}
func (NullLogger) Info(msg string) {} // no-op

type OrderService struct{ Log Logger }

func (s OrderService) Place() {
    s.Log.Info("order placed")
}

// OrderService{Log: NullLogger{}}.Place()
```

In Go, a `nil` interface is *not* a Null Object — calling methods on a nil concrete pointer can still panic. Prefer an explicit `NullLogger{}`.

## When to use

- Optional behavior with a safe default: logging, metrics, listeners, no-op cache.
- You want polymorphic “always call it” without branching.
- Tests that don’t care about a collaborator.

## When not to use / pitfalls

- Absence is meaningful (user not found) → return `Optional` / `(T, error)`, don’t fake a user.
- Null objects that hide errors (“always succeed”) can mask bugs.
- Not a substitute for proper error handling.
- Don’t confuse with Optional/Maybe types — Null Object is a *real instance* with neutral behavior.

## Interview trigger phrase

> “If logging is optional, I’d inject a NullLogger so OrderService never branches on nil.”

## Exercise

`DiscountPolicy.apply(total)` is optional at checkout.

1. Sketch `NoDiscount` as a Null Object.
2. When is `Optional[DiscountPolicy]` clearer?
3. In Go, why is `var log Logger` (nil interface) risky?
