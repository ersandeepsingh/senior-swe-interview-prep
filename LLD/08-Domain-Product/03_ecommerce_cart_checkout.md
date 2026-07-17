# E-commerce Cart & Checkout

> Cart, discounts, payment, inventory — **Strategy** (discount / payment) + **State** (order). 🔴

## Scope / requirements

**In:** add/update/remove cart lines, apply coupon, checkout → reserve inventory → pay → create order (`PENDING_PAYMENT → PAID → FULFILLING → SHIPPED` / `CANCELLED`).

**Out:** full catalog search, warehouse routing depth, tax engine beyond a stub, PCI-level payments.

## Entities

| Entity | Owns |
|--------|------|
| `Cart`, `CartItem` | mutable session lines |
| `Product` / SKU | price, stock pointer |
| `Coupon` / `DiscountStrategy` | eligibility + amount |
| `PaymentMethod` (strategy) | charge / refund stub |
| `Order` | immutable snapshot of cart at checkout |
| `InventoryService` | reserve / commit / release |

## Invariants

- Cart quantities > 0; price snapshot at checkout (or live — declare which).
- Checkout fails if any line lacks reservation.
- Payment success required before `PAID`; failed pay releases reservations.
- Order lines are a **copy** of cart — cart mutations after checkout don’t alter the order.

## Interfaces / patterns — and why

| Seam | Pattern | Why |
|------|---------|-----|
| Discounts | **Strategy** / Chain | % off, flat, BOGO — stackable later |
| Payment | **Strategy** | Card / UPI / COD |
| Order lifecycle | **State** | Refund/cancel rules by status |
| Inventory | Repository + reserve API | Consistency boundary |

## End-to-end flow

1. User builds cart → `apply_coupon` via discount strategy → preview total.
2. `checkout`: validate → `inventory.reserve(lines)` → create `Order(PENDING_PAYMENT)`.
3. `payment.charge(order)` → on success `PAID` + `inventory.commit`; on failure release + `CANCELLED`.

## Skeletons

### Python

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class CartItem:
    sku: str
    qty: int
    unit_price: int  # paise


@dataclass
class Cart:
    items: dict[str, CartItem] = field(default_factory=dict)

    def add(self, sku: str, qty: int, unit_price: int) -> None:
        if sku in self.items:
            self.items[sku].qty += qty
        else:
            self.items[sku] = CartItem(sku, qty, unit_price)

    def subtotal(self) -> int:
        return sum(i.qty * i.unit_price for i in self.items.values())


class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, subtotal: int, cart: Cart) -> int:  # returns discount amount
        ...


class PercentOff(DiscountStrategy):
    def __init__(self, pct: int): self.pct = pct
    def apply(self, subtotal: int, cart: Cart) -> int:
        return subtotal * self.pct // 100


class PaymentMethod(ABC):
    @abstractmethod
    def charge(self, order_id: str, amount: int) -> bool: ...


class Inventory:
    def __init__(self): self.stock: dict[str, int] = {}
    def reserve(self, sku: str, qty: int) -> bool:
        if self.stock.get(sku, 0) < qty:
            return False
        self.stock[sku] -= qty
        return True
    def release(self, sku: str, qty: int) -> None:
        self.stock[sku] = self.stock.get(sku, 0) + qty


class CheckoutService:
    def __init__(self, inventory: Inventory, payment: PaymentMethod):
        self._inv, self._pay = inventory, payment

    def checkout(self, cart: Cart, discount: DiscountStrategy | None) -> str:
        sub = cart.subtotal()
        off = discount.apply(sub, cart) if discount else 0
        total = sub - off
        reserved = []
        for item in cart.items.values():
            if not self._inv.reserve(item.sku, item.qty):
                for s, q in reserved:
                    self._inv.release(s, q)
                raise RuntimeError("insufficient stock")
            reserved.append((item.sku, item.qty))
        order_id = "ord-1"
        if not self._pay.charge(order_id, total):
            for s, q in reserved:
                self._inv.release(s, q)
            raise RuntimeError("payment failed")
        return order_id
```

### Go

```go
type DiscountStrategy interface {
    Apply(subtotal int, cart *Cart) int
}

type PaymentMethod interface {
    Charge(orderID string, amount int) bool
}

type Inventory interface {
    Reserve(sku string, qty int) bool
    Release(sku string, qty int)
}

type CheckoutService struct {
    Inv Inventory
    Pay PaymentMethod
}

func (s *CheckoutService) Checkout(cart *Cart, d DiscountStrategy) (string, error) {
    sub := cart.Subtotal()
    off := 0
    if d != nil {
        off = d.Apply(sub, cart)
    }
    total := sub - off
    var reserved [][2]any
    for _, it := range cart.Items {
        if !s.Inv.Reserve(it.SKU, it.Qty) {
            for _, r := range reserved {
                s.Inv.Release(r[0].(string), r[1].(int))
            }
            return "", fmt.Errorf("insufficient stock")
        }
        reserved = append(reserved, [2]any{it.SKU, it.Qty})
    }
    orderID := "ord-1"
    if !s.Pay.Charge(orderID, total) {
        for _, r := range reserved {
            s.Inv.Release(r[0].(string), r[1].(int))
        }
        return "", fmt.Errorf("payment failed")
    }
    return orderID, nil
}
```

## Concurrency / consistency

- Two checkouts on last unit: **reserve** must be atomic (DB row lock, Redis `DECR` with check, or optimistic version).
- Prefer **reserve → pay → commit**; never decrement only after pay without holding a hold TTL.
- Idempotency key on checkout/payment to avoid double charge.

## Tradeoffs / pitfalls

- Mutating catalog price into the order without snapshotting.
- Applying discounts after payment authorization amount was locked.
- Soft stock checks in UI only — always re-check at checkout.

## Interview prompts

- Reserve vs commit vs release — when each?
- How do stackable coupons change the design? (Chain / pipeline)
- COD: skip charge but still reserve?

## Exercise / follow-ups

1. Add order `State` with `cancel()` releasing inventory only if not shipped.
2. Compose two discounts with a max-cap rule.
3. Add idempotency key to `checkout`.
