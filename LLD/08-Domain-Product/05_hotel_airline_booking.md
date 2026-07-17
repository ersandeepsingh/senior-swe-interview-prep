# Hotel / Airline Booking

> Availability, reservation, cancellation — **concurrency** (seat/room hold) + **State**. 🔴

## Scope / requirements

**In:** search availability by date (hotel) or flight/seat map (airline), hold resource with TTL, confirm after payment, cancel/refund rules.

**Out:** full GDS/Amadeus integration, dynamic packaging, loyalty tiers depth — stub as ports.

## Entities

| Entity | Owns |
|--------|------|
| `RoomType` / `Flight` + `Seat` | inventory unit |
| `InventorySlot` | date × room or flight × seat |
| `Hold` / `Reservation` | temporary lock + expiry |
| `Booking` | confirmed reservation + state |
| `PricingStrategy` (optional) | seasonal rates |

## Invariants

- A seat/room-night cannot be confirmed twice overlapping the same interval.
- Hold expires → inventory returns to available.
- Confirm only from `HELD`; cancel rules depend on state / policy.
- Overlapping hotel bookings for same room are forbidden (interval conflict).

## Interfaces / patterns — and why

| Seam | Pattern | Why |
|------|---------|-----|
| Booking lifecycle | **State** | Hold → Confirmed → CheckedIn / Cancelled |
| Fare / rate | **Strategy** | Weekday vs weekend, cabin class |
| Search | Repository / index | Query available slots |
| Locking | Mutex / CAS / DB constraint | The senior ask |

## End-to-end flow

1. Search available rooms/seats for dates.
2. `hold(resource, user, ttl)` → `Booking(HELD)`.
3. Pay → `confirm` → `CONFIRMED`; or TTL sweeper → release.
4. `cancel` per policy → free inventory.

## Skeletons

### Python

```python
import time
from enum import Enum, auto


class BookingStatus(Enum):
    HELD = auto()
    CONFIRMED = auto()
    CANCELLED = auto()
    EXPIRED = auto()


class SeatInventory:
    def __init__(self):
        self._available: set[str] = set()
        self._holds: dict[str, tuple[str, float]] = {}  # seat -> (user, expiry)

    def add_seats(self, seats: list[str]) -> None:
        self._available.update(seats)

    def hold(self, seat: str, user: str, ttl_sec: float) -> bool:
        self._expire()
        if seat not in self._available:
            return False
        self._available.remove(seat)
        self._holds[seat] = (user, time.time() + ttl_sec)
        return True

    def confirm(self, seat: str, user: str) -> bool:
        self._expire()
        h = self._holds.get(seat)
        if not h or h[0] != user:
            return False
        del self._holds[seat]
        return True  # seat now owned by booking store

    def release(self, seat: str) -> None:
        self._holds.pop(seat, None)
        self._available.add(seat)

    def _expire(self) -> None:
        now = time.time()
        for seat, (_, exp) in list(self._holds.items()):
            if exp <= now:
                self.release(seat)


class Booking:
    def __init__(self, id: str, seat: str):
        self.id, self.seat = id, seat
        self.status = BookingStatus.HELD

    def confirm(self) -> None:
        if self.status != BookingStatus.HELD:
            raise ValueError("not held")
        self.status = BookingStatus.CONFIRMED
```

### Go

```go
type SeatInventory struct {
    mu        sync.Mutex
    available map[string]struct{}
    holds     map[string]hold // seat -> user + expiry
}

type hold struct {
    user   string
    expiry time.Time
}

func (inv *SeatInventory) Hold(seat, user string, ttl time.Duration) bool {
    inv.mu.Lock()
    defer inv.mu.Unlock()
    inv.expireLocked()
    if _, ok := inv.available[seat]; !ok {
        return false
    }
    delete(inv.available, seat)
    inv.holds[seat] = hold{user, time.Now().Add(ttl)}
    return true
}

func (inv *SeatInventory) Confirm(seat, user string) bool {
    inv.mu.Lock()
    defer inv.mu.Unlock()
    inv.expireLocked()
    h, ok := inv.holds[seat]
    if !ok || h.user != user {
        return false
    }
    delete(inv.holds, seat)
    return true
}
```

## Concurrency / consistency

- **Two users, one seat:** mutex per flight/cabin or DB `UNIQUE(seat, flight)` on confirmed rows; hold table with expiry.
- Optimistic: version column on inventory row; retry on conflict.
- Never “check then book” without a lock — classic TOCTOU.

## Tradeoffs / pitfalls

- Hotel date ranges need **interval overlap** checks, not just equality.
- Infinite holds without TTL = inventory leak.
- Confirming without verifying hold ownership (user mismatch).

## Interview prompts

- Hold TTL vs soft booking — tradeoffs?
- How do airlines overbook? (policy layer — don’t bake into inventory math blindly)
- Hotel: room instance vs room type inventory?

## Exercise / follow-ups

1. Hotel `RoomType` with count N and date-range overlap reservation list.
2. Cancellation policy Strategy (free 24h before / non-refundable).
3. Explain how you’d make `Hold` safe across two app servers (DB/Redis).
