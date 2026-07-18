# Backpressure & Load Shedding

> Under overload, **backpressure** slows producers when consumers can’t keep up; **load shedding** **drops** (or rejects) work so the system stays alive for a subset of traffic instead of melting down for everyone.

## Plain English

| Idea | Meaning | User-facing feel |
|------|---------|------------------|
| **Backpressure** | Propagate “slow down” upstream (queue bounds, TCP window, 503 + retry) | Requests wait or clients retry later |
| **Load shedding** | Deliberately refuse excess work | Some get errors; survivors stay fast |
| **Queue unbounded** | Accept everything into memory | Then OOM / GC death spiral |
| **Degradation** | Serve cheaper paths (cached, read-only) | Partial feature loss beats total outage |

Senior instinct: **fail a fraction early** rather than make *all* requests time out.

```text
  Normal:     Client → API → workers → OK

  Overload without shed:
  Client → API → unbounded queue → timeouts everywhere 💥

  Overload with shed:
  Client → API ──► queue full?
              │         │
              │        yes → 503 / drop low priority
              │         │
              └─no──► workers (healthy latency)
```

## Simple example

**Food-delivery order API** at dinner surge:

```text
  Priority tiers at gateway / service:
    P0  place order / pay     → never shed first
    P1  track order           → shed after P2
    P2  restaurant browse     → shed first (or serve CDN/cache only)

  Worker pool saturated:
    - Bounded queue (e.g. 1k)
    - New browse → 503 + Retry-After
    - Place-order still admitted
```

Clients of browse see errors; checkout keeps succeeding. Without shedding, checkout p99 explodes too.

## Why prefer one over the other

| Prefer **backpressure** when… | Prefer **load shedding** when… |
|-------------------------------|--------------------------------|
| Callers can slow down (internal RPC, queues) | External clients won’t stop (open internet) |
| You have bounded buffers & timeouts | Queue is already full; must protect core latency |
| Smooth pipelines (stream processing) | Spike would otherwise take down critical path |

| Shed **browse / analytics** first | Never shed **pay / auth** first |
|-----------------------------------|----------------------------------|
| Cheap to retry / degrade | Wrong drop = lost revenue / lockouts |

**Not “add a bigger queue.”** A bigger queue turns a short outage into a long one (latency death).

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Bounded queues + 503 | Predictable latency under load | Some rejected requests |
| Priority shedding | Protect revenue paths | Complexity; fairness debates |
| Client retries without jitter | Apparent resilience | Retry storms amplify overload |
| Auto-scale only | More capacity eventually | Scale lag; still need shed during ramp |

## Interview trigger phrase

> “Under overload I’d **bound queues and shed low-priority traffic first** — return 503 on browse — so checkout keeps its SLO. Unbounded queues just turn an outage into a latency catastrophe.”

## Exercise

**Design overload behavior for a ride-hailing backend.**

1. Rank shed order: surge pricing calc, nearby-driver map, trip payment capture, receipt email enqueue — and justify.  
2. Driver app retries aggressively on 503 — what must you add to avoid a retry storm?  
3. Say one sentence on when you’d choose “slow the producer” (backpressure) vs “drop the request” (shed).
