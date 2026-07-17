# Pluggable Persistence

> Repository interface so **in-memory now, DB later** (Dependency Inversion).

## Plain English

Domain services depend on an abstract `Repository` / store port, not on SQLite/Postgres/Redis APIs. In an interview you ship a dict-backed impl; swapping to a DB is a new adapter, not a rewrite of business rules.

## Senior signal

You draw the boundary out loud: “OrderService talks to `OrderRepository`; this is an in-memory map for the demo.” That answers “how would this work in prod?” without coding JDBC.

## Examples

### Python

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Order:
    id: str
    total: int


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None: ...
    @abstractmethod
    def get(self, order_id: str) -> Order | None: ...


class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self._data: dict[str, Order] = {}

    def save(self, order: Order) -> None:
        self._data[order.id] = order

    def get(self, order_id: str) -> Order | None:
        return self._data.get(order_id)


class OrderService:
    def __init__(self, repo: OrderRepository):
        self._repo = repo

    def place(self, order_id: str, total: int) -> Order:
        order = Order(order_id, total)
        self._repo.save(order)
        return order
```

### Go

```go
type Order struct {
    ID    string
    Total int
}

type OrderRepository interface {
    Save(o Order) error
    Get(id string) (Order, bool)
}

type MemoryOrderRepository struct {
    data map[string]Order
}

func (r *MemoryOrderRepository) Save(o Order) error {
    r.data[o.ID] = o
    return nil
}

func (r *MemoryOrderRepository) Get(id string) (Order, bool) {
    o, ok := r.data[id]
    return o, ok
}

type OrderService struct {
    Repo OrderRepository
}
```

## When / how to apply

1. Identify aggregates that need storage (Order, Booking, Wallet ledger).
2. Define narrow repo methods the use-case needs — not a generic `saveAnything`.
3. Construct concrete repo in `main` / wiring; inject into services.
4. Keep transactions at the application service if multiple repos participate.

## Pitfalls

- Repository that leaks SQL types into the domain.
- One mega-repo for the whole app.
- Business rules inside the repository adapter.
- Skipping the interface “to go faster” then rewriting half the service for DB.

## Interview trigger

> “Persistence is behind `OrderRepository` — in-memory for the round, Postgres adapter later without touching domain logic.”

## Exercise

Extract a `SeatRepository` from a booking service that currently uses a raw `dict`. Keep conflict checks in the domain/service, not in the dict wrapper.
