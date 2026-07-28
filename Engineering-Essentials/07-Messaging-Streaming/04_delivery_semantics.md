# Delivery Semantics

> Brokers promise **at-most-once**, **at-least-once**, or (with care) **exactly-once**. In practice seniors design for **at-least-once + idempotent consumers** — duplicates happen; handlers must tolerate them.

## Plain English

| Semantic | Meaning | Failure mode |
|----------|---------|--------------|
| **At-most-once** | Deliver 0 or 1 time | Message can be **lost** |
| **At-least-once** | Deliver ≥ 1 time | Message can be **duplicated** |
| **Exactly-once** | Effectively once | Hard; needs txn / idempotency / dedupe |

```text
  Producer ──► Broker ──► Consumer
                 │
     crash / timeout / retry
                 ▼
        Unsure if processed? → retry → DUPLICATE
```

What you usually want is **exactly-once effect**: processing twice doesn’t double-charge.

## Essentials (must-know for this topic)

### At-most / at-least / exactly-once

| Semantic | Meaning | You must accept… |
|----------|---------|------------------|
| **At-most-once** | 0 or 1 delivery | Possible **loss** |
| **At-least-once** | ≥ 1 delivery | Possible **duplicates** |
| **Exactly-once** | Effectively once | Broker txns **and/or** idempotent side effects |

### How seniors actually ship it

| Building block | Role |
|----------------|------|
| **Idempotency key** | Dedupe so retry ≠ double charge / double email |
| **Unique constraint** | DB enforces “process once” |
| **Outbox pattern** | DB row + outbox in one txn → publisher drains to broker |
| **ACK after side effect** | ACK before work → loss; work before dedupe record → careful ordering |

**Interview default:** design for **at-least-once + idempotent consumers**. “Exactly-once” without an idempotency story is a red flag.

## Simple example

Payment worker receives `charge order-99 ₹500`.

```text
  Attempt 1: charge succeeds, ACK lost
  Broker redelivers
  Attempt 2: naive code charges again 💥

  Fix: UNIQUE(order_id) / Idempotency-Key / SETNX processed:order-99
```

**Outbox pattern:** write business row + outbox row in **one DB transaction**; a publisher drains outbox → broker. Avoids “DB committed but message never sent.”

## When to use / trade-offs

| Prefer **at-least-once + idempotency** when… | Prefer **at-most-once** when… |
|----------------------------------------------|-------------------------------|
| Money, inventory, emails you can dedupe | Metrics / samples where loss is OK |
| Default for business workflows | Best-effort telemetry |

| Decision | You gain | You give up |
|----------|----------|-------------|
| At-most-once | Simple | Silent loss |
| At-least-once | No silent loss | Must handle duplicates |
| Idempotent consumer | Safe retries | Extra storage / unique indexes |
| Kafka EOS / transactions | Strong story in closed pipelines | Complexity; side effects still need care |

## Pitfalls

- Saying “exactly-once” with **no** idempotency plan for DB/HTTP side effects.  
- Idempotency key too coarse (blocks legitimate retries) or too fine (doesn’t dedupe).  
- ACK before side effect → loss; side effect before durable dedupe record → double apply on crash mid-way (order the steps carefully).  
- Ignoring producer retries → duplicate publishes.

## Interview trigger phrase

> “I’d assume **at-least-once** delivery and make consumers **idempotent** with an idempotency key — duplicates are OK; double side effects aren’t.”

## Exercise

**Design “send welcome email” on signup.**

1. Pick a delivery semantic and justify it in one sentence.  
2. One concrete idempotency approach so two deliveries don’t send two emails.  
3. Signup DB write succeeds but enqueue fails — name a pattern that prevents “user exists, no email forever.”
