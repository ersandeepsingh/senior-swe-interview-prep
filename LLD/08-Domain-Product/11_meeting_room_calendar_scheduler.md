# Meeting Room / Calendar Scheduler

> Booking, conflicts, recurrence — **interval logic** + **Observer**. 🟡

## Scope / requirements

**In:** create rooms, book time ranges, reject overlaps, list agenda, optional recurrence (RRULE-lite: daily/weekly count), cancel, notify attendees.

**Out:** full CalDAV, free/busy across orgs, fancy timezone DB — use aware datetimes and say you’d normalize to UTC.

## Entities

| Entity | Owns |
|--------|------|
| `Room` | id, capacity |
| `Meeting` / `Booking` | room, start, end, attendees |
| `RecurrenceRule` | frequency, count/until |
| `CalendarService` | conflict check + CRUD |
| `SchedulerObserver` | invite notifications |

## Invariants

- For a room, no two bookings with overlapping `[start, end)` (half-open intervals avoid boundary fights).
- `start < end`.
- Cancel removes occurrence (or series — declare scope).
- Recurring expand must still pass conflict checks per instance.

## Interfaces / patterns — and why

| Seam | Pattern | Why |
|------|---------|-----|
| Conflict detection | Interval overlap algorithm | Core domain |
| Notifications | **Observer** | Email/Slack without coupling |
| Recurrence expand | Strategy / helper | Daily vs weekly |
| Persistence | Repository | Find overlapping by room + range |

## End-to-end flow

1. `book(room, start, end, attendees)` → query overlaps → if none, persist → notify.
2. Recurring: expand instances in range → book each or fail all (transactional — say which).
3. `cancel(meeting_id)` → notify cancellation.

## Skeletons

### Python

```python
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod


@dataclass
class Booking:
    id: str
    room_id: str
    start: datetime
    end: datetime
    attendees: list[str]


def overlaps(a_start, a_end, b_start, b_end) -> bool:
    return a_start < b_end and b_start < a_end  # half-open [start, end)


class CalendarObserver(ABC):
    @abstractmethod
    def on_booked(self, booking: Booking) -> None: ...
    @abstractmethod
    def on_cancelled(self, booking: Booking) -> None: ...


class CalendarService:
    def __init__(self):
        self._by_room: dict[str, list[Booking]] = {}
        self._observers: list[CalendarObserver] = []

    def book(self, booking: Booking) -> None:
        if booking.start >= booking.end:
            raise ValueError("invalid range")
        existing = self._by_room.get(booking.room_id, [])
        for e in existing:
            if overlaps(booking.start, booking.end, e.start, e.end):
                raise RuntimeError("conflict")
        self._by_room.setdefault(booking.room_id, []).append(booking)
        for o in self._observers:
            o.on_booked(booking)

    def cancel(self, room_id: str, booking_id: str) -> None:
        rooms = self._by_room.get(room_id, [])
        for i, b in enumerate(rooms):
            if b.id == booking_id:
                rooms.pop(i)
                for o in self._observers:
                    o.on_cancelled(b)
                return
        raise KeyError(booking_id)
```

### Go

```go
type Booking struct {
    ID, RoomID string
    Start, End time.Time
    Attendees  []string
}

func Overlaps(aStart, aEnd, bStart, bEnd time.Time) bool {
    return aStart.Before(bEnd) && bStart.Before(aEnd)
}

type CalendarService struct {
    mu       sync.Mutex
    byRoom   map[string][]Booking
    observers []CalendarObserver
}

func (s *CalendarService) Book(b Booking) error {
    s.mu.Lock()
    defer s.mu.Unlock()
    if !b.Start.Before(b.End) {
        return fmt.Errorf("invalid range")
    }
    for _, e := range s.byRoom[b.RoomID] {
        if Overlaps(b.Start, b.End, e.Start, e.End) {
            return fmt.Errorf("conflict")
        }
    }
    s.byRoom[b.RoomID] = append(s.byRoom[b.RoomID], b)
    for _, o := range s.observers {
        o.OnBooked(b)
    }
    return nil
}
```

## Concurrency / consistency

- Two users book same slot: **per-room lock** or DB exclusion constraint / `WHERE NOT overlaps` transaction.
- Check-then-insert without lock → double booking.
- Recurring series: lock room for the whole expand+insert to avoid partial series.

## Tradeoffs / pitfalls

- Closed vs half-open intervals — be explicit (`10–11` and `11–12` OK).
- Time zones: store UTC, display local.
- Expanding infinite recurrence into memory — bound by query window.

## Interview prompts

- How do you detect overlap efficiently for many bookings? (interval tree / DB range types)
- Cancel one instance vs entire series?
- How do observers fail without rolling back the booking? (outbox)

## Exercise / follow-ups

1. Add weekly recurrence for N occurrences with conflict-all-or-nothing.
2. Query `agenda(room, from, to)`.
3. Replace linear scan with sorted intervals + binary search by start time.
