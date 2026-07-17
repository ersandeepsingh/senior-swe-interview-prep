# Step 3 — Pick Load-Bearing Patterns (~5 min)

Name the **1–2 patterns that carry the design**. Don’t pattern-stuff. Interviewers probe the seam that will change.

## Minute budget

| Min | Do this |
|-----|---------|
| 0–2 | Name the varying parts (algorithms, lifecycle, creation) |
| 2–4 | Map each to one pattern; say why |
| 4–5 | Say what you will *not* use and why |

## Exact phrases to say

- “Load-bearing here: **Strategy** for pricing (hourly vs flat later), **Factory** optional for creating typed spots.”
- “Spot occupancy is a boolean for MVP — full **State** machine is overkill unless we add reserved/out-of-order.”
- “I’m not adding Observer/Mediator unless we need entry-gate displays or notifications.”
- “If we add EV/handicap rules, allocation becomes a Strategy too — I’ll leave an interface.”

## Heuristic map (reuse every problem)

| If this varies… | Reach for |
|-----------------|-----------|
| Algorithm (price, match, split) | **Strategy** |
| Lifecycle (order, ticket, machine) | **State** |
| Creation of families/types | **Factory** |
| Notify many listeners | **Observer** |
| Stackable rules/middleware | **Chain of Responsibility** |
| Concurrent critical section | Lock / actor (call out in step 5) |

## Worked example — Parking Lot

| Concern | Pattern | Why |
|---------|---------|-----|
| Fee calculation | **Strategy** | Hourly / flat / free-hours swap without editing `unpark` |
| Spot creation by type | **Factory** (light) | `create_spot(type)` — optional if enum + ctor is enough |
| Ticket lifecycle | Data + methods | Entry/exit times; skip full State unless interviewer pushes |

### Python — name the seam

```python
class PricingStrategy(Protocol):
    def fee(self, ticket: Ticket, exit_at: datetime) -> Money: ...

class HourlyPricing:
    def __init__(self, rates: dict[SpotType, float]): ...
    def fee(self, ticket: Ticket, exit_at: datetime) -> Money: ...
```

### Go — name the seam

```go
type PricingStrategy interface {
    Fee(t Ticket, exit time.Time) Money
}

type HourlyPricing struct{ Rates map[SpotType]float64 }
func (h HourlyPricing) Fee(t Ticket, exit time.Time) Money { /* ... */ }
```

## Common mistakes

- Listing six patterns in the intro (“I’ll use Singleton, Facade…”)
- Strategy for everything including one-line helpers
- Forcing State when a bool + timestamps suffice
- Never naming *where* the pattern sits (the interface / method)

## Interviewer signals

| Signal | Meaning |
|--------|---------|
| “What if pricing changes tomorrow?” | They want Strategy — confirm it |
| “Add reserved spots” | State or status enum on Spot |
| “Don’t over-engineer” | Drop Factory; keep Strategy if pricing is real |

## Exercise / checklist

- [ ] Named ≤2 load-bearing patterns out loud
- [ ] Pointed at the exact interface/method for each
- [ ] Explicitly rejected ≥1 pattern as YAGNI
- [ ] Linked pattern choice to a clarifying answer from step 1
