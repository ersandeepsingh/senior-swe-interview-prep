# Inventory / Warehouse

> Stock levels, reservations, replenishment — **Observer** (low-stock alerts) + **repository**. 🟡

## Scope / requirements

**In:** SKU stock per warehouse (or single warehouse), `receive`, `reserve`, `commit`, `release`, low-stock threshold events.

**Out:** multi-hop WMS, pick-path optimization, supplier ERP — mention only.

## Entities

| Entity | Owns |
|--------|------|
| `SKU` / `ProductId` | identity |
| `Warehouse` | location identity |
| `StockLevel` | on_hand, reserved, available = on_hand − reserved |
| `Reservation` | id, sku, qty, ttl/expires |
| `StockRepository` | persistence port |
| `StockObserver` | low-stock / replenishment hooks |

## Invariants

- `available >= 0`; never reserve more than available.
- `on_hand >= reserved` always.
- `commit` converts reserved → shipped (decrement both on_hand and reserved).
- `release` returns reserved to available.

## Interfaces / patterns — and why

| Seam | Pattern | Why |
|------|---------|-----|
| Persistence | **Repository** (DIP) | In-memory now, DB later |
| Low stock | **Observer** | Email / replenishment job without coupling |
| Reservation policy | Strategy (optional) | FIFO lots / expiry later |

## End-to-end flow

1. `receive(sku, qty)` → increase `on_hand`; notify if crossed above threshold (optional).
2. Order path: `reserve(sku, qty)` → create reservation; if `available < threshold` notify observers.
3. Ship: `commit(reservation_id)`; cancel: `release(reservation_id)`.

## Skeletons

### Python

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class StockLevel:
    on_hand: int = 0
    reserved: int = 0

    @property
    def available(self) -> int:
        return self.on_hand - self.reserved


class StockObserver(ABC):
    @abstractmethod
    def on_low_stock(self, sku: str, available: int) -> None: ...


class InventoryService:
    def __init__(self, threshold: int = 5):
        self._stock: dict[str, StockLevel] = {}
        self._observers: list[StockObserver] = []
        self.threshold = threshold

    def receive(self, sku: str, qty: int) -> None:
        s = self._stock.setdefault(sku, StockLevel())
        s.on_hand += qty

    def reserve(self, sku: str, qty: int) -> bool:
        s = self._stock.setdefault(sku, StockLevel())
        if s.available < qty:
            return False
        s.reserved += qty
        if s.available < self.threshold:
            for o in self._observers:
                o.on_low_stock(sku, s.available)
        return True

    def commit(self, sku: str, qty: int) -> None:
        s = self._stock[sku]
        if s.reserved < qty:
            raise ValueError("nothing to commit")
        s.reserved -= qty
        s.on_hand -= qty

    def release(self, sku: str, qty: int) -> None:
        s = self._stock[sku]
        s.reserved = max(0, s.reserved - qty)
```

### Go

```go
type StockLevel struct {
    OnHand, Reserved int
}

func (s StockLevel) Available() int { return s.OnHand - s.Reserved }

type StockObserver interface {
    OnLowStock(sku string, available int)
}

type InventoryService struct {
    stock     map[string]*StockLevel
    observers []StockObserver
    threshold int
}

func (inv *InventoryService) Reserve(sku string, qty int) bool {
    s := inv.stock[sku]
    if s == nil {
        s = &StockLevel{}
        inv.stock[sku] = s
    }
    if s.Available() < qty {
        return false
    }
    s.Reserved += qty
    if s.Available() < inv.threshold {
        for _, o := range inv.observers {
            o.OnLowStock(sku, s.Available())
        }
    }
    return true
}

func (inv *InventoryService) Commit(sku string, qty int) error {
    s := inv.stock[sku]
    if s.Reserved < qty {
        return fmt.Errorf("nothing to commit")
    }
    s.Reserved -= qty
    s.OnHand -= qty
    return nil
}
```

## Concurrency / consistency

- All mutations on a SKU need a **per-SKU lock** or atomic DB update (`UPDATE … WHERE available >= qty`).
- Reservations should **expire** (TTL sweeper) or checkout holds forever and leaks stock.
- Multi-warehouse: reserve locally then, or two-phase across warehouses — say you’d shard by SKU.

## Tradeoffs / pitfalls

- Storing only `available` and losing the reserved/on_hand split — hard to debug oversell.
- Notifying observers inside the lock for too long — keep callbacks thin or async.
- Negative stock from `commit` without checking reserved.

## Interview prompts

- Why separate reserve and commit?
- How do you expire abandoned carts’ holds?
- Low-stock: sync observer vs event queue?

## Exercise / follow-ups

1. Add `Reservation` ids and TTL expiry job.
2. Multi-warehouse `reserve` that prefers nearest warehouse (Strategy).
3. Unit-test oversell: two concurrent reserves of last unit (describe expected).
