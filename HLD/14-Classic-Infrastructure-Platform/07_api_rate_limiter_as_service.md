# Design an API Rate Limiter as a Service 🟡

> **Crux:** Enforce **central quotas across a fleet** with correct **distributed counting** — local token buckets alone can’t enforce a global limit.

## Clarify (say this first)

**Functional**
- Limits per API key / user / IP / endpoint
- Algorithms: token bucket / sliding window / fixed window
- Sync reject (`429`) vs soft throttle
- Admin CRUD for policies; burst vs sustained

**Non-functional**
- p99 decision ≪ app SLA (sub-ms–few ms)
- Accurate enough (± small error OK often)
- Multi-region: local vs global quotas
- Survive Redis blip without opening floodgates (fail closed/open policy)

## Back-of-envelope

```text
App: 500k QPS behind gateway → rate-limiter QPS ≈ same
100k API keys; hot key 10k QPS alone
Redis: INCR / Lua ≈ 50–100k+ ops/s per shard → shard by key
Sliding window log: heavy memory; prefer window counters / token bucket
```

## API + data model

```text
POST /v1/check  {tenant, key, cost=1} → {allow, remaining, reset_at}
POST /v1/policies  {key_pattern, limit, window, burst}
```

| Entity | Fields |
|--------|--------|
| Policy | `id`, `selector`, `limit`, `window`, `algo` |
| Counter | `key`, `tokens`/`counts`, `window_start` |

## High-level architecture

```text
  Edge / API Gateway
         │
         ▼
  Rate Limit Service (stateless)
         │  Lua / pipelined ops
         ▼
  Redis cluster (sharded by rate-limit key)
         │
         └── optional: local cache of policy config
```

## Deep dive: the crux

**Distributed counting:**
| Approach | Accuracy | Cost | When |
|----------|----------|------|------|
| **Central Redis + Lua token bucket** | High | Extra hop | Default SaaS limiter |
| **Fixed/sliding window counters** | Good | Simple INCR+TTL | Quotas per minute/day |
| **Local only** | Weak globally | Fast | Coarse protection / shed |
| **Local + async sync** | Approximate | Soft global | Ultra-low latency edge |
| **Gossip / CL-counters** | Approx | Complex | Multi-region soft limits |

**Pick:** Redis cluster, key=`{tenant}:{route}:{window}`, **atomic Lua** for take-token; fixed window for simplicity or sliding window counter for smoother limits. Multi-region: **regional limits** + smaller global budget, or sticky region.

**Fairness:** separate burst vs sustained; optional priority lanes so health checks / admin APIs aren’t starved by one noisy tenant.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Central store | True global cap | Latency + dependency |
| Fixed window | Simple | Boundary burst (2× at edge) |
| Sliding / token bucket | Smoother | Slightly more logic |
| Fail open | Availability | Abuse during outage |
| Fail closed | Safety | False 429s on Redis blip |
| Approximate local | Latency | Over/under enforce |

## Failure modes & scale

- **Redis hotspot:** one tenant dominates — isolate key; dedicated shard
- **Clock skew:** window boundaries wrong — use Redis time
- **Gateway bypass:** enforce at every entry (edge + service mesh)
- **Config lag:** stale higher limits — version policies; short cache TTL
- **Scale:** shard counters; read replicas don’t help writes — scale primary shards

## Interview trigger phrase

> “Local buckets can’t enforce a **fleet-wide** quota — I’d keep **atomic counters in Redis** (token bucket via Lua), shard by limit key, and decide **fail-open vs fail-closed** explicitly when Redis is down.”

## Exercise

1. Fixed 100 req/min — show the double-spend at window boundary; how does sliding window help?  
2. Two regions each allow 1000 QPS local — how do you cap 1200 global without a cross-region lock on every request?  
3. Redis p99 spikes to 20 ms — where do you shed and what do users see?
