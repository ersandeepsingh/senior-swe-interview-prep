# Step 5 — Concurrency, Extensibility & Testing (~5–10 min)

Even if you don’t fully implement these, **call them out**. This is the senior differentiator after a working skeleton.

## Minute budget

| Min | Do this |
|-----|---------|
| 0–3 | Concurrency: races + how you’d lock |
| 3–6 | Extensibility: next requirement → which seam |
| 6–10 | Testing: 3–5 cases you’d write; DI for fakes |

## Exact phrases to say

- “Two attendants calling `park` can grab the same spot — I’d synchronize allocation or use compare-and-set on spot occupancy.”
- “Pricing and allocation are Strategy seams; new vehicle type is mostly data + rate map, not a rewrite.”
- “I’d inject `PricingStrategy` and a clock so tests don’t sleep; cases: full lot, double-unpark, fee ceiling.”
- “Idempotent unpark: second call with same ticket id should fail cleanly, not double-charge.”

## Worked example — Parking Lot

### Concurrency

**Race:** Thread A and B both see Spot S free → both assign → one ticket orphaned / double-book.

**Fix options (say one):**
- Mutex around `find free + occupy` in `ParkingLot`
- Per-spot lock / atomic `tryOccupy`
- Single-threaded actor owning the lot (message park/unpark)

```python
# sketch — lock the critical section
class ParkingLot:
    def __init__(self, ...):
        self._lock = threading.Lock()
    def park(self, plate: str, vehicle_type: str) -> Ticket:
        with self._lock:
            return self._park_unlocked(plate, vehicle_type)
```

```go
func (p *ParkingLot) Park(plate, vType string) (*Ticket, error) {
    p.mu.Lock()
    defer p.mu.Unlock()
    return p.parkLocked(plate, vType)
}
```

### Extensibility

| Next ask | Seam |
|----------|------|
| Flat-rate weekend pricing | New `PricingStrategy` |
| Prefer EV spots / nearest entry | `AllocationStrategy` |
| Notify display boards | Observer on park/unpark |
| Persist tickets | `TicketRepository` interface |

### Testing

```python
def test_park_unpark_fee():
    lot = ParkingLot([Spot("1", "CAR")], HourlyPricing(1000))
    t = lot.park("XYZ", "CAR")
    fee = lot.unpark(t.id, exit_at=t.entry + timedelta(hours=2))
    assert fee.cents == 2000

def test_lot_full():
    lot = ParkingLot([Spot("1", "CAR")], HourlyPricing())
    lot.park("A", "CAR")
    with pytest.raises(ValueError):
        lot.park("B", "CAR")
```

**Checklist of cases:** happy path fee · lot full · wrong ticket id · unpark frees spot for next park · (stretch) concurrent park doesn’t double-book.

## Common mistakes

- Never mentioning races after a concurrent prompt
- Over-implementing a full thread pool mid-round
- “I’d unit test everything” with zero concrete cases
- Extensibility = more inheritance instead of Strategy/DI

## Interviewer signals

| Signal | Meaning |
|--------|---------|
| “Two cars enter at once” | They want the lock story — answer even if not coded |
| “Add coupons tomorrow” | Point at Strategy / Chain, don’t rewrite |
| “How do you know it’s right?” | List test cases + injectables |

## Exercise / checklist

- [ ] Named one concrete race and one mitigation
- [ ] Named two future requirements and the seam for each
- [ ] Listed ≥3 unit tests with expected outcomes
- [ ] Mentioned injected clock/strategy for testability
- [ ] Did not derail the demo to implement all three fully
