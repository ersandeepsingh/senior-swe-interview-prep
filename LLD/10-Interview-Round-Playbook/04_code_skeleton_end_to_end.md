# Step 4 — Code the Skeleton / End-to-End Flow (~25–35 min)

Interfaces + key classes + **one working flow** park→unpark. Leave stubs and say so. Working demo beats perfect UML.

## Minute budget

| Min | Do this |
|-----|---------|
| 0–5 | Interfaces + enums + data classes |
| 5–15 | `ParkingLot.park` / find free spot / create ticket |
| 15–25 | `unpark` + pricing strategy + release spot |
| 25–35 | Tiny main/demo; stub extras; narrate gaps |

## Exact phrases to say

- “I’ll code the happy path end-to-end first: park then unpark with a fee.”
- “Leaving `findNearest` as first-free for now — swap allocation strategy later.”
- “Stubbing persistence behind a dict; repository interface if we have time.”
- “Demo: motorcycle parks, exits after 2 hours → fee printed.”

## Worked example — Parking Lot

### Python — skeleton that runs

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

@dataclass
class Money:
    cents: int

class PricingStrategy(Protocol):
    def fee(self, hours: float, vehicle_type: str) -> Money: ...

class HourlyPricing:
    def __init__(self, rate_cents: int = 1000):  # $10/hr
        self.rate = rate_cents
    def fee(self, hours: float, vehicle_type: str) -> Money:
        billable = max(1, int(hours + 0.999))  # ceil hour
        return Money(billable * self.rate)

@dataclass
class Spot:
    id: str
    spot_type: str
    vehicle_plate: str | None = None

@dataclass
class Ticket:
    id: str
    plate: str
    spot_id: str
    entry: datetime

class ParkingLot:
    def __init__(self, spots: list[Spot], pricing: PricingStrategy):
        self.spots = {s.id: s for s in spots}
        self.tickets: dict[str, Ticket] = {}
        self.pricing = pricing
        self._n = 0

    def park(self, plate: str, vehicle_type: str) -> Ticket:
        spot = next((s for s in self.spots.values()
                     if s.vehicle_plate is None and s.spot_type == vehicle_type), None)
        if not spot:
            raise ValueError("lot full for type")
        spot.vehicle_plate = plate
        self._n += 1
        t = Ticket(f"T{self._n}", plate, spot.id, datetime.utcnow())
        self.tickets[t.id] = t
        return t

    def unpark(self, ticket_id: str, exit_at: datetime | None = None) -> Money:
        t = self.tickets.pop(ticket_id)
        exit_at = exit_at or datetime.utcnow()
        hours = (exit_at - t.entry).total_seconds() / 3600
        self.spots[t.spot_id].vehicle_plate = None
        return self.pricing.fee(hours, "ignored")  # type from ticket in fuller design
```

### Go — same flow

```go
type PricingStrategy interface{ Fee(hours float64) int } // cents

type HourlyPricing struct{ RateCents int }
func (h HourlyPricing) Fee(hours float64) int {
    billable := int(hours + 0.999)
    if billable < 1 { billable = 1 }
    return billable * h.RateCents
}

type Spot struct{ ID, Type string; Plate *string }
type Ticket struct{ ID, Plate, SpotID string; Entry time.Time }

type ParkingLot struct {
    Spots   map[string]*Spot
    Tickets map[string]*Ticket
    Pricing PricingStrategy
    seq     int
}

func (p *ParkingLot) Park(plate, vType string) (*Ticket, error) {
    for _, s := range p.Spots {
        if s.Plate == nil && s.Type == vType {
            s.Plate = &plate
            p.seq++
            t := &Ticket{ID: fmt.Sprintf("T%d", p.seq), Plate: plate, SpotID: s.ID, Entry: time.Now().UTC()}
            p.Tickets[t.ID] = t
            return t, nil
        }
    }
    return nil, errors.New("lot full")
}

func (p *ParkingLot) Unpark(ticketID string, exit time.Time) (int, error) {
    t, ok := p.Tickets[ticketID]
    if !ok { return 0, errors.New("unknown ticket") }
    delete(p.Tickets, ticketID)
    p.Spots[t.SpotID].Plate = nil
    hours := exit.Sub(t.Entry).Hours()
    return p.Pricing.Fee(hours), nil
}
```

**Narrate stubs:** multi-floor indexing, nearest-spot, vehicle-type rate table, ticket store persistence.

## Common mistakes

- Writing every class fully before any runnable path
- Silent coding for 20 minutes — narrate decisions
- Perfecting helpers while `park` still doesn’t compile
- Hiding the Strategy behind concrete `if rate == …` mid-skeleton

## Interviewer signals

| Signal | Meaning |
|--------|---------|
| “Can you demo it?” | Run/main path — prioritize this |
| “What about floors?” | Add `Floor` container; don’t rewrite pricing |
| Time warning at :40 | Freeze features; polish demo + step 5 talk |

## Exercise / checklist

- [ ] Compilable/runnable park → unpark path
- [ ] Pricing behind an interface
- [ ] At least one failure path (`lot full`) mentioned or coded
- [ ] Said out loud what is stubbed
- [ ] Can walk the call stack in 90 seconds
