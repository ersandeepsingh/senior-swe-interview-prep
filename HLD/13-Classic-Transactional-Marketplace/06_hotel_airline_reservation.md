# Design Hotel / Airline Reservation 🔴

> **Crux:** **Concurrent booking** on scarce inventory (room-nights / seats) — availability search can be stale; **confirm must be strongly consistent**.

## Clarify (say this first)

**Functional**
- Search availability by dates/route, quote price, book, pay, cancel/change
- Inventory: hotel rooms by type/date; airline seats by flight/cabin/fare class
- Overbooking policy (airlines often intentional — state assumption)

**Non-functional**
- Search: high QPS, eventual OK
- Booking: no double sell of same physical inventory (unless overbook policy)
- Holds during payment; GDS/supplier latency if external
- Multi-city / connecting flights increase combinatorial search cost

## Back-of-envelope

- Search:read >> book:write (100:1 or more)
- Hot flights/hotels: contention on few inventory keys
- Date-range hotel query touches many room-night rows — need efficient availability index
- Airline: inventory by fare class buckets often, not always every seat map until later

## API + data model

```text
GET  /availability?…          # hotel dates / flight O&D
POST /quotes                  # price lock / fare rules
POST /holds                   # temporary inventory hold
POST /bookings                # confirm + pay
POST /bookings/{id}/cancel
```

| Entity | Key fields |
|--------|------------|
| Property / Flight | id, attrs |
| InventoryUnit | key (room_type+date or flight+class), available, held, sold |
| Hold | id, units[], expires_at, price_snapshot |
| Booking | id, PNR, status, passengers, fare |

## High-level architecture

```text
Client ──► Search Svc ──► Availability Index (cache / ES / columnar)
                │
                └──► Booking Svc ──► Inventory DB (strong)
                          │
                          ├──► Pricing / Rules
                          ├──► Payment
                          └──► Supplier / GDS adapter (optional)
```

## Deep dive: the crux

**Availability vs booking**
- Search hits **denormalized availability** (updated async from inventory).
- Book path: **conditional decrement / hold** on source-of-truth inventory.

**Hotel room-nights**
- Key = `property_id + room_type + date`; booking N nights = txn across N keys (or pre-aggregated contiguous availability).
- Prefer: check all nights free → hold all → pay → sell; else fail atomically.

**Airline**
- Often **bucket counts** per fare class; seat map assignment later.
- Overbooking: sell > physical seats; deny-board process is business logic.

| Alternative | When to pick |
|-------------|--------------|
| Per-seat locks | Small venue / detailed seat selection |
| Fare-class counters + later seat assign | Airlines default |
| Soft hold + TTL | Any paid booking flow |
| External GDS as SoT | OTA aggregating suppliers |

**Distributed txn:** if inventory + payment + supplier — use hold + confirm saga, not 2PC across PSP.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Stale search cache | Fast browse | “Available” then book fails |
| Long price/hold lock | Better conversion | Inventory blockage |
| Intentional overbook | Yield | Customer pain / compensation |
| Atomic multi-night hold | Correct stays | Harder sharding across dates |

## Failure modes & scale

- Book fails after pay → auto-refund saga; never leave orphan charge
- Supplier confirm fails → release hold; compensate
- Hot hotel weekend → single inventory partition for property; queue
- Cache says 1 left, SoT 0 → expected UX; refresh search
- Scale: shard by property_id / flight_id; search tier separate from booking tier

## Interview trigger phrase

> “Search can be **eventually consistent**; booking does an **atomic hold with TTL** on inventory keys, then confirms after payment — I'd rather fail the book than double-sell the room-night.”

## Exercise

1. Model a 3-night hotel hold across date keys in one transaction — failure if night 2 is taken.
2. Airline overbooking: where in the state machine do you exceed physical seats?
3. OTA with supplier timeout mid-book — saga steps and user-visible states.
