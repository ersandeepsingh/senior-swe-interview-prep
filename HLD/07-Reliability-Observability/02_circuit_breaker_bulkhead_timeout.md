# Circuit Breaker, Bulkhead & Timeout

> Retries without bounds **amplify** outages. **Timeouts** bound waits; **circuit breakers** stop calling a sick dependency; **bulkheads** isolate pools so one failure doesn’t sink the ship.

## Plain English

Cascading failure pattern: slow dependency → threads pile up → caller times out → callers of the caller pile up → whole site down. These three patterns **contain blast radius**.

| Pattern | One-liner |
|---------|-----------|
| **Timeout** | Don’t wait forever; fail fast |
| **Circuit breaker** | After enough failures → open (fail fast); half-open probe; closed = normal |
| **Bulkhead** | Separate thread/connection pools / queues per dependency or tenant |

```text
  API ──► Payment client
              │
         ┌────┴────┐
         │ Breaker │── open ──► return fallback / 503
         └────┬────┘
              │ closed
              ▼
         Payment SVC (slow)
              │
         bulkhead: max 50 conns
         (search pool separate)
```

**Breaker states:** Closed (normal) → Open (trip) → Half-open (trial requests) → Closed or Open again.

## Simple example

Feed service calls Ranker + Ads + Social-graph.

Ranker p99 blows up → without protection, feed threads pile up → whole feed 5xx.

```text
  With protection:
    timeout Ranker @ 100ms
    breaker opens at 50% errors
    bulkhead: Ranker pool ≠ Ads pool
    fallback: chronological feed from cache
    Ads still served ✓
```

**Retries:** only with jittered backoff + idempotency + **retry budget** (e.g. max 10% of traffic). Never retry storms on non-idempotent POSTs.

## Why prefer one over the other

| Prefer **breaker + timeout** when… | Prefer **bulkhead** when… |
|------------------------------------|---------------------------|
| Dependency is flaky / overloaded | One tenant or dep can starve others |
| You have a fallback | Shared thread pool today |
| Fail-fast better than queue forever | Need isolation of resources |

Libraries / systems: Resilience4j, Hystrix (legacy), Envoy outlier detection, concurrency limits.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Aggressive timeout | Protect caller latency | More false failures |
| Open circuit | Stop cascade | Temporary hard fail / fallback UX |
| Tight bulkhead limits | Isolation | Under-utilized capacity |
| Heavy retries | Survive blips | Amplify outages if mis-tuned |

**Trap:** “We’ll add retries” as the whole resilience story. Seniors name **timeout → retry budget → breaker → bulkhead → fallback**.

**Timeout stacking:** gateway 3s, service 2s, dependency 1s — set inner timeouts shorter than outer or you’ll get useless retries on already-dead requests.

**Adaptive concurrency limits** (TCP-BBR inspired / queue-based) are a modern cousin of bulkheads when thread pools are hard to size.

## Interview trigger phrase

> “Every outbound call gets a **timeout**, a **retry budget**, and a **circuit breaker**; pools are **bulkheaded** so a sick Ranker can’t exhaust the Feed’s threads.”

## Exercise

**Feed depends on Ranker and Ad service.**

1. Sketch breaker states when Ranker error rate hits 60%.
2. Why separate connection pools for Ranker vs Ads?
3. One sentence: what the client sees when the Ranker circuit is open.
