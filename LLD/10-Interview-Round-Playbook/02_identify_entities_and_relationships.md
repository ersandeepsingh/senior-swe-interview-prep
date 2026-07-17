# Step 2 — Identify Entities & Relationships (~10 min)

Nouns → classes, verbs → methods. State the core objects and how they relate **out loud** before coding.

## Minute budget

| Min | Do this |
|-----|---------|
| 0–3 | List nouns from requirements |
| 3–6 | Draw/say relationships (has-a, uses) |
| 6–10 | Name key methods + ownership of state |

## Exact phrases to say

- “Core entities: `ParkingLot`, `Floor`, `Spot`, `Vehicle`, `Ticket`, and a `PricingStrategy`.”
- “A lot **has** floors; a floor **has** spots; a ticket **binds** vehicle + spot + entry time.”
- “`ParkingLot` owns allocation; spots don’t choose themselves.”
- “I’ll keep pricing off the ticket — ticket is data; strategy computes fee.”

## Worked example — Parking Lot

```
ParkingLot
  └── Floor[] 
        └── Spot[]  (type, occupied?, vehicle?)
Vehicle (plate, type)
Ticket (id, vehicle, spot, entryTime, exitTime?)
PricingStrategy → fee(ticket) 
```

**Verbs → API surface:**
- `park(vehicle) → Ticket | error`
- `unpark(ticketId) → Fee`
- `availability(type?) → counts` (optional stretch)

### Python sketch (types only)

```python
class SpotType(Enum): COMPACT = 1; LARGE = 2; MOTORCYCLE = 3

@dataclass
class Vehicle:
    plate: str
    type: SpotType

@dataclass
class Spot:
    id: str
    type: SpotType
    vehicle: Vehicle | None = None

@dataclass
class Ticket:
    id: str
    vehicle: Vehicle
    spot: Spot
    entry: datetime
```

### Go sketch (types only)

```go
type SpotType int
const (Compact SpotType = iota; Large; Motorcycle)

type Vehicle struct{ Plate string; Type SpotType }
type Spot struct{ ID string; Type SpotType; Vehicle *Vehicle }
type Ticket struct {
    ID string; Vehicle Vehicle; SpotID string; Entry time.Time
}
```

## Common mistakes

- Modeling UI/DB tables as domain objects
- `Spot.park()` that knows pricing, floors, and gates (God spot)
- Forgetting `Ticket` — then exit fee has nowhere to hang
- Deep inheritance (`Car`/`Truck` subclasses) when an enum + type field is enough

## Interviewer signals

| Signal | Meaning |
|--------|---------|
| “Who owns the spot list?” | Clarify aggregate root (`ParkingLot` / `Floor`) |
| “Why isn’t fee on Ticket?” | They want Strategy / SRP separation |
| Silent nod | Move to patterns — don’t over-UML |

## Exercise / checklist

- [ ] Wrote 5–8 entity names
- [ ] Said ownership: who creates tickets, who marks spots occupied
- [ ] Listed park/unpark signatures
- [ ] Avoided inheritance tree for vehicle types (enum OK)
- [ ] Can explain relationships in 60 seconds without code
