# Rate Limiting Algorithms

> Protect systems (and fair users) by capping how fast clients can call you. Algorithms differ in **burstiness**, **smoothness**, and **implementation cost**.

## Plain English

Where to enforce: API gateway, service middleware, Redis counters for distributed limits, or local token buckets per instance (approximate). Return `429` with `Retry-After`.

```text
  Token bucket (rate 10/s, burst 50):
    Idle → fills to 50 tokens
    Burst of 50 allowed immediately
    Then sustained ≤ 10/s

  Fixed window (100/min):
    100 at 00:00.9 and 100 at 00:01.0 → 200 in 200ms  ← edge burst
```

## Essentials (must-know for this topic)

### Algorithm comparison

| Algorithm | Idea | Burst? |
|-----------|------|--------|
| **Fixed window** | Count per wall-clock window (e.g. each minute) | Yes — spike at window edge |
| **Sliding window log** | Store timestamps; count in last N seconds | Accurate; memory heavy |
| **Sliding window counter** | Weighted previous + current window | Good middle ground |
| **Token bucket** | Bucket holds tokens; refill at rate R; request spends a token | Yes — up to bucket size |
| **Leaky bucket** | Queue/drain at fixed rate (smooth outbound) | Smooths bursts (may delay/drop) |

### Token vs leaky vs sliding (interview focus)

| | Token bucket | Leaky bucket | Sliding window |
|---|--------------|--------------|----------------|
| Burst | Allowed up to capacity | Discouraged / queued | Depends on variant |
| Feel | Sustained rate + controlled burst | Smooth constant drain | More accurate fairness |
| Common use | **API quotas** | Traffic shaping | Precise per-user limits |
| Cost | Simple; Redis/Lua for global | Queue management | Log = memory; counter ≈ cheaper |

### Distributed enforcement

| Approach | Risk |
|----------|------|
| Per-instance only | N pods ⇒ **N×** effective limit |
| Redis / shared store | True global cap; extra latency + dependency |
| Separate limits for expensive routes | `/search` vs `/health` shouldn't share one bucket |

## Simple example

Public API: **100 requests / minute / API key**, allow short bursts.

- Use **token bucket**: refill \(100/60\) tokens per second, capacity 20–100 depending on product.
- Return `429` with `Retry-After`.
- Store counters in Redis: `INCR` + `EXPIRE`, or Lua for token bucket atomicity.

For login endpoints: stricter limits + backoff to slow credential stuffing (often separate from general API quotas).

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Token bucket | Simple burst + sustained rate | Need careful distributed sync |
| Fixed window | Trivial to implement | Boundary burst unfairness |
| Sliding log | Precise | Memory / CPU at high QPS |
| Per-instance limit only | No Redis | N instances ⇒ N× limit |
| Global Redis limit | True global cap | Extra latency + Redis dependency |

## Pitfalls

- **Only rate limiting by IP** behind NAT — whole offices share one IP.
- **No separate limits** for expensive endpoints (`/search`) vs cheap (`/health`).
- **Silent drops** without `429` / headers — clients can't back off.
- **Limits that don't match idempotent retries** — clients retry into more 429s; teach jittered backoff.
- **Leaky vs token confusion** in interviews — know burst vs smooth.

## Interview trigger phrase

> “I'd use a **token bucket** for API quotas — sustained rate plus controlled burst — enforced at the gateway with Redis for global fairness, returning **429 + Retry-After**.”

## Exercise

You need 10 rps sustained and burst of 50 per user, globally across 8 gateway pods. Which algorithm and where do you store state? What goes wrong if state is only local to each pod?
