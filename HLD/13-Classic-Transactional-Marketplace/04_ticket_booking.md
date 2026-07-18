# Design Ticket Booking (BookMyShow / Ticketmaster) 🔴

> **Crux:** **Concurrent seat inventory** under flash sales — two users must never get the same seat; use **holds + strong consistency** on the hot rows.

## Clarify (say this first)

**Functional**
- Browse events, select seats/zones, pay, issue tickets
- Soft hold (timer) then confirm on payment
- Cancel/refund rules; waitlist optional

**Non-functional**
- **CP on seat assignment**; availability reads can be slightly stale
- Extreme spikes at on-sale (100k+ users for one event)
- Hold TTL must be reliable (expire → release)
- Fairness / anti-bot (scope mention)

## Back-of-envelope

- 10k seats × on-sale → tiny data, huge contention on few rows/partitions
- Read QPS for seat maps >> write QPS; cache seat map with careful invalidation
- Payment latency 1–5s → holds must cover that window
- Hot event = single-partition bottleneck by design — plan for it

## API + data model

```text
GET  /events/{id}/seating
POST /holds                 # seat_ids[] → hold_id, expires_at
POST /orders                # hold_id + payment → confirm
POST /holds/{id}/release
GET  /orders/{id}/tickets
```

| Entity | Key fields |
|--------|------------|
| Event | id, venue, starts_at |
| Seat | event_id, seat_id, status (FREE/HELD/SOLD), hold_id, version |
| Hold | id, user_id, seats[], expires_at |
| Order | id, hold_id, payment_id, tickets[] |

## High-level architecture

```text
Client ──► Gateway ──► Booking Svc
                          │
              ┌───────────┼────────────┐
              ▼           ▼            ▼
         Seat Map     Inventory     Payment
         Cache        DB (CP)       Svc
                          │
                     Hold Expiry Worker
```

## Deep dive: the crux

**Hold then pay**
1. Transaction: set seats FREE→HELD iff still FREE (optimistic version / `UPDATE … WHERE status='FREE'`).
2. Start TTL (e.g. 10 min); return hold_id.
3. Payment success → HELD→SOLD in one txn; issue tickets.
4. Expiry worker / bucketed TTL → HELD→FREE if still same hold_id.

| Alternative | When to pick |
|-------------|--------------|
| Pessimistic row locks for whole checkout | Small venue, simple |
| Soft hold + conditional updates | Default (**best interview answer**) |
| GA (general admission) counters | No reserved seats — atomic decrement |
| Queue / virtual waiting room | Extreme on-sale fairness before booking |

**Avoid:** long DB transactions spanning payment PSP calls.

**Seat map reads:** cache OK; on hold/sell, invalidate event_id map or version stamp so UI refreshes.

**GA zones:** one atomic counter per zone beats per-seat rows when seats are fungible — still use holds so payment window doesn't oversell.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Soft holds | Time to pay | Temporary inventory lockout |
| Long hold TTL | Better convert | More speculative lock |
| Strong seat CP | No double book | Lower availability if DB partition |
| Waiting room | Smooth spike | Extra product complexity |

## Failure modes & scale

- Pay success + confirm crash → idempotent confirm by hold_id; reconcile with PSP
- Clock skew on TTL → central expiry or absolute expires_at checked in txn
- Bot sniping → rate limit, device attestation, queue
- Hot event → shard by event_id (one event one primary); vertical scale inventory store; GA zones as counters
- Cache shows FREE but hold fails → expected; UI retries with fresh map

## Interview trigger phrase

> “I never hold a DB lock across payment — I **atomically soft-hold seats with a TTL**, confirm to SOLD on payment success, and release with conditional updates so double-booking is impossible.”

## Exercise

1. Two users click the same seat at once — exact SQL/CAS semantics and responses.
2. Payment succeeds but `confirm` never runs — how do you heal without releasing a paid seat?
3. When do you choose GA counters vs per-seat rows?
