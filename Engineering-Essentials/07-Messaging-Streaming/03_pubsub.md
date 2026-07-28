# Pub / Sub

> **Publish/Subscribe** fans one event out to **many** independent subscribers. The publisher doesn’t know (or care) who listens. Contrast with a work queue where **competing consumers** share the load of one task stream.

## Plain English

| Pattern | Behavior |
|---------|----------|
| **Work queue** | Each message handled by **one** of N workers |
| **Pub/Sub** | Each message delivered to **all** subscribers (fan-out) |

Implementations: Redis pub/sub, RabbitMQ fanout/topic, SNS→SQS, Kafka (multiple consumer groups), Google Pub/Sub, NATS.

```text
  Work queue:          Pub/Sub:
  msg → W1  (W2 idle)  msg → Service A
                       msg → Service B
                       msg → Service C
```

## Essentials (must-know for this topic)

### Work queue vs pub/sub

| Pattern | Delivery | Use when |
|---------|----------|----------|
| **Work queue** | Each message → **one** of N workers | Share load of the same job |
| **Pub/Sub** | Each message → **all** subscribers | Many independent reactions to one fact |

### Durable vs ephemeral fan-out

| Style | Example | Offline subscriber |
|-------|---------|-------------------|
| **Ephemeral** | Redis pub/sub | **Misses** events |
| **Durable** | SNS→SQS, Kafka consumer groups | Catches up / receives later |

### Common building blocks

| Piece | Role |
|-------|------|
| **Topic / subject** | Named event channel |
| **Subscriber / consumer group** | Independent reader of the fan-out |
| **Schema / contract** | Shared event shape — version it |
| **Outbox** | Publish reliably after DB commit |

**Rule:** critical business events need durable subscribers, not fire-and-forget Redis pub/sub.

## Simple example

**`UserSignedUp` event:**

```text
  Publisher: Auth service

  Subscribers:
    Email service   → welcome email
    Analytics       → funnel event
    CRM             → create lead
    Growth          → start onboarding drip
```

Auth shouldn’t call four HTTP APIs synchronously. Publish once; each team owns its consumer.

**SNS + SQS:** SNS topic fans out; each SQS queue is one subscriber’s durable inbox (common AWS pattern).

## When to use / trade-offs

| Prefer **pub/sub** when… | Prefer **direct call / queue** when… |
|--------------------------|--------------------------------------|
| Many systems react to one fact | One downstream must do the work |
| Loose coupling across teams | You need request/response or single ownership |
| New subscribers shouldn’t change publisher | Workflow needs central orchestration |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Fan-out | Extensibility | Harder to see end-to-end flow |
| Durable subscribers (SNS→SQS, Kafka groups) | No silent loss if consumer down | More moving parts |
| Ephemeral pub/sub (Redis) | Simple | Offline subscribers miss events |

## Pitfalls

- Using **ephemeral** pub/sub for must-not-lose business events.  
- Hidden coupling via **shared event schemas** nobody versions.  
- Assuming order across all subscribers (each may process at different speeds).  
- Dual-writing DB + publish without **outbox** → lost or phantom events.  
- Exploding fan-out with no ownership of failure (who alerts?).

## Interview trigger phrase

> “I’d **publish domain events** and let each bounded context subscribe — fan-out via SNS/Kafka consumer groups — so adding a new reaction doesn’t change the producer.”

## Exercise

**Order placed in checkout.**

1. List 4 realistic subscribers and whether each needs durable delivery.  
2. Why is Redis pub/sub a weak fit for inventory reservation?  
3. Sketch SNS→SQS vs one Kafka topic with 4 consumer groups — one pro each.
