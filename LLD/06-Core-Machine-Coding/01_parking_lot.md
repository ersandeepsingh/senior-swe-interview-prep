# Parking Lot

> Multi-level lot: spot allocation, ticketing, pricing → **State + Strategy + Factory**. 🟡

## Scope / Requirements

**In scope**
- Multiple floors; spots of types: motorcycle, compact, large (or EV).
- Vehicle entry → allocate spot → issue ticket; exit → compute fee → free spot.
- Pluggable pricing (hourly, flat, progressive).
- Prefer closest / type-compatible spot (simple allocation strategy).

**Out of scope (say so)**
- Real payments, gates hardware, persistence, reservations, valet.

**Domain invariants**
- A spot is either free or occupied by exactly one vehicle.
- A ticket is open until exit; fee uses entry time and pricing strategy.
- Vehicle type must fit spot type (motorcycle ⊆ compact ⊆ large).

## Core Entities & Responsibilities

| Entity | Responsibility |
|--------|----------------|
| `Vehicle` | Identity + type (car, bike, truck). |
| `ParkingSpot` | Type, floor/id, occupied flag, parked vehicle. |
| `Floor` / `ParkingLot` | Aggregate spots; expose availability queries. |
| `Ticket` | Spot + vehicle + entry time; closed on exit. |
| `SpotAllocator` | Strategy: pick a free compatible spot. |
| `PricingStrategy` | Compute fee from duration / ticket. |
| `ParkingService` | Orchestrate park / unpark; issues tickets. |
| `VehicleFactory` (optional) | Create vehicle subtypes from input. |

## Key Interfaces / Patterns

- **Strategy — `PricingStrategy`:** fees change often; open for new pricing without editing exit flow.
- **Strategy — `SpotAllocator`:** nearest, random, EV-first — same park API.
- **State (light):** spot Free/Occupied; ticket Open/Closed — often enums + methods, not full State classes unless asked.
- **Factory:** map plate/type string → `Vehicle` without `if` soup in the service.

## End-to-End Flow

1. Driver arrives with vehicle type + plate.
2. `ParkingService.park` → allocator finds compatible free spot → mark occupied → create open `Ticket` → return ticket id.
3. On exit, load ticket → `PricingStrategy.fee(entry, exit)` → free spot → close ticket → return amount.

## Python Skeleton

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class SpotType(Enum):
    MOTORCYCLE = 1
    COMPACT = 2
    LARGE = 3


class VehicleType(Enum):
    MOTORCYCLE = 1
    CAR = 2
    TRUCK = 3


COMPATIBLE = {
    VehicleType.MOTORCYCLE: {SpotType.MOTORCYCLE, SpotType.COMPACT, SpotType.LARGE},
    VehicleType.CAR: {SpotType.COMPACT, SpotType.LARGE},
    VehicleType.TRUCK: {SpotType.LARGE},
}


@dataclass
class Vehicle:
    plate: str
    vtype: VehicleType


@dataclass
class ParkingSpot:
    spot_id: str
    stype: SpotType
    vehicle: Optional[Vehicle] = None

    @property
    def free(self) -> bool:
        return self.vehicle is None


@dataclass
class Ticket:
    ticket_id: str
    spot_id: str
    vehicle: Vehicle
    entry: datetime
    exit: Optional[datetime] = None


class PricingStrategy(ABC):
    @abstractmethod
    def fee(self, entry: datetime, exit: datetime) -> float: ...


