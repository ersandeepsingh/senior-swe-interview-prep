# Rate Limiting

> **Rate limiting** caps how many requests a client/key may send per window so one noisy neighbor (or bot) doesn’t starve everyone. Classic algorithms: **token bucket** and **sliding window**.

## Plain English

| Algorithm | Intuition | Behavior |
|-----------|-----------|----------|
| **Token bucket** | Tokens refill at rate R; each request spends 1 | Allows **bursts** up to bucket size, then steady rate |
| **Fixed window** | Counter resets every N seconds | Simple; bursty at window edges (2× spike) |
| **Sliding window** | Count events in last N seconds (log or approx) | Smoother than fixed window; more state |
| **Leaky bucket** | Queue drains at fixed rate | Smooths bursts; adds latency / drops when full |

Where to enforce: **edge / gateway** (per API key, IP) and sometimes **per service** (protect DB).

```text
  Client ──► Gateway rate limiter ──allow──► Service
                    │
                 deny (429)
                    │
                    ▼
              Retry-After / error body
```

## Simple example

**Public SMS OTP API:** 5 sends / phone / hour, burst of 2.

```text
  Token bucket per phone:
    capacity = 2          (burst)
    refill   = 5/hour     (~1 token / 12 min)

  t=0  send OK (tokens 1)
  t=1s send OK (tokens 0)
  t=2s send → 429
  later tokens refill → allow again
```

Login endpoint: sliding window **20 req / IP / minute** to blunt credential stuffing without punishing a short double-click burst as harshly as a tiny fixed window.

## Why prefer one over the other

| Prefer **token bucket** when… | Prefer **sliding window** when… |
|-------------------------------|----------------------------------|
| You want controlled bursts (mobile retries) | You need fair “last N seconds” caps |
| Gateways already implement it (Envoy, nginx) | Abuse is “just under” fixed-window edges |
| UX tolerates short bursts | Compliance / billing needs smoother quotas |

| Limit at **gateway** | Limit at **service** |
|----------------------|----------------------|
| Cheap early reject | Protects specific expensive RPCs |
| One policy for public API | Catches internal fan-out / mesh traffic |

**Not “rate limit = backpressure.”** Rate limit is *policy* on a key. Backpressure is *system overload* response (see load shedding).

### Identity of the limit key

| Key | Good for | Weak against |
|-----|----------|--------------|
| IP | Anonymous abuse | NAT / shared campus IPs |
| User / API key | Fair multi-tenant quotas | Stolen keys (still need revoke) |
| Route + key | Protect expensive RPCs only | More config to maintain |

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Token bucket | Burst-friendly UX | Need to tune capacity vs refill carefully |
| Fixed window | Trivial counters | Edge spikes; easier to game |
| Sliding log | Accurate | Memory for timestamps at high QPS |
| Distributed Redis counters | Cluster-wide limits | Extra hop; clock/skew & failure modes |
| 429 + Retry-After | Clients can behave | Bad clients ignore; still need shed |

## Interview trigger phrase

> “I’d rate-limit at the **API gateway** with a **token bucket** per API key for bursty mobile clients, and a **sliding window** on login by IP — returning **429** with Retry-After before the DB feels the abuse.”

## Exercise

**Protect a ticket-booking “reserve seat” API.**

1. Pick algorithm and key (user vs IP vs SKU) for anonymous browse vs authenticated reserve — why different?  
2. Show how fixed window can allow ~2× limit at a boundary; how does sliding window change that?  
3. Redis rate-limiter blips for 2 seconds — fail open or fail closed, and what do you tell the interviewer?
