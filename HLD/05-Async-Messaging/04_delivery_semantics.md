# Delivery Semantics

> Brokers promise **at-most-once**, **at-least-once**, or (with care) **exactly-once**. In practice seniors design for **at-least-once + idempotent consumers** — duplicates happen; your handler must tolerate them.

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
                 │
                 ▼
        "Did they process it?"
        If unsure → retry → DUPLICATE
```

Network timeouts make “exactly once on the wire” almost mythical. What you want is **exactly-once effect**: processing twice doesn’t double-charge.

## Simple example

Payment worker receives `charge order-99 ₹500`.

```text
  Attempt 1: charge succeeds, ACK lost in network
  Broker redelivers
  Attempt 2: naive code charges again 💥
```

**Idempotent fix:** key the charge by `orderId` (or idempotency key). Second attempt sees “already charged” and ACKs without charging again.

```text
  UNIQUE(order_id) on payments
  OR Redis SETNX idempotency:order-99
  OR Upsert with version check
```

## Why prefer one over the other

| Prefer **at-least-once + idempotency** when… | Prefer **at-most-once** when… |
|----------------------------------------------|-------------------------------|
| Money, inventory, emails you can dedupe | Metrics / samples where loss is OK |
| Default for business workflows | Best-effort telemetry |
| You can store processed keys / unique constraints | Cost of dedupe > cost of loss |

**“Exactly-once” in interviews:** Say Kafka transactions / EOS *can* help end-to-end in a closed pipeline, but **your DB side effects still need idempotency keys**. Don’t claim magic without naming the mechanism.

### Real systems (interview name-drops)

- **SQS / Rabbit / Kafka (default):** at-least-once (or configurable).
- **Idempotency-Key header** (Stripe-style) for HTTP APIs.
- **Outbox pattern** to avoid “DB committed but message never sent.”

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| At-most-once | Simpler; no dup handling | Silent data loss |
| At-least-once | No silent loss | Must handle duplicates |
| Idempotent consumer | Safe retries | Extra storage / unique indexes |
| End-to-end exactly-once txn | Strong story in narrow pipelines | Complexity; not free across arbitrary APIs |

**Common interview trap:** “We’ll use exactly-once delivery” with no idempotency plan for side effects.

## Interview trigger phrase

> “I’d assume **at-least-once** delivery and make consumers **idempotent** with an idempotency key — duplicates are OK; double side effects aren’t.”

## Exercise

**Design “send welcome email” on signup.**

1. Pick a delivery semantic and justify it in one sentence.  
2. Describe one concrete idempotency approach so two deliveries don’t send two emails.  
3. Signup DB write succeeds but enqueue fails — name a pattern that prevents “user exists, no email forever.”