class HourlyPricing(PricingStrategy):
    def __init__(self, rate: float = 10.0):
        self.rate = rate

    def fee(self, entry: datetime, exit: datetime) -> float:
        hours = max(1, int((exit - entry).total_seconds() // 3600) + 1)
        return hours * self.rate


class SpotAllocator(ABC):
    @abstractmethod
    def allocate(self, spots: list[ParkingSpot], vtype: VehicleType) -> Optional[ParkingSpot]: ...


class FirstFitAllocator(SpotAllocator):
    def allocate(self, spots: list[ParkingSpot], vtype: VehicleType) -> Optional[ParkingSpot]:
        allowed = COMPATIBLE[vtype]
        for s in spots:
            if s.free and s.stype in allowed:
                return s
        return None


class ParkingService:
    def __init__(self, spots: list[ParkingSpot], allocator: SpotAllocator, pricing: PricingStrategy):
        self._spots = {s.spot_id: s for s in spots}
        self._allocator = allocator
        self._pricing = pricing
        self._tickets: dict[str, Ticket] = {}
        self._seq = 0

    def park(self, vehicle: Vehicle) -> Ticket:
        spot = self._allocator.allocate(list(self._spots.values()), vehicle.vtype)
        if not spot:
            raise RuntimeError("lot full")
        spot.vehicle = vehicle
        self._seq += 1
        t = Ticket(f"T{self._seq}", spot.spot_id, vehicle, datetime.utcnow())
        self._tickets[t.ticket_id] = t
        return t

    def unpark(self, ticket_id: str) -> float:
        t = self._tickets[ticket_id]
        if t.exit:
            raise RuntimeError("already closed")
        t.exit = datetime.utcnow()
        self._spots[t.spot_id].vehicle = None
        return self._pricing.fee(t.entry, t.exit)
```

## Go Skeleton

```go
package parking

import (
    "errors"
    "time"
)

type SpotType int
type VehicleType int

const (
    SpotMotorcycle SpotType = iota + 1
    SpotCompact
    SpotLarge
)

const (
    VehMotorcycle VehicleType = iota + 1
    VehCar
    VehTruck
)

type Vehicle struct {
    Plate string
    Type  VehicleType
}

type ParkingSpot struct {
    ID      string
    Type    SpotType
    Vehicle *Vehicle
}

func (s *ParkingSpot) Free() bool { return s.Vehicle == nil }

type Ticket struct {
    ID      string
    SpotID  string
    Vehicle Vehicle
    Entry   time.Time
    Exit    *time.Time
}

type PricingStrategy interface {
    Fee(entry, exit time.Time) float64
}

type HourlyPricing struct{ Rate float64 }

func (h HourlyPricing) Fee(entry, exit time.Time) float64 {
    hours := int(exit.Sub(entry).Hours()) + 1
    if hours < 1 {
        hours = 1
    }
    return float64(hours) * h.Rate
}

type SpotAllocator interface {
    Allocate(spots []*ParkingSpot, vt VehicleType) *ParkingSpot
}

type FirstFitAllocator struct{}

func compatible(vt VehicleType, st SpotType) bool {
    switch vt {
    case VehMotorcycle:
        return true
    case VehCar:
        return st == SpotCompact || st == SpotLarge
    case VehTruck:
        return st == SpotLarge
    }
    return false
}

func (FirstFitAllocator) Allocate(spots []*ParkingSpot, vt VehicleType) *ParkingSpot {
    for _, s := range spots {
        if s.Free() && compatible(vt, s.Type) {
            return s
        }
    }
    return nil
}

type ParkingService struct {
    Spots     map[string]*ParkingSpot
    Allocator SpotAllocator
    Pricing   PricingStrategy
    Tickets   map[string]*Ticket
    seq       int
}

func (p *ParkingService) Park(v Vehicle) (*Ticket, error) {
    list := make([]*ParkingSpot, 0, len(p.Spots))
    for _, s := range p.Spots {
        list = append(list, s)
    }
    spot := p.Allocator.Allocate(list, v.Type)
    if spot == nil {
        return nil, errors.New("lot full")
    }
    spot.Vehicle = &v
    p.seq++
    t := &Ticket{ID: fmtID(p.seq), SpotID: spot.ID, Vehicle: v, Entry: time.Now()}
    p.Tickets[t.ID] = t
    return t, nil
}

func (p *ParkingService) Unpark(ticketID string) (float64, error) {
    t, ok := p.Tickets[ticketID]
    if !ok || t.Exit != nil {
        return 0, errors.New("invalid ticket")
    }
    now := time.Now()
    t.Exit = &now
    p.Spots[t.SpotID].Vehicle = nil
    return p.Pricing.Fee(t.Entry, now), nil
}

func fmtID(n int) string { return "T" + string(rune('0'+n%10)) /* sketch */ }
```

## Concurrency / Consistency

- Park and unpark on the same spot must not interleave: lock per spot or one lot mutex in interview code.
- Ticket id generation needs a counter lock or UUID.
- “Check free then occupy” is a classic race — atomic allocate under lock.

## Extensions / Trade-offs / Pitfalls

- Index free spots by type (`dict[SpotType, deque]`) for O(1) allocate vs scan.
- EV spots + charging fees → new spot type + pricing decorator, don’t fork the service.
- Pitfall: allowing truck into motorcycle spot; encode compatibility once.
- Over-design: full State machine for spots when a bool + ticket status is enough.

## Interview Discussion Points

- Why Strategy for pricing vs `if pricing_type == ...` in `unpark`?
- How would you add “reserved spots” without rewriting allocation?
- Floor-level aggregates vs flat spot list — when does hierarchy pay off?

## Exercise

Design **entry + exit** for a 2-floor lot with bike/car/truck spots and hourly pricing.

**Follow-ups**
1. Add a progressive rate (first hour ₹X, then ₹Y) without changing `ParkingService.unpark` signature.
2. Make allocation prefer the lowest floor; say what you change.
3. Under two concurrent entries for the last compact spot, what breaks and how do you fix it?
