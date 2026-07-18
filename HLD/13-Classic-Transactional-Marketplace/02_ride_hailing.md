# Design Ride-Hailing (Uber / Lyft) 🔴

> **Crux:** **Geospatial matching** of riders to nearby drivers using **fresh location streams** — ETA and dispatch quality live or die on location freshness + index design.

## Clarify (say this first)

**Functional**
- Request ride, match driver, track trip, fare, cancel, ratings
- Driver app: go online, accept/reject, navigate
- Surge pricing (scope lightly); multi-modal optional

**Non-functional**
- Location update high QPS; map freshness < few seconds
- Match latency: seconds; trip tracking: near real-time
- Availability over perfect consistency for locations (AP/EL OK)
- Dispatch decision should avoid double-assigning one driver (**stronger** on trip assignment)

## Back-of-envelope

- 1M drivers online × 1 location update / 4s → **250k writes/s** to location path
- Match QPS: city-peak thousands/sec; each query scans radius
- Location store must be memory-heavy geo index, not OLTP primary for every ping
- Trip state transitions: low QPS vs location firehose

## API + data model

```text
POST /trips                     # pickup, dropoff, product
POST /drivers/location          # lat, lng, heading, ts (batch OK)
POST /trips/{id}/accept|arrive|complete|cancel
GET  /trips/{id}/track          # WS/SSE preferred
```

| Entity | Key fields |
|--------|------------|
| Driver | id, status (offline/idle/busy), vehicle |
| Location | driver_id, geohash, lat, lng, ts, speed |
| Trip | id, rider, driver, state machine, pickup, fare |
| MatchOffer | trip_id, driver_id, expires_at |

## High-level architecture

```text
Driver apps ──location──► Ingest ──► Redis/Quadtree/Geohash index
                                      │
Rider ──► Trip Svc ──► Matcher ◄──────┘
              │            │
              │            └──► Offer to driver (push)
              ▼
         Trip State DB ──► Tracking WS ──► Rider/Driver
              │
              └──► Pricing / Payments (async)
```

## Deep dive: the crux

**Location**
- Update path: UDP/HTTP batch → hot in-memory store keyed by **geohash / H3 / quadtree**.
- TTL stale drivers out; don't match on locations older than N seconds.

**Matching**
1. Rider request → cell + ring neighbors → candidate idle drivers.
2. Rank: ETA, rating, idle time, directionality.
3. Offer one (or small batch) with timeout; on accept, **CAS** driver status idle→busy + create trip.
4. On fail/timeout, next candidate.

| Alternative | When to pick |
|-------------|--------------|
| SQL `ORDER BY distance` | Tiny city / prototype |
| Geohash rings + in-memory index | Default city-scale |
| Partition by city/hex + local matchers | Multi-city / global |
| Batch auction / optimization | Marketplace efficiency research |

**Double assign:** conditional update on driver row / lock trip_id; only one offer wins.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Eventual location | Scale & latency | Occasional stale ETAs |
| Exclusive offer | Simpler UX | Higher match latency |
| Concurrent offers | Faster fill | More cancel/reject churn |
| City-sharded matchers | Scale | Cross-boundary edge cases |

## Failure modes & scale

- Ghost drivers (app killed) → heartbeat TTL; rider re-match
- Matcher hotspot downtown → finer H3 resolution; shard by cell
- Network partition: locations AP; **assignment CP** in region
- Surge / events → pre-scale matchers; degrade to larger radius
- Scale: separate location cluster from trip OLTP; Kafka for trip events

## Interview trigger phrase

> “Location is an **AP geo-index** with aggressive TTLs; matching queries H3 rings and **atomically claims** a driver so we never double-dispatch.”

## Exercise

1. Compare geohash ring search vs quadtree for “drivers within 2 km.”
2. Two riders request the same driver in the same millisecond — how does only one win?
3. What do you show the rider if the driver's GPS stalls for 30 seconds mid-trip?
