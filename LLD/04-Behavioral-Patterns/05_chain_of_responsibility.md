# Chain of Responsibility

> Pass a request along a **chain of handlers**; each either handles it or forwards it to the next.

## Plain English

Middleware, approval flows, ATM cash dispensers: try handler A, then B, then C. No single god `if` knows every case. Ordering matters.

## Why seniors get asked this

Logging pipelines, HTTP middleware, coupon/discount stacks, ATM. Seniors discuss short-circuiting and who decides “handled.”

## Real-world analogy

**Customer support tiers**: L1 tries first; if stuck, escalate to L2, then L3 — same ticket travels the chain.

## Example

### Python

```python
from abc import ABC, abstractmethod
from typing import Optional


class Handler(ABC):
    def __init__(self) -> None:
        self._next: Optional["Handler"] = None

    def set_next(self, handler: "Handler") -> "Handler":
        self._next = handler
        return handler

    def handle(self, amount: int) -> None:
        if self._can_handle(amount):
            self._do_handle(amount)
        elif self._next:
            self._next.handle(amount)
        else:
            print(f"can't dispense {amount}")

    @abstractmethod
    def _can_handle(self, amount: int) -> bool: ...

    @abstractmethod
    def _do_handle(self, amount: int) -> None: ...


class NoteHandler(Handler):
    def __init__(self, note: int) -> None:
        super().__init__()
        self.note = note

    def _can_handle(self, amount: int) -> bool:
        return amount >= self.note

    def _do_handle(self, amount: int) -> None:
        n, rem = divmod(amount, self.note)
        print(f"{n} x {self.note}")
        if rem and self._next:
            self._next.handle(rem)
        elif rem:
            print(f"leftover {rem}")


h200 = NoteHandler(200)
h100 = NoteHandler(100)
h50 = NoteHandler(50)
h200.set_next(h100).set_next(h50)
h200.handle(350)  # 1x200, 1x100, 1x50
```

### Go

```go
type Handler interface {
    SetNext(Handler) Handler
    Handle(amount int)
}

type NoteHandler struct {
    note int
    next Handler
}

func (h *NoteHandler) SetNext(n Handler) Handler { h.next = n; return n }

func (h *NoteHandler) Handle(amount int) {
    if amount >= h.note {
        n, rem := amount/h.note, amount%h.note
        fmt.Printf("%d x %d\n", n, h.note)
        if rem > 0 && h.next != nil {
            h.next.Handle(rem)
        } else if rem > 0 {
            fmt.Println("leftover", rem)
        }
        return
    }
    if h.next != nil {
        h.next.Handle(amount)
    }
}
```

## When to use

- Multiple potential handlers; runtime decides who processes.
- Pipelines: auth → rate-limit → validate → business logic.
- Avoid coupling sender to a concrete receiver.

## When not to use / pitfalls

- One clear handler → just call it.
- Guaranteeing *someone* handles the request — need a terminal default / error.
- Debugging long chains is harder; keep handlers small and ordered explicitly.
- Don’t confuse with **Decorator** (always wraps and usually adds; chain may skip).
- Performance: very long chains on hot paths — measure.

## Interview trigger phrase

> “Approvals go manager → director → finance — Chain of Responsibility, each stage can approve or forward.”

## Exercise

HTTP middleware: authenticate, then rate-limit, then handle request.

1. Sketch three handlers and the link order.
2. Where do you short-circuit on 401?
3. How is this different from Decorator?
