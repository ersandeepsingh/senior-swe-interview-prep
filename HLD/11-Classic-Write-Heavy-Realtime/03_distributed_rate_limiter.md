# Design a Distributed Rate Limiter 🟡

> **Crux:** Enforce limits across many API nodes using a **shared counter store** — token bucket / sliding window — with clear consistency vs latency trade-offs.

## Clarify (say this first)

**Functional**
- Limit by API key / user / IP / route; return 429 + `Retry-After`
- Algorithms: token bucket or sliding window (pick and defend)
- Different quotas per tier (free vs paid)
- Optional: soft limit vs hard; burst allowance

**Non-functional**
- Inline on request path — add minimal latency (p99 +1–5 ms ideal)
- Correct enough under contention; slight over-allow often OK
- Highly available — fail open vs fail closed policy
- Multi-region: local vs global limits

## Back-of-envelope

```text
Assumptions: 100K RPS through gateway; every request checks limiter
Redis ops: ~1–2 per check → 100–200K Redis cmds/s (cluster)
Keys: user_id + route → cardinality millions; TTL = window size
Hot keys: single API key at high RPS → shard or local+sync hybrid
```

## API + data model

```text
Middleware: allow(key, cost) → { allowed, remaining, reset_at }
Admin: PUT /limits/{tier} { rpm, burst }
```

| Concept | Storage |
|---------|---------|
| Token bucket | `key → { tokens, last_refill }` in Redis (Lua) |
| Sliding window | Redis ZSET of timestamps or window counters |
| Config | `route + tier → limit` in config service / local |

## High-level architecture

```text
Client → API Gateway / sidecar
              │
              ▼
        Rate limiter lib ──► Redis Cluster (shared counters)
              │
         allow? ──yes──► service
              └──no──► 429
```

## Deep dive: the crux

**Distributed counters:** all app nodes must share state or you under-enforce by N×.

| Approach | Pros | Cons | Pick when |
|----------|------|------|-----------|
| Redis + Lua atomic | Simple, fast enough | Redis = SPOF/hot key | Default interview |
| Local token bucket + sync | Ultra low latency | Temporary over-allow | Extreme QPS |
| Quorum / CRDT counters | Multi-region | Complexity; soft limits | Global caps |
| Envoy/gateway native | Central enforcement | Less app flexibility | Edge-first |

**Token bucket:** refill rate R, capacity B (burst). Lua: read-modify-write atomic. **Sliding window log:** accurate, heavier. **Fixed window:** simple, burst at boundary — mention and usually prefer bucket or sliding.

**Consistency:** slightly exceeding limit under race is usually fine (AP). For billing hard caps, accept higher latency or centralized limiter service.

**Fail policy:** fail **open** (availability) vs **closed** (protect backend) — say which and why (payments closed; marketing open).

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Central Redis | Accurate global limit | Extra hop; dependency |
| Local-only | Speed | N× over-allow |
| Fixed window | Simplicity | Boundary burst |
| Fail closed | Protects origin | Outage when Redis dies |

## Failure modes & scale

- **Redis down:** cached last decision short TTL; or fail open/closed per route
- **Hot key:** split key by shard suffix and sum (approximate); or dedicated limiter service with consistent hashing
- **Clock skew:** prefer Redis server time in Lua
- **Multi-region:** per-region limits + smaller global budget; or regional only
- **Cardinality explosion:** hash keys, TTLs on all counter keys

## Interview trigger phrase

> “I’d enforce a token bucket in Redis with an atomic Lua script so every gateway sees the same counters — I’d accept tiny over-allow under races, and explicitly choose fail-open or fail-closed per route when Redis is unavailable.”

## Exercise

1. Implement **sliding window** vs **token bucket** — when is the extra accuracy worth it?
2. How do you rate-limit a **single viral API key** doing 50K RPS without melting one Redis shard?
3. Design **per-tenant fair sharing** when one tenant would consume the whole cluster.
