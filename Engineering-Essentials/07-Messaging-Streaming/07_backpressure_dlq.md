# Backpressure & DLQ

> When consumers can’t keep up, the system needs **backpressure** (slow producers or shed load) and a plan for **poison messages** — retries with backoff, then a **dead-letter queue (DLQ)** for humans/automation.

## Plain English

| Concept | Meaning |
|---------|---------|
| **Backpressure** | Signal upstream to slow down, or buffer/shed intentionally |
| **Retry + backoff** | Transient failures: wait longer each time (+ **jitter**) |
| **Poison message** | Message that **always** fails (bad payload, bug) |
| **DLQ** | Side queue for messages that exhausted retries |

```text
  Consume → process
      │ fail (transient)
      ▼
  retry 1s → 2s → 4s → … (cap)
      │ still fail / N attempts
      ▼
     DLQ → alert → fix → replay
```

Without a DLQ, one bad message can **block a partition** (Kafka) or burn CPU forever.

## Essentials (must-know for this topic)

### Backpressure, retry, DLQ — definitions

| Concept | Meaning |
|---------|---------|
| **Backpressure** | Slow producers, buffer with limits, or shed load when consumers lag |
| **Transient error** | Timeout / 5xx — worth retrying |
| **Poison message** | Always fails (bad schema, bug) — retries won’t help |
| **Exponential backoff + jitter** | Wait 1s, 2s, 4s… with randomness to avoid herds |
| **DLQ** | Side queue after max attempts for ops/replay |
| **Lag SLO** | Alert when consumer falls behind, not only when DLQ fills |

### What to do with failures

| Failure type | Action |
|--------------|--------|
| Blip / timeout | Retry with backoff + jitter |
| Validation / bad payload | DLQ (or skip + alert) quickly |
| Downstream overload | Backpressure / load shed; don’t retry-storm |
| Kafka poison at offset | Skip or write DLQ topic, then **commit past** it |

**DLQ without alerts = silent graveyard.** Bound retries; never infinite-loop one bad record.

## Simple example

**SQS:** `maxReceiveCount = 5` → then move to DLQ. Worker returns error → visibility timeout expires → retry.

**Kafka:** bad record → log + skip (commit past it) or write to `topic.dlq` + commit; don’t infinite-loop on the same offset.

**HTTP producer backpressure:** return `429` / `503` with `Retry-After`; use load shedding when queue depth &gt; threshold.

## When to use / trade-offs

| Prefer **retry in place** when… | Prefer **DLQ quickly** when… |
|---------------------------------|------------------------------|
| Timeouts, 5xx, blips | Validation errors, schema breaks |
| Downstream briefly overloaded | Poison will never succeed as-is |

| Prefer **block / slow producer** when… | Prefer **drop / sample** when… |
|----------------------------------------|--------------------------------|
| Correctness requires eventual process | Telemetry / best-effort |
| Queue depth is the signal | Protecting core path under attack |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Aggressive retries | Survive blips | Amplify outages (retry storm) |
| Long backoff + jitter | Gentler recovery | Higher latency to success |
| DLQ | Unblocks pipeline | Needs ops process to drain |
| Infinite block on bad msg | “No data loss” feeling | Total stall |

## Pitfalls

- Retries **without jitter** → thundering herd on recovery.  
- Retrying **non-idempotent** side effects.  
- DLQ with **no alarm** and no runbook → silent graveyard.  
- Kafka: failing without advancing offset → partition stuck.  
- Treating backlog as “fine” until disk/cost explodes — set lag SLOs.

## Interview trigger phrase

> “I’d retry **transient** errors with **exponential backoff and jitter**, send **poison messages to a DLQ** after a bound, alert on DLQ depth, and apply **backpressure** when consumer lag breaches SLO.”

## Exercise

**Payment webhook processor.**

1. Classify: timeout to bank vs malformed JSON vs insufficient funds — retry, DLQ, or ack?  
2. Design max attempts + backoff schedule.  
3. Kafka partition stuck on one bad event — two recovery options and a trade-off for each.
