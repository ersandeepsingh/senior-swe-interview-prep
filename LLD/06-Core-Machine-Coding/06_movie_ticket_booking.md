# Movie Ticket Booking (BookMyShow-style)

> Seat locking, concurrency, payment → **Concurrency + Strategy**. 🔴

## Scope / Requirements

**In scope**
- Movies, shows (screen + time), seat map.
- User selects seats → temporary lock → pay → confirm booking.
- Lock expiry releases seats; payment failure releases seats.
- Pricing strategy (weekday/weekend, premium seats).

**Out of scope**
- Full payment gateway, partner inventory sync, recommendations.

**Domain invariants**
- A seat for a show is Free, Locked, or Booked — never double-booked.
- Lock held by one session with TTL; only that session may confirm.
- Confirm is idempotent for a booking id; payment success transitions Locked → Booked atomically.
- Available seat query must not show Locked/Booked as free.

## Core Entities & Responsibilities

| Entity | Responsibility |
|--------|----------------|
| `Movie` / `Screen` / `Show` | Catalog + seat layout reference. |
| `Seat` / `ShowSeat` | Per-show seat state. |
| `SeatLock` | Session id, seat ids, expiry. |
| `Booking` | User, show, seats, status, amount. |
| `BookingService` | Lock, confirm, cancel orchestration. |
| `PricingStrategy` | Compute total. |
| `PaymentGateway` | Port; success/fail. |

## Key Interfaces / Patterns

- **Concurrency control:** pessimistic lock / CAS on seat rows — *the* senior topic.
- **Strategy — pricing:** base + seat category.
- **State:** booking Initiated → Locked → Confirmed / Expired / Failed.
- **Optional Optimistic UI** vs server truth — discuss.

## End-to-End Flow

1. List seats for show → user picks A1,A2.
2. `lockSeats(session, show, [A1,A2], ttl=10m)` under lock; fail if not Free.
3. `confirm(session, payment)` → charge → mark Booked → issue booking id.
4. Background sweeper expires locks → Free.

## Python Skeleton

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from threading import Lock
from typing import Optional


class SeatStatus(Enum):
    FREE = auto()
    LOCKED = auto()
    BOOKED = auto()


@dataclass
class ShowSeat:
    seat_id: str
    status: SeatStatus = SeatStatus.FREE
    locked_by: Optional[str] = None
    lock_until: Optional[datetime] = None


@dataclass
class Booking:
    booking_id: str
    show_id: str
    user_id: str
    seats: list[str]
    amount: float
    status: str  # CONFIRMED


class PricingStrategy(ABC):
    @abstractmethod
    def price(self, show_id: str, seats: list[str]) -> float: ...


class FlatPricing(PricingStrategy):
    def __init__(self, unit: float = 200.0):
        self.unit = unit

    def price(self, show_id: str, seats: list[str]) -> float:
        return self.unit * len(seats)


class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, user_id: str, amount: float, idem_key: str) -> bool: ...


class BookingService:
    def __init__(self, pricing: PricingStrategy, payments: PaymentGateway):
        self._shows: dict[str, dict[str, ShowSeat]] = {}
        self._pricing = pricing
        self._payments = payments
        self._mu = Lock()
        self._seq = 0

    def add_show(self, show_id: str, seat_ids: list[str]) -> None:
        self._shows[show_id] = {s: ShowSeat(s) for s in seat_ids}

    def lock_seats(self, show_id: str, seat_ids: list[str], session_id: str, ttl_sec: int = 600) -> None:
        now = datetime.utcnow()
        with self._mu:
            self._expire_unlocked(show_id, now)
            seats = self._shows[show_id]
            for sid in seat_ids:
                st = seats[sid]
                if st.status == SeatStatus.BOOKED:
                    raise RuntimeError(f"{sid} booked")
                if st.status == SeatStatus.LOCKED and st.locked_by != session_id and st.lock_until > now:
                    raise RuntimeError(f"{sid} locked")
            until = now + timedelta(seconds=ttl_sec)
            for sid in seat_ids:
                st = seats[sid]
                st.status = SeatStatus.LOCKED
                st.locked_by = session_id
                st.lock_until = until

    def confirm(self, show_id: str, seat_ids: list[str], user_id: str, session_id: str) -> Booking:
        amount = self._pricing.price(show_id, seat_ids)
        # charge outside seat mutex when possible; re-check under lock
        ok = self._payments.charge(user_id, amount, idem_key=f"{session_id}:{show_id}")
        if not ok:
            self.release(show_id, seat_ids, session_id)
            raise RuntimeError("payment failed")
        with self._mu:
            now = datetime.utcnow()
            seats = self._shows[show_id]
            for sid in seat_ids:
                st = seats[sid]
                if st.locked_by != session_id or st.status != SeatStatus.LOCKED or st.lock_until < now:
                    raise RuntimeError("lock lost")
                st.status = SeatStatus.BOOKED
                st.locked_by = None
            self._seq += 1
            return Booking(f"B{self._seq}", show_id, user_id, seat_ids, amount, "CONFIRMED")

    def release(self, show_id: str, seat_ids: list[str], session_id: str) -> None:
        with self._mu:
            for sid in seat_ids:
                st = self._shows[show_id][sid]
                if st.locked_by == session_id and st.status == SeatStatus.LOCKED:
                    st.status = SeatStatus.FREE
                    st.locked_by = st.lock_until = None

    def _expire_unlocked(self, show_id: str, now: datetime) -> None:
        for st in self._shows[show_id].values():
            if st.status == SeatStatus.LOCKED and st.lock_until and st.lock_until < now:
                st.status = SeatStatus.FREE
                st.locked_by = st.lock_until = None
