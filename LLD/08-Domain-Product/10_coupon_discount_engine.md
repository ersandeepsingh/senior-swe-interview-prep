# Coupon / Discount Engine

> Stackable rules & eligibility — **Chain of Responsibility** + **Strategy**. 🟡

## Scope / requirements

**In:** evaluate coupons against a cart (min amount, % off, flat off, SKU include/exclude), optional stacking with priority / exclusivity, return final discount breakdown.

**Out:** full promotion OMS, personalized ML offers — keep rule engine small.

## Entities

| Entity | Owns |
|--------|------|
| `Cart` / line items | input context |
| `Coupon` / `DiscountRule` | code, predicate, effect |
| `DiscountHandler` | chain node |
| `DiscountResult` | total off + applied codes |
| `EligibilityStrategy` | who can use (first-order, user segment) |

## Invariants

- Discount never exceeds subtotal (unless you explicitly allow negative — don’t).
- Exclusive coupons short-circuit the chain when configured.
- Rules run in defined priority order.
- Same coupon code applied at most once per evaluation.

## Interfaces / patterns — and why

| Seam | Pattern | Why |
|------|---------|-----|
| Pipeline of rules | **Chain of Responsibility** | ordered, stoppable processing |
| Effect math | **Strategy** | percent vs flat vs BOGO |
| Eligibility | Strategy / predicate | first order, geo, SKU |

## End-to-end flow

1. Build chain from active coupons sorted by priority.
2. `evaluate(cart)` walks handlers; each may add discount and pass/`stop`.
3. Return breakdown; checkout applies `subtotal - total_off`.

## Skeletons

### Python

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Cart:
    subtotal: int
    skus: set[str]
    user_id: str


@dataclass
class DiscountResult:
    total_off: int = 0
    applied: list[str] = field(default_factory=list)


class DiscountHandler(ABC):
    def __init__(self):
        self.next: DiscountHandler | None = None

    def set_next(self, h: "DiscountHandler") -> "DiscountHandler":
        self.next = h
        return h

    def handle(self, cart: Cart, acc: DiscountResult) -> DiscountResult:
        stop = self._apply(cart, acc)
        if not stop and self.next:
            return self.next.handle(cart, acc)
        return acc

    @abstractmethod
    def _apply(self, cart: Cart, acc: DiscountResult) -> bool:
        """return True to stop chain"""
        ...


class PercentCoupon(DiscountHandler):
    def __init__(self, code: str, pct: int, min_subtotal: int = 0, exclusive: bool = False):
        super().__init__()
        self.code, self.pct, self.min_subtotal, self.exclusive = code, pct, min_subtotal, exclusive

    def _apply(self, cart: Cart, acc: DiscountResult) -> bool:
        if cart.subtotal < self.min_subtotal:
            return False
        base = cart.subtotal - acc.total_off
        off = base * self.pct // 100
        acc.total_off += off
        acc.applied.append(self.code)
        return self.exclusive


def evaluate(cart: Cart, head: DiscountHandler) -> DiscountResult:
    return head.handle(cart, DiscountResult())
```

### Go

```go
type DiscountHandler interface {
    SetNext(DiscountHandler) DiscountHandler
    Handle(cart Cart, acc *DiscountResult) *DiscountResult
}

type PercentCoupon struct {
    Code        string
    Pct         int
    MinSubtotal int
    Exclusive   bool
    next        DiscountHandler
}

func (p *PercentCoupon) SetNext(h DiscountHandler) DiscountHandler {
    p.next = h
    return h
}

func (p *PercentCoupon) Handle(cart Cart, acc *DiscountResult) *DiscountResult {
    if cart.Subtotal >= p.MinSubtotal {
        base := cart.Subtotal - acc.TotalOff
        acc.TotalOff += base * p.Pct / 100
        acc.Applied = append(acc.Applied, p.Code)
        if p.Exclusive {
            return acc
        }
    }
    if p.next != nil {
        return p.next.Handle(cart, acc)
    }
    return acc
}
```

## Concurrency / consistency

- Evaluation is usually pure/stateless per request — easy to parallelize across checkouts.
- Coupon **redemption count** is the concurrent part: atomic decrement of remaining uses at checkout commit.
- Don’t mark redeemed during preview — only on successful order.

## Tradeoffs / pitfalls

- Unbounded stacking → 100% off bugs; enforce caps and exclusivity.
- Order of percent-then-flat vs flat-then-percent changes money — document priority.
- Mixing eligibility into every effect class — split predicate vs effect if it grows.

## Interview prompts

- Chain vs list of strategies folded in a loop?
- How do exclusive coupons interact with priority?
- Where do you enforce max redemptions?

## Exercise / follow-ups

1. Add `FlatOff` and `BuyXGetY` handlers.
2. Cap total discount at 40% of subtotal after the chain.
3. Redeem coupon with remaining_uses under a lock / CAS.
