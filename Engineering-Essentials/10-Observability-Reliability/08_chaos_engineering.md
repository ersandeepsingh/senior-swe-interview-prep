# Chaos Engineering

> Deliberately inject faults in a controlled way to prove (or disprove) that your resilience claims are real — before production does it for free.

## Plain English

You *think* timeouts and circuit breakers work. Chaos engineering **experiments** to verify: kill a pod, add latency to a dependency, drop network packets, exhaust a connection pool — in staging first, then carefully in prod with blast-radius limits.

```text
  Hypothesis: If payment-service latency goes to 2s,
              checkout still completes in < 5s via timeout + degraded path.

  Experiment: Inject 2s latency on payment for 5% of traffic in one AZ.

  Result:     Pass → document. Fail → fix before next real outage.
```

Tools/ideas: Chaos Monkey (kill instances), network latency injection, dependency fault injection libraries, game days.

## Essentials (must-know for this topic)

### Hypothesis-driven, not vandalism

| Piece | Example |
|-------|---------|
| **Steady state** | Checkout p99 < 2s, error rate < 0.1% |
| **Hypothesis** | “If payment latency = 2s, we still finish < 5s via timeout + degrade” |
| **Experiment** | Inject fault on small % / one AZ |
| **Abort criteria** | Error rate > X% or budget burn → stop immediately |
| **Learn** | Pass → document; fail → fix resilience gap |

### Common fault types

| Inject | What you prove |
|--------|----------------|
| Kill pod / instance | Auto-heal, LB health checks |
| Dependency latency / errors | Timeouts, circuit breaker, fallback |
| Network partition / packet loss | Retry + idempotency behavior |
| Exhaust connection pool | Bulkheads actually isolate |

### Staging vs prod

| Where | Gain | Risk |
|-------|------|------|
| **Staging only** | Safe | Misses prod-only config/data paths |
| **Controlled prod** | Real confidence | Needs small blast radius + abort + observability |

**Prerequisite:** basic timeouts, metrics, and runbooks already exist — chaos without observability just creates confusion.

## Simple example

Game day for “inventory DB primary fails”:

1. Failover replica promotion — does app reconnect?
2. Does circuit breaker open on connection errors?
3. Does UI show “stock unknown, try again” vs hang?
4. Do alerts fire within 2 minutes with the right runbook link?

If step 2 hangs for 30s with no timeout — you found a bug *before* Black Friday.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Chaos in staging only | Safe | Misses prod-only config/data paths |
| Controlled prod chaos | Real confidence | Real risk — needs abort + small blast radius |
| Frequent small experiments | Continuous learning | Needs mature observability & culture |
| Annual big game day | Visibility | Gaps grow between events |

## Pitfalls

- **Chaos without observability** — you break things and can't see what happened.
- **No abort criteria** — experiment snowballs into a real incident.
- **Random failure without hypothesis** — noise, no learning.
- **Running chaos before basic timeouts exist** — you'll only rediscover known pain.

## Interview trigger phrase

> “I'd treat resilience as a **hypothesis** and validate it with controlled fault injection — start in staging, then limited prod blast radius — so failover and degradation aren't theoretical.”

## Exercise

Pick one hypothesis for a checkout service that depends on payments and inventory. Define: fault to inject, success criteria, and abort condition.
