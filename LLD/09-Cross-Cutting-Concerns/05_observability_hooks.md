# Observability Hooks

> Events/observers for logging, metrics, notifications **without coupling**.

## Plain English

When something important happens (order paid, trip completed, stock low), emit a domain event or notify observers. Logging, metrics, and push notifications subscribe at the edges. The core flow doesn’t call `logger.info` and `metrics.inc` and `email.send` inline everywhere.

## Senior signal

You mention Observer/events as a **decoupling** tool, not as “I’ll add log statements.” You keep callbacks thin and avoid doing heavy work under locks.

## Examples

### Python

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class OrderPaid:
    order_id: str
    amount: int


class OrderEventHandler(ABC):
    @abstractmethod
    def on_paid(self, event: OrderPaid) -> None: ...


class MetricsHandler(OrderEventHandler):
    def on_paid(self, event: OrderPaid) -> None:
        print(f"metric order_paid_total amount={event.amount}")


class AuditLogHandler(OrderEventHandler):
    def on_paid(self, event: OrderPaid) -> None:
        print(f"audit order={event.order_id} paid")


class OrderService:
    def __init__(self, handlers: list[OrderEventHandler]):
        self._handlers = handlers

    def mark_paid(self, order_id: str, amount: int) -> None:
        # ... persist state first ...
        event = OrderPaid(order_id, amount)
        for h in self._handlers:
            h.on_paid(event)
```

### Go

```go
type OrderPaid struct {
    OrderID string
    Amount  int
}

type OrderEventHandler interface {
    OnPaid(e OrderPaid)
}

type OrderService struct {
    Handlers []OrderEventHandler
}

func (s *OrderService) MarkPaid(orderID string, amount int) {
    // persist first
    e := OrderPaid{orderID, amount}
    for _, h := range s.Handlers {
        h.OnPaid(e)
    }
}
```

## When / how to apply

1. List lifecycle moments worth observing (created, paid, failed, low stock).
2. Define a small event type or observer method per moment.
3. Register logging/metrics/notify impls in wiring.
4. In real systems: prefer outbox/queue if observers must not lose events after commit.

## Pitfalls

- Business logic inside observers (hard to test, hidden flow).
- Notifying before durable commit → phantom events on rollback.
- Synchronous email under a DB lock.
- God `EventBus` with stringly-typed topics and no schema — fine to mention; keep interview code typed.

## Interview trigger

> “Status changes publish domain events — notifications and metrics subscribe so OrderService doesn’t hard-depend on SMTP or Prometheus.”

## Exercise

Add observers to **food delivery** status transitions: one metrics counter, one user notifier. Show they can be disabled in unit tests by passing an empty list.
