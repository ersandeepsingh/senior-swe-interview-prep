# Design Food Delivery (Swiggy / DoorDash) 🔴

> **Crux:** Triangulate **restaurant prep + courier matching + live order state** — three parties, one SLA, real-time tracking under messy real-world delays.

## Clarify (say this first)

**Functional**
- Browse menus, place order, pay, restaurant accept/prep, courier pickup/drop
- Live map tracking; ratings; cancellations / refunds
- Batching / multi-order courier optional

**Non-functional**
- Order state strongly consistent for the order object (who's responsible now)
- Location of courier: fresh, eventually consistent OK
- Peak lunch/dinner 10×; regional failure isolation
- Matching quality: ETA accuracy > raw assign speed

## Back-of-envelope

- 5M orders/day → ~60 OPS avg; peaks ~600–1000 OPS in a city cluster
- Courier location: similar firehose to rides but denser urban cells
- Menu/catalog read-heavy → cache/CDN; order path write-heavy transactional
- Hot restaurants: queueing at kitchen becomes bottleneck (product + system)

## API + data model

```text
GET  /restaurants?lat=&lng=
POST /orders
POST /orders/{id}/restaurant/accept|reject
POST /orders/{id}/courier/assign|pickup|deliver
GET  /orders/{id}/track          # WS
```

| Entity | Key fields |
|--------|------------|
| Restaurant | id, geo, hours, prep_time_est |
| MenuItem | id, restaurant_id, price, availability |
| Order | id, items[], state, restaurant_id, courier_id, ETAs |
| Courier | id, status, location, capacity |
| Assignment | order_id, courier_id, score, expires_at |

Order state machine: PLACED → RESTAURANT_ACCEPTED → PREP → READY → PICKED_UP → DELIVERED / CANCELLED.

## High-level architecture

```text
Customer ──► Order Svc ──► Order DB (state)
                │
                ├──► Payment
                ├──► Restaurant WS / app
                └──► Dispatch Svc ◄── Courier locations (geo index)
                         │
                         └──► Assign / reassign ──► Tracking ──► Customer
```

## Deep dive: the crux

**Matching (dispatch)**
- Not only “nearest courier”: consider restaurant ready time, courier route, batching, zone.
- Strategies: assign early (may wait at restaurant) vs assign when READY (may delay pickup).
- **Pick when:** predictive assign if prep_time reliable; late assign if kitchens unpredictable.

**Real-time state**
- Single order aggregate with version; push events on transition.
- Courier GPS → ETA service updates customer view without rewriting order truth.

| Alternative | When to pick |
|-------------|--------------|
| Nearest-idle courier only | MVP |
| ETA-aware + ready-time coupling | Default production |
| Continuous optimization / batching | Dense cities, efficiency KPI |
| Human dispatcher override | Edge / VIP / outages |

**Inventory of menu items:** eventual OK with restaurant truth; oversell handled by restaurant reject.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Early courier assign | Lower pickup delay | Courier idle at restaurant |
| Assign at READY | Less idle | Higher late delivery risk |
| Multi-order batching | Efficiency | ETA complexity / UX |
| Strong order state | Clear ownership | Need careful retries/idempotency |

## Failure modes & scale

- Restaurant never accepts → timeout + cancel/refund saga
- Courier cancel mid-route → re-dispatch; preserve order version
- Storm / zone close → pause matching; degrade to longer ETA messaging
- Hot geo cells → shard dispatch by city/hex
- Scale: city-first deployment; catalog cache; order DB shard by city_id or order_id

## Interview trigger phrase

> “I'd model a strict **order state machine**, stream courier locations separately, and run **dispatch** that optimizes for ready-time + ETA — not just nearest pin on the map.”

## Exercise

1. Draw the state machine and which actor can trigger each transition.
2. Kitchen is 15 minutes late — how do matching and customer ETA update?
3. Design re-dispatch when the courier's bike breaks after pickup.
