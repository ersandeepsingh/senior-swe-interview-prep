# Extensibility Seams

> Where will requirements change? Put a **Strategy / Factory** there before you're asked.

## Plain English

An extensibility seam is a deliberate interface boundary where you expect variants: payment methods, pricing, matching, notifications, eviction policies. You code to that interface so adding a variant is a **new type**, not an edited `if/else`.

Not every method needs a seam — only the axes the problem statement (or interviewer) keeps twisting.

## Senior signal

You name the seam **early** (“pricing will vary → `PricingStrategy`”) and keep the orchestration thin. Juniors hard-code the first algorithm; seniors leave a socket even if only one implementation ships in 45 minutes.

## Examples

### Python

```python
from abc import ABC, abstractmethod


class PricingStrategy(ABC):
    @abstractmethod
    def quote(self, distance_km: float) -> int: ...


class FlatPricing(PricingStrategy):
    def quote(self, distance_km: float) -> int:
        return 5000 + int(distance_km * 1000)


class SurgePricing(PricingStrategy):
    def __init__(self, inner: PricingStrategy, multiplier: float):
        self._inner, self._m = inner, multiplier

    def quote(self, distance_km: float) -> int:
        return int(self._inner.quote(distance_km) * self._m)


class RideService:
    def __init__(self, pricing: PricingStrategy):
        self._pricing = pricing  # seam

    def estimate(self, distance_km: float) -> int:
        return self._pricing.quote(distance_km)
```

### Go

```go
type PricingStrategy interface {
    Quote(distanceKm float64) int
}

type FlatPricing struct{}

func (FlatPricing) Quote(distanceKm float64) int {
    return 5000 + int(distanceKm*1000)
}

type RideService struct {
    Pricing PricingStrategy // seam injected
}

func (s RideService) Estimate(distanceKm float64) int {
    return s.Pricing.Quote(distanceKm)
}
```

## When / how to apply

1. While clarifying: ask “will X vary?” — if yes, name an interface.
2. One concrete impl is enough for the demo; say “second strategy is a new file.”
3. Pair with Factory when selection depends on config/type string.
4. Don’t invent seams for stable domain facts (e.g. “an order has line items”).

## Pitfalls

- Strategy explosion for one-off flags — YAGNI.
- Fat seams that leak unrelated methods (breaks ISP).
- Seams without injection — `new Concrete()` inside the service kills the point.

## Interview trigger

> “I’d put a Strategy at pricing/matching so we can swap algorithms without touching the trip lifecycle.”

## Exercise

Take **Parking Lot pricing** or **Notification channels**: write the interface + two impls + the one-liner you’d say in the interview about why the seam exists.
