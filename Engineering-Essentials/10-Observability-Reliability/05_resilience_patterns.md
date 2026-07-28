# Resilience Patterns

> Assume networks and dependencies **fail**. Timeouts, retries, circuit breakers, and bulkheads stop a small blip from becoming a site-wide outage.

## Plain English

Dependencies will time out, flap, and overload. Resilience patterns contain blast radius so one sick payment provider doesn't take down the whole site.

```text
  Call payment:
    timeout 2s
    on timeout/5xx → retry up to 3x with exponential backoff + jitter
    if failure rate high → circuit OPEN → fail fast / degrade
    use separate connection pool (bulkhead) so inventory still works
```

**Retries without jitter** = thundering herd. **Retries without timeouts** = pile-up. **Retries on non-idempotent POSTs** = double charges.

## Essentials (must-know for this topic)

### Pattern one-liners

| Pattern | Idea in one line |
|---------|------------------|
| **Timeout** | Don't wait forever; fail fast and free the thread/connection |
| **Retry + backoff + jitter** | Transient failures may succeed later; space attempts; randomize to avoid stampede |
| **Circuit breaker** | After enough failures, **stop calling** for a while; probe later (open → half-open → closed) |
| **Bulkhead** | Isolate pools (threads/connections) so one dependency can't exhaust everything |
| **Fallback / degrade** | Return cached/default/partial UX when the dependency is unavailable |
| **Idempotent retries** | Safe to retry only if the operation can be repeated without double effects |

### Circuit breaker states

| State | Behavior |
|-------|----------|
| **Closed** | Calls flow normally; track failures |
| **Open** | Fail fast — don't call the dependency |
| **Half-open** | Allow a probe; success → closed, fail → open again |

### Retry rules of thumb

| Do | Don't |
|----|-------|
| Retry **transient** errors (503, timeouts, network) | Retry **400 / 401 / 403** (won't help) |
| Exponential backoff **+ jitter** | Fixed synchronized retries (thundering herd) |
| One responsible retry layer | Client + gateway + service all retrying |
| Pair with timeouts + idempotency | Retry forever with no deadline |

## Simple example

Payment client:

1. Timeout 2s per attempt.
2. Retry on `503` / network error only (not on `400` validation).
3. Backoff: 100ms, 200ms, 400ms + random jitter.
4. Circuit: open after 50% failures in a 30s window; half-open after 30s with one probe.
5. Bulkhead: max 50 concurrent payment calls; rest get fast fail or queue with limit.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Aggressive retries | Mask blips | Amplify load on a sick dependency |
| Short timeouts | Protect callers | False failures on slow paths |
| Circuit breaker | Fail fast, recover capacity | Temporary hard fail even if some calls would work |
| Shared thread pool | Simpler | One slow dep starves others |

## Pitfalls

- **Retry storms** — every layer retries (client + gateway + service) → exponential load. Prefer **one** responsible retryer.
- **Retrying non-idempotent writes** without idempotency keys.
- **Infinite waits** with no deadline on the whole operation.
- **Circuit breaker with no degraded path** — users just see errors; pair with fallbacks.

## Interview trigger phrase

> “I'd set **timeouts everywhere**, retry only **transient + idempotent** calls with **backoff and jitter**, and wrap flaky deps in a **circuit breaker + bulkhead** so failures stay contained.”

## Exercise

Cart → Inventory → Warehouse API. Warehouse is flapping 20% errors. Where do you put the circuit breaker, and what do you return to the user when it's open?