```

## Go Skeleton

```go
package booking

import (
    "errors"
    "sync"
    "time"
)

type SeatStatus int

const (
    Free SeatStatus = iota
    Locked
    Booked
)

type ShowSeat struct {
    ID        string
    Status    SeatStatus
    LockedBy  string
    LockUntil time.Time
}

type PricingStrategy interface {
    Price(showID string, seats []string) float64
}

type PaymentGateway interface {
    Charge(userID string, amount float64, idemKey string) bool
}

type Service struct {
    mu       sync.Mutex
    shows    map[string]map[string]*ShowSeat
    pricing  PricingStrategy
    payments PaymentGateway
    seq      int
}

func (s *Service) LockSeats(showID string, seats []string, session string, ttl time.Duration) error {
    s.mu.Lock()
    defer s.mu.Unlock()
    now := time.Now()
    sm := s.shows[showID]
    for _, id := range seats {
        st := sm[id]
        s.expire(st, now)
        if st.Status == Booked || (st.Status == Locked && st.LockedBy != session) {
            return errors.New("unavailable: " + id)
        }
    }
    until := now.Add(ttl)
    for _, id := range seats {
        st := sm[id]
        st.Status, st.LockedBy, st.LockUntil = Locked, session, until
    }
    return nil
}

func (s *Service) Confirm(showID string, seats []string, userID, session string) (string, error) {
    amount := s.pricing.Price(showID, seats)
    if !s.payments.Charge(userID, amount, session+":"+showID) {
        _ = s.Release(showID, seats, session)
        return "", errors.New("payment failed")
    }
    s.mu.Lock()
    defer s.mu.Unlock()
    now := time.Now()
    for _, id := range seats {
        st := s.shows[showID][id]
        if st.LockedBy != session || st.Status != Locked || st.LockUntil.Before(now) {
            return "", errors.New("lock lost")
        }
        st.Status, st.LockedBy = Booked, ""
    }
    s.seq++
    return "B" + string(rune('0'+s.seq%10)), nil
}

func (s *Service) Release(showID string, seats []string, session string) error {
    s.mu.Lock()
    defer s.mu.Unlock()
    for _, id := range seats {
        st := s.shows[showID][id]
        if st.LockedBy == session && st.Status == Locked {
            st.Status, st.LockedBy = Free, ""
        }
    }
    return nil
}

func (s *Service) expire(st *ShowSeat, now time.Time) {
    if st.Status == Locked && st.LockUntil.Before(now) {
        st.Status, st.LockedBy = Free, ""
    }
}
```

## Concurrency / Consistency

- Critical section: check Free + set Locked (same for Booked).
- Payment then confirm: re-validate lock; use idempotency key on charge.
- Distributed: Redis lock / DB `UPDATE … WHERE status='FREE'` row count check.
- Sweeper vs lazy expiry on read — both OK if consistent.

## Extensions / Trade-offs / Pitfalls

- Partial lock failure: all-or-nothing seat group.
- Pitfall: showing locked seats as available (stale cache).
- Group booking hold vs single-seat races.
- Overbooking for “social distancing” blocked seats — seat layout metadata.

## Interview Discussion Points

- Pessimistic seat lock vs saga — which for tickets and why?
- Where do you put TTL expiry — DB job, Redis TTL, lazy on access?
- How do you design idempotent `confirm` for double-clicks?

## Exercise

Implement lock → pay → confirm for one show with 2 seats under a mutex.

**Follow-ups**
1. Two users race for the same seat — write the failing interleaving and your fix.
2. Add premium seat multiplier via pricing Strategy only.
3. Sketch SQL for atomic lock of N seats.
