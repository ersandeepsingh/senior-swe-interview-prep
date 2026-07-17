# Ride Hailing (Uber / Ola)

> Driver matching, pricing, trip state — **State** (trip lifecycle) + **Strategy** (matching / pricing). 🔴

## Scope / requirements

**In:** rider requests trip, match driver, start/end trip, fare estimate + final fare, basic statuses (`REQUESTED → MATCHED → EN_ROUTE → IN_PROGRESS → COMPLETED` / `CANCELLED`).

**Out:** real GPS streaming, map matching, multi-hop pooling depth (mention as extension), payments beyond “charge fare”.

## Entities

| Entity | Owns |
|--------|------|
| `Rider`, `Driver` | identity; driver: location, status (`IDLE`/`BUSY`) |
| `Trip` | pickup/drop, status, fare, driver_id |
| `MatchingStrategy` | who gets the request |
| `PricingStrategy` | estimate + final fare |
| `Location` | lat/lng value object |

## Invariants

- Only `IDLE` drivers are matchable.
- A driver has at most one `IN_PROGRESS` / `EN_ROUTE` trip.
- Fare is computed by strategy at estimate time and again at complete (or locked estimate — say which).
- Illegal status transitions raise domain errors.

## Interfaces / patterns — and why

| Seam | Pattern | Why |
|------|---------|-----|
| Trip lifecycle | **State** | Behavior (cancel fees, who can start) depends on status |
| Driver selection | **Strategy** | Nearest / highest rating / ETA |
| Pricing | **Strategy** | Base + time/distance; surge as decorator or strategy |

## End-to-end flow

1. Rider `request(pickup, drop)` → `Trip(REQUESTED)` + fare estimate via `PricingStrategy`.
2. `MatchingStrategy.match(trip, idle_drivers)` → bind driver → `MATCHED`; driver → `BUSY`.
3. Driver arrives → `EN_ROUTE` (or skip) → start → `IN_PROGRESS` → end → `COMPLETED`, fare finalize, driver → `IDLE`.

## Skeletons

### Python

```python
from abc import ABC, abstractmethod
from enum import Enum, auto


class TripStatus(Enum):
    REQUESTED = auto()
    MATCHED = auto()
    EN_ROUTE = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    CANCELLED = auto()


class MatchingStrategy(ABC):
    @abstractmethod
    def match(self, trip, drivers: list): ...


class NearestDriver(MatchingStrategy):
    def match(self, trip, drivers: list):
        idle = [d for d in drivers if d.status == "IDLE"]
        return min(idle, key=lambda d: d.distance_to(trip.pickup), default=None)


class PricingStrategy(ABC):
    @abstractmethod
    def estimate(self, pickup, drop) -> float: ...
    @abstractmethod
    def finalize(self, trip) -> float: ...


class Trip:
    def __init__(self, id: str, pickup, drop):
        self.id, self.pickup, self.drop = id, pickup, drop
        self.status = TripStatus.REQUESTED
        self.driver_id = None
        self.fare: float | None = None

    def to(self, status: TripStatus) -> None:
        # enforce ALLOWED transitions
        self.status = status


class RideService:
    def __init__(self, matcher: MatchingStrategy, pricing: PricingStrategy):
        self._matcher, self._pricing = matcher, pricing

    def request(self, trip: Trip, drivers: list) -> Trip:
        trip.fare = self._pricing.estimate(trip.pickup, trip.drop)
        driver = self._matcher.match(trip, drivers)
        if not driver:
            raise RuntimeError("no drivers")
        trip.driver_id = driver.id
        driver.status = "BUSY"
        trip.to(TripStatus.MATCHED)
        return trip

    def complete(self, trip: Trip, driver) -> None:
        trip.fare = self._pricing.finalize(trip)
        trip.to(TripStatus.COMPLETED)
        driver.status = "IDLE"
```

### Go

```go
type MatchingStrategy interface {
    Match(trip *Trip, drivers []*Driver) *Driver
}

type PricingStrategy interface {
    Estimate(pickup, drop Location) float64
    Finalize(trip *Trip) float64
}

type Trip struct {
    ID, DriverID string
    Pickup, Drop Location
    Status       TripStatus
    Fare         float64
}

type RideService struct {
    Matcher MatchingStrategy
    Pricing PricingStrategy
}

func (s *RideService) Request(trip *Trip, drivers []*Driver) error {
    trip.Fare = s.Pricing.Estimate(trip.Pickup, trip.Drop)
    d := s.Matcher.Match(trip, drivers)
    if d == nil {
        return fmt.Errorf("no drivers")
    }
    trip.DriverID = d.ID
    d.Status = Busy
    trip.Status = Matched
    return nil
}

func (s *RideService) Complete(trip *Trip, d *Driver) {
    trip.Fare = s.Pricing.Finalize(trip)
    trip.Status = Completed
    d.Status = Idle
}
```

## Concurrency / consistency

- Matching is a classic **race**: two riders claim one driver — CAS on `driver.status IDLE→BUSY` keyed by `driver_id`.
- Trip updates: lock per `trip_id` or single-writer actor per trip.
- Idempotent `complete(trip_id)` for retries after network blips.

## Tradeoffs / pitfalls

- Don’t simulate continuous GPS; snapshot location on request/match.
- Matching + pricing + payments in one class — keep strategies injectable.
- Forgetting cancel paths and who pays cancellation fee (state-dependent).

## Interview prompts

- Nearest vs rating-based matching — what’s the interface?
- Surge: new strategy or decorator on base pricing?
- How do you prevent double-assigning a driver?

## Exercise / follow-ups

1. Add cancel rules: free before match; fee after `MATCHED`.
2. Implement `SurgePricing` wrapping a base strategy (Decorator).
3. Sketch CAS pseudocode for `Idle → Busy`.
