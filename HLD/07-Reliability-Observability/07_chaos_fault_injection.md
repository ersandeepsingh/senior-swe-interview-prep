# Chaos & Fault Injection

> Resilience you never **tested** is fictional. **Chaos engineering** deliberately injects faults (kill nodes, add latency, drop partitions) to verify failover, breakers, and runbooks — in controlled blast radius.

## Plain English

Diagrams claim HA. Chaos asks: “Did failover actually work last Tuesday?” Practice is **hypothesis-driven**, not random vandalism.

| Practice | What you do |
|----------|-------------|
| **Fault injection** | Timeout, 5xx, packet loss, clock skew in test/stage (or prod carefully) |
| **Chaos experiments** | Hypothesis → inject → measure SLO → learn |
| **Game days** | Humans practice DR / incident response |

```text
  Hypothesis: "If Ranker latency +2s, Feed p99 stays <300ms via breaker+fallback"

       Inject latency ──► Observe metrics / traces
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
        Hypothesis holds                 Fix: tune timeout,
        (document)                       bulkhead, fallback
```

## Simple example

Kill the Kafka leader in staging → confirm consumers reconnect, no stuck lag forever. Add 5s delay to payment sandbox → confirm checkout breaker opens and user sees clear retry UX — not hung spinners.

```text
  Experiment card:
    Blast radius: 1% canary, one AZ
    Abort: SLO burn > X or pager
    Observe: error%, p99, breaker state, lag
```

Netflix Chaos Monkey popularized random instance death; modern practice pairs automation (Litmus, Chaos Mesh, Gremlin, FIS) with **guardrails**.

## Why prefer one over the other

| Prefer **chaos in prod (careful)** when… | Prefer **stage-only** when… |
|------------------------------------------|-----------------------------|
| Stage ≠ prod traffic/shape | Regulated / high blast risk |
| Strong observability + abort switch | Early maturity, weak SLOs |
| Small % canaries | Can’t isolate tenants yet |

**Start in staging**, then canary prod experiments with kill switches. Never chaos without metrics and a rollback plan. Game days train humans; fault injection trains systems.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Regular fault injection | Real confidence | Engineering time; some user impact |
| Only theoretical HA | Pretty diagrams | Surprise on real outage |
| Random wide chaos | Broad coverage | Harder to learn; higher risk |
| Narrow hypotheses | Clear learnings | May miss unknown unknowns |

**Trap:** “We have replicas so we’re fine.” Seniors: “We **proved** failover under injection last quarter; here’s what broke.”

**Good first experiments:** kill one AZ’s pods; add +500ms to a dependency; partition app↔DB briefly; expire a cert in staging. Each maps to a concrete hypothesis.

**Stop conditions:** automatic abort if error budget burns too fast — chaos without brakes is just an outage you scheduled.

## Interview trigger phrase

> “I’d validate HA with **fault injection and game days** — kill the primary, delay deps — and treat failing hypotheses as backlog, not a checkbox.”

## Exercise

**Chaos plan for a chat system (WS gateway + message store + fan-out).**

1. Write one falsifiable hypothesis about gateway pod death.
2. What blast radius controls do you set for a prod experiment?
3. One sentence linking chaos results to circuit breaker timeouts.
