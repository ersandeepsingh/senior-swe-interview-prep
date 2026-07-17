# Observer

> Define a **one-to-many** dependency so when one object changes state, all dependents are notified automatically.

## Plain English

Subject holds a list of subscribers. On change, it notifies them. Publishers don’t hard-code who listens — stock tickers, UI events, domain events (“order placed”).

## Why seniors get asked this

Notifications, analytics, websocket fan-out — decoupling “what happened” from “who cares.” Seniors mention sync vs async and avoiding notification storms.

## Real-world analogy

A **newsletter**: you subscribe; when an issue publishes, all subscribers get it. The author doesn’t email each person manually by name in code.

## Example

### Python

```python
from abc import ABC, abstractmethod


class Observer(ABC):
    @abstractmethod
    def update(self, symbol: str, price: float) -> None: ...


class Display(Observer):
    def __init__(self, name: str) -> None:
        self.name = name

    def update(self, symbol: str, price: float) -> None:
        print(f"[{self.name}] {symbol} = {price}")


class StockFeed:
    def __init__(self) -> None:
        self._observers: list[Observer] = []
        self._prices: dict[str, float] = {}

    def subscribe(self, obs: Observer) -> None:
        self._observers.append(obs)

    def set_price(self, symbol: str, price: float) -> None:
        self._prices[symbol] = price
        for obs in self._observers:
            obs.update(symbol, price)


feed = StockFeed()
feed.subscribe(Display("A"))
feed.subscribe(Display("B"))
feed.set_price("INFY", 1500.0)
```

### Go

```go
type Observer interface {
    Update(symbol string, price float64)
}

type Display struct{ Name string }
func (d Display) Update(symbol string, price float64) {
    fmt.Printf("[%s] %s = %.2f\n", d.Name, symbol, price)
}

type StockFeed struct {
    observers []Observer
}

func (s *StockFeed) Subscribe(o Observer) {
    s.observers = append(s.observers, o)
}

func (s *StockFeed) SetPrice(symbol string, price float64) {
    for _, o := range s.observers {
        o.Update(symbol, price)
    }
}
```

## When to use

- Multiple independent reactions to the same event.
- You want open-ended listeners without editing the subject.
- Domain events: order placed → email, metrics, inventory.

## When not to use / pitfalls

- One caller that always needs one reaction → just call it.
- Unbounded sync notify → slow observers block the subject; mention queues for heavy work.
- Forgotten unsubscribe → leaks (especially UI).
- Update order dependencies between observers → fragile; don’t rely on order.
- Not a replacement for a full message broker in distributed systems — say the scope.

## Interview trigger phrase

> “OrderService shouldn’t know about email and metrics — I’d publish an event and let observers react.”

## Exercise

On `Order.placed`, update inventory and send email.

1. Sketch subject + two observers.
2. What happens if email is slow? What would you change?
3. Observer vs Mediator — one sentence each.
