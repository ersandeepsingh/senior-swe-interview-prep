# Food Delivery (Swiggy / Zomato)

> Restaurants, orders, and delivery assignment — **Strategy** (pricing / assignment) + **Observer** (status fan-out). 🔴

## Scope / requirements

**In:** browse restaurants/menus, place order, track status (`PLACED → ACCEPTED → PREPARING → READY → OUT_FOR_DELIVERY → DELIVERED`), assign a delivery partner, basic pricing (item + delivery fee).

**Out (say so):** real maps/ETA ML, payment gateway depth, multi-city catalog, surge math beyond a pluggable strategy.

## Entities

| Entity | Owns |
|--------|------|
| `Customer`, `Restaurant`, `MenuItem` | identity + catalog |
| `Order`, `OrderItem` | line items, status, totals |
| `DeliveryPartner` | availability, location stub |
| `AssignmentStrategy` | which partner gets the order |
| `PricingStrategy` | fees / surge |
| `OrderEventPublisher` | notify customer / restaurant / partner |

## Invariants

- Order total = sum(line items) + fees − discounts; never mutate after `DELIVERED`.
- Only `READY` (or agreed state) orders are assignable.
- A partner is assigned to at most one active delivery (or capacity N if you model capacity).
- Status transitions are allowed only via an explicit state machine — no arbitrary jumps.

## Interfaces / patterns — and why

| Seam | Pattern | Why |
|------|---------|-----|
| Partner selection | **Strategy** | Nearest / least-loaded / zone — changes without touching `OrderService` |
| Fees / surge | **Strategy** | Same reason |
| Status updates | **Observer** / events | Customer app, restaurant tablet, partner app stay decoupled |
| Order lifecycle | **State** (light) | Illegal transitions fail fast |

## End-to-end flow

1. Customer places order → validate restaurant open + items → create `Order(PLACED)`.
2. Restaurant accepts → `ACCEPTED` → `PREPARING` → `READY`.
3. Assigner runs `AssignmentStrategy.pick(ready_order, available_partners)` → bind partner → `OUT_FOR_DELIVERY`.
4. Partner completes → `DELIVERED`; observers notified at each step.

## Skeletons

### Python

```python
from abc import ABC, abstractmethod
from enum import Enum, auto


class OrderStatus(Enum):
    PLACED = auto()
    ACCEPTED = auto()
    PREPARING = auto()
    READY = auto()
    OUT_FOR_DELIVERY = auto()
    DELIVERED = auto()


ALLOWED = {
    OrderStatus.PLACED: {OrderStatus.ACCEPTED},
    OrderStatus.ACCEPTED: {OrderStatus.PREPARING},
    OrderStatus.PREPARING: {OrderStatus.READY},
    OrderStatus.READY: {OrderStatus.OUT_FOR_DELIVERY},
    OrderStatus.OUT_FOR_DELIVERY: {OrderStatus.DELIVERED},
}


class AssignmentStrategy(ABC):
    @abstractmethod
    def pick(self, order, partners: list) -> object | None: ...


class NearestPartner(AssignmentStrategy):
    def pick(self, order, partners: list):
        available = [p for p in partners if p.available]
        return min(available, key=lambda p: p.distance_to(order.restaurant), default=None)


class OrderObserver(ABC):
    @abstractmethod
    def on_status(self, order_id: str, status: OrderStatus) -> None: ...


class Order:
    def __init__(self, id: str, restaurant_id: str):
        self.id, self.restaurant_id = id, restaurant_id
        self.status = OrderStatus.PLACED
        self.partner_id: str | None = None

    def transition(self, to: OrderStatus) -> None:
        if to not in ALLOWED.get(self.status, set()):
            raise ValueError(f"{self.status} → {to} illegal")
        self.status = to


class DeliveryService:
    def __init__(self, assigner: AssignmentStrategy, observers: list[OrderObserver]):
        self._assigner, self._observers = assigner, observers

    def assign(self, order: Order, partners: list) -> None:
        if order.status != OrderStatus.READY:
            raise ValueError("not ready")
        partner = self._assigner.pick(order, partners)
        if partner is None:
            raise RuntimeError("no partner")
        order.partner_id = partner.id
        order.transition(OrderStatus.OUT_FOR_DELIVERY)
        for o in self._observers:
            o.on_status(order.id, order.status)
```

### Go

```go
type OrderStatus int

const (
    Placed OrderStatus = iota
    Accepted
    Preparing
    Ready
    OutForDelivery
    Delivered
)

type AssignmentStrategy interface {
    Pick(order *Order, partners []*Partner) *Partner
}

type OrderObserver interface {
    OnStatus(orderID string, status OrderStatus)
}

type Order struct {
    ID, RestaurantID string
    Status           OrderStatus
    PartnerID        string
}

func (o *Order) Transition(to OrderStatus) error {
    // check ALLOWED map; return error if illegal
    o.Status = to
    return nil
}

type DeliveryService struct {
    Assigner  AssignmentStrategy
    Observers []OrderObserver
}

func (s *DeliveryService) Assign(order *Order, partners []*Partner) error {
    if order.Status != Ready {
        return fmt.Errorf("not ready")
    }
    p := s.Assigner.Pick(order, partners)
    if p == nil {
        return fmt.Errorf("no partner")
    }
    order.PartnerID = p.ID
    _ = order.Transition(OutForDelivery)
    for _, obs := range s.Observers {
        obs.OnStatus(order.ID, order.Status)
    }
    return nil
}
```

## Concurrency / consistency

- **Assignment race:** two threads assign the same partner — use `compare-and-set` on `partner.available` or a lock per partner / shard.
- **Status fan-out:** publish after durable status write (or transactional outbox in real systems).
- Prefer **idempotent** `assign(order_id)` — second call no-ops if already assigned.

## Tradeoffs / pitfalls

- Don’t build a full GIS stack; stub distance.
- God `OrderManager` that prices, assigns, and notifies — split seams early.
- Over-modeling every restaurant config before one happy path compiles.

## Interview prompts

- How do you swap “nearest” for “batch by zone” without rewriting order flow?
- What happens if the partner goes offline mid-delivery?
- Where would you put surge pricing?

## Exercise / follow-ups

1. Add `Cancelled` with rules: cancel only before `OUT_FOR_DELIVERY`; free the partner.
2. Implement a second `AssignmentStrategy` (least active deliveries) and inject it.
3. Say out loud the race if two `READY` orders claim one partner.
