# Strategy

> Define a family of **interchangeable algorithms**, encapsulate each one, and make them swappable behind a common interface.

## Plain English

Pricing, sorting, payment, matching — the *steps around* the algorithm stay stable; the *algorithm itself* varies. Pass in a strategy object instead of growing `if/else`.

## Why seniors get asked this

The most common LLD extensibility move. Interviewers say “add another pricing rule / payment method” and expect polymorphism, not a longer switch.

## Real-world analogy

Choosing a **route app mode**: car, bike, walk — same “get me there” request, different route algorithms.

## Example

### Python

```python
from abc import ABC, abstractmethod


class PricingStrategy(ABC):
    @abstractmethod
    def price(self, distance_km: float) -> int: ...


class FlatPricing(PricingStrategy):
    def price(self, distance_km: float) -> int:
        return 100


class DistancePricing(PricingStrategy):
    def price(self, distance_km: float) -> int:
        return int(40 + distance_km * 12)


class Ride:
    def __init__(self, strategy: PricingStrategy) -> None:
        self._strategy = strategy

    def set_strategy(self, strategy: PricingStrategy) -> None:
        self._strategy = strategy

    def quote(self, distance_km: float) -> int:
        return self._strategy.price(distance_km)


ride = Ride(DistancePricing())
print(ride.quote(10))
ride.set_strategy(FlatPricing())
print(ride.quote(10))
```

### Go

```go
type PricingStrategy interface {
    Price(distanceKm float64) int
}

type FlatPricing struct{}
func (FlatPricing) Price(distanceKm float64) int { return 100 }

type DistancePricing struct{}
func (DistancePricing) Price(distanceKm float64) int {
    return int(40 + distanceKm*12)
}

type Ride struct{ Strategy PricingStrategy }

func (r Ride) Quote(distanceKm float64) int {
    return r.Strategy.Price(distanceKm)
}
```

## When to use

- Multiple ways to do the same job; you expect more variants.
- You want OCP at an algorithm seam (payments, discounts, eviction, scheduling).
- Avoiding fat conditionals in a service class.

## When not to use / pitfalls

- Two branches that will never grow → `if` is fine (YAGNI).
- Strategies that need huge shared context may indicate wrong split.
- Don’t confuse with **State** (behavior depends on object lifecycle) or **Template Method** (fixed skeleton, override steps via inheritance).
- Creating a strategy interface for a single implementation is premature.

## Interview trigger phrase

> “Pricing varies independently of the ride flow — I’d inject a PricingStrategy so we can add surge without editing Ride.”

## Exercise

A cache supports **LRU** and **LFU** eviction.

1. Sketch an `EvictionStrategy` and where the cache calls it.
2. What stays in the cache class vs the strategy?
3. When would you keep a simple `if` instead?
