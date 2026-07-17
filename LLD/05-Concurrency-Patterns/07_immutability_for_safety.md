# Immutability for Safety

> **Share data across threads freely** when it cannot change after creation — no locks needed for readers if nothing mutates.

## Plain English

If nobody can erase or scribble on the shared whiteboard, everyone can read it at once without fighting over a marker. “Change” means creating a new value and swapping a reference atomically.

## Simple analogy

Printed newspaper edition: everyone reads the same copy; corrections ship as tomorrow’s edition, not edits in place.

## Why seniors get asked this

Config snapshots, money totals, event payloads, functional-style state updates — seniors reduce lock scope by making shared data immutable or copy-on-write.

## Good: immutable values + atomic snapshot swap

### Python

```python
from dataclasses import dataclass
from typing import FrozenSet
import threading


@dataclass(frozen=True)
class SeatMap:
    available: FrozenSet[str]

    def reserve(self, seat_id: str) -> "SeatMap":
        if seat_id not in self.available:
            raise ValueError("seat not available")
        return SeatMap(self.available - {seat_id})


class BookingService:
    def __init__(self, seats: set[str]) -> None:
        self._lock = threading.Lock()
        self._map = SeatMap(frozenset(seats))

    def reserve(self, seat_id: str) -> SeatMap:
        with self._lock:
            updated = self._map.reserve(seat_id)
            self._map = updated  # publish new immutable snapshot
            return updated

    def snapshot(self) -> SeatMap:
        return self._map  # safe to read fields; don't mutate nested mutables
```

`frozen=True` makes the dataclass immutable; `FrozenSet` prevents mutating the seat collection. The lock guards the **reference swap**, not every read.

### Go

```go
package main

import (
    "fmt"
    "maps"
    "sync"
    "sync/atomic"
)

type SeatMap struct {
    available map[string]struct{}
}

func NewSeatMap(seats []string) SeatMap {
    m := make(map[string]struct{}, len(seats))
    for _, s := range seats {
        m[s] = struct{}{}
    }
    return SeatMap{available: m}
}

func (sm SeatMap) Reserve(seatID string) (SeatMap, error) {
    if _, ok := sm.available[seatID]; !ok {
        return SeatMap{}, fmt.Errorf("seat not available")
    }
    next := make(map[string]struct{}, len(sm.available)-1)
    maps.Copy(next, sm.available)
    delete(next, seatID)
    return SeatMap{available: next}, nil
}

type BookingService struct {
    mu  sync.Mutex
    ptr atomic.Pointer[SeatMap]
}

func NewBookingService(seats []string) *BookingService {
    sm := NewSeatMap(seats)
    b := &BookingService{}
    b.ptr.Store(&sm)
    return b
}

func (b *BookingService) Reserve(seatID string) error {
    b.mu.Lock()
    defer b.mu.Unlock()
    cur := b.ptr.Load()
    next, err := cur.Reserve(seatID)
    if err != nil {
        return err
    }
    b.ptr.Store(&next)
    return nil
}

func (b *BookingService) Snapshot() SeatMap {
    return *b.ptr.Load() // copy struct; map header copied — treat map as read-only
}
```

Readers can `Load()` the pointer without the mutex if they only need a consistent snapshot and never mutate the map in place. Writers still serialize updates under `mu` when creating the next version.

## Concurrency safety

| Concern | What to watch |
|---------|----------------|
| **Race** | “Immutable” object holding a **mutable** `list`/`dict` — callers can still mutate innards. Deep immutability or defensive copies matter. |
| **Deadlock** | Fewer locks → fewer deadlocks; swapping references wrong can still race if two writers don’t coordinate. |
| **Stale reads** | Readers see an old snapshot — fine for config; not fine if you need latest balance without version checks. |

**Python GIL:** immutability reduces need for locks on reads, but publishing a new object still needs a lock or careful atomic reference swap if multiple writers exist.

## When to use / not use

**Use:** value objects (money, coordinates); config snapshots; event records passed between threads; reduce lock contention on read-heavy paths.

**Don’t use:** hot path with constant small mutations (locking a mutable struct may be simpler); large structures where copy-on-write is too expensive; when you need in-place updates for performance with proven safety.

## Pitfalls

- Shallow immutability — frozen dataclass with `list` field still mutable inside.
- Returning internal mutable map from `snapshot()` in Go — document read-only or copy.
- Assuming immutability fixes distributed consistency — still need transactions/locking across services.
- Confusing with Encapsulation principle — here the focus is **cross-thread safety**, not just API design.

## Interview trigger phrase

> “I’d use **immutable snapshots** — readers take the current version without locks; writers publish a new copy under a short lock.”

## Exercise

**Exchange rate table** refreshed every 60s; thousands of threads read rates for pricing.

1. Immutable snapshot vs RWLock — compare memory and complexity.
2. What if `rates` is `dict[str, float]` inside a frozen dataclass?
3. How do readers know they’re not on a stale rate for compliance?
