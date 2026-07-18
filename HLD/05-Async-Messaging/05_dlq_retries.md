# DLQ & Retries

> Some messages **never** succeed as-is (**poison messages**). Blind infinite retries melt workers. Use **bounded retries with backoff**, then a **dead-letter queue (DLQ)** so bad messages are isolated for humans/tools — not stuck blocking the main queue.

## Plain English

| Concept | Meaning |
|---------|---------|
| **Transient error** | Timeout, 503, lock contention — retry may work |
| **Poison message** | Bad schema, permanent 400, bug — retry won’t help |
| **Backoff** | Wait longer between retries (often exponential + jitter) |
| **DLQ** | Side queue for messages that exhausted retries |

```text
  Main queue ──► Worker
                  │
         success ─┴─► ACK (done)
                  │
         fail ────┤
                  ▼
            Retry (1, 2, 3…)
            with backoff
                  │
         still fail
                  ▼
            ┌─────────┐
            │   DLQ   │ ──► alert / replay after fix
            └─────────┘
```

## Simple example

Image resize worker gets `{"url": null}` — every attempt throws. Without DLQ:

```text
  Same poison msg redelivered forever
  → CPU burned, good messages delayed, pager quiet (or noisy)
```

With policy: 5 attempts, exponential backoff (1s, 2s, 4s…), then DLQ + metric `dlq_depth`.

```text
  attempt 1 fail → wait
  attempt 5 fail → move to dlq:image-resize
  engineer fixes schema → replay from DLQ
```

## Why prefer one over the other

| Prefer **retry + DLQ** when… | Prefer **fail fast / no retry** when… |
|------------------------------|----------------------------------------|
| Mix of transient and permanent errors | Error is clearly permanent (auth denied) |
| You must not lose the message forever | Best-effort; dropping is OK |
| Ops can inspect / replay later | Consumer should never block on bad input |

**Backoff matters:** thundering herd of retries after an outage can DDoS yourself. Add **jitter**. Cap max attempts.

### Real systems (interview name-drops)

- **SQS redrive policy → DLQ**, **Kafka** retry topics / DLQ patterns, **Rabbit** dead-letter exchanges.
- **Alert on DLQ depth** — silent DLQ is a failure mode.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Infinite retries | Never “give up” | Poison messages stall / waste resources |
| Bounded retries + DLQ | Main lane stays healthy; inspectable failures | Need replay tooling + runbooks |
| Immediate retry only | Simple | Amplifies outages |
| Long backoff | Gentler on deps | Higher end-to-end latency for transient blips |

**Common interview trap:** Drawing a queue with zero mention of poison messages or DLQ.

## Interview trigger phrase

> “I’d retry with **exponential backoff and jitter**, then send poison messages to a **DLQ** with an alert on depth — fix and replay, don’t block the main queue.”

## Exercise

**Design webhook delivery to customer endpoints.**

1. Customer returns 500 vs 400 — how does retry vs DLQ policy differ?  
2. Why add jitter when 10k webhooks fail during their outage?  
3. One sentence: what metric/page tells you “something is stuck,” not just “error rate blipped”?
