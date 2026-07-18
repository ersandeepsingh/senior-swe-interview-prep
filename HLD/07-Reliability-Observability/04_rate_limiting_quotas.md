# Rate Limiting & Quotas

> **Rate limits** protect the system; **quotas** enforce **per-tenant fairness** so one customer can’t starve everyone. (Edge throttling overlaps networking — here focus on **multi-tenant quotas** and fairness.)

## Plain English

Abuse protection and SaaS product limits are related but not identical. Networking rate limits (CDN/WAF) stop bots; **quotas** encode plan entitlements and noisy-neighbor isolation.

| Concept | Meaning |
|---------|---------|
| **Rate limit** | Max requests / tokens per window (IP, user, API key) |
| **Quota** | Longer-horizon budget (e.g. 1M API calls / month, 10k QPS reserved) |
| **Fairness** | Noisy neighbor isolation; weighted shares |

Algorithms (brief): **token bucket** (burst + steady rate), sliding window, leaky bucket — pick one and move to **where** you enforce (gateway vs service vs data plane).

```text
  Tenant A ──┐
  Tenant B ──┼──► API Gateway          ┌─ A: 1000 rps, 10M/mo
  Tenant C ──┘    quota + rate check ──┤─ B: 100 rps, 1M/mo
                     │                 └─ C: burst 50, fair queue
                     ▼
                   Backend
              (bulkhead per tenant optional)
```

## Simple example

SaaS analytics API: free tier 10 rps / 100k rows scanned; enterprise 2k rps. Without quotas, a free crawler saturates DB and enterprise p99 dies. Gateway returns **429** with `Retry-After`; billing service tracks monthly quota separately from burst rate.

```text
  Check order (typical):
    1) auth → tenant id
    2) monthly quota remaining?
    3) burst rate limit (Redis token bucket)
    4) expensive op units (ES shard cost / LLM tokens)
```

Overlap with networking rate limit: same algorithms at CDN/WAF for abuse; **quotas** are product/billing-aware and often stored in Redis + durable counters.

## Why prefer one over the other

| Prefer **global rate limit** when… | Prefer **per-tenant quota** when… |
|------------------------------------|-----------------------------------|
| Protecting shared infra from abuse | Multi-tenant SaaS / API products |
| Single app, few users classes | Contractual limits, billing tiers |
| Simple IP/user throttle enough | Need fairness + overage policy |

**Soft vs hard quota:** soft = warn / throttle; hard = reject. Enterprise often wants reserved capacity (bulkhead), not only best-effort limits.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Strict per-tenant caps | Fairness, predictable cost | Complexity; false 429s |
| Shared pool only | Simpler | Noisy neighbor |
| Central Redis counters | Accurate global limits | Extra dependency; race windows |
| Limit only at edge | Easy | Internal fan-out bypasses cost control |

**Trap:** Only limiting HTTP QPS while expensive **fan-out** internal calls bypass quotas. Enforce at the **costly** resource (DB query units, LLM tokens), not just request count.

**Fair queuing:** under overload, weighted fair share per tenant beats FIFO — one elephant request shouldn’t block a hundred mice.

**Distributed counters:** Redis `INCR` + TTL windows are the usual interview implementation; mention clock skew and multi-region approximate limits if global.

## Interview trigger phrase

> “I’d enforce **per-tenant rate limits and monthly quotas** at the gateway, with heavier limits on expensive operations — so one tenant can’t burn the shared DB budget.”

## Exercise

**Multi-tenant “search API” shared Elasticsearch cluster.**

1. What do you limit besides QPS (e.g. query complexity / shard fan-out)?
2. How do free vs paid tenants differ in limit + fairness?
3. One sentence on 429 vs degrading to approximate results.
