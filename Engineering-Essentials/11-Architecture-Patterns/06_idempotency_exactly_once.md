# Idempotency & Exactly-Once

> Networks retry. Clients double-click. Queues redeliver. **Idempotency** makes repeats safe. “Exactly-once” in distributed systems is almost always **at-least-once + idempotent processing** (or a transactional outbox trick).

## Plain English

**Idempotent operation:** doing it N times has the same effect as once. `PUT /resource/id` with same body ≈ idempotent. `POST /charge` without a key is not.

```text
  Client  --POST /payments (Idempotency-Key: abc)-->  Server
  Client retries same key
  Server finds abc → returns stored 200 + payment_id  (no second charge)
```

## Essentials (must-know for this topic)

### Delivery semantics

| Claim | Reality |
|-------|---------|
| **At-most-once** | May lose messages |
| **At-least-once** | May duplicate — **default** on networks/queues |
| **Exactly-once** | End-to-end is hard; usually **effectively once** via idempotent consumers + dedupe |

### Idempotency key pattern

| Piece | Role |
|-------|------|
| **Client** | Sends `Idempotency-Key: <uuid>` once per user intent |
| **Server** | Stores key → response/result |
| **Retry** | Same key → return stored result (**no** second side effect) |
| **TTL** | Expire old keys after a safe window |

### Making consumers safe

| Technique | Idea |
|-----------|------|
| **Unique event-id table** | Insert event_id in same txn as side effect; conflict → already done |
| **Natural idempotency** | `UPDATE … SET status='paid' WHERE id=? AND status!='paid'` |
| **Outbox pattern** | Business row + outbox event in **one** DB txn; publisher relays → bus |

**Interview line:** assume at-least-once; make handlers idempotent → effectively exactly-once side effects.

## Simple example

Kafka consumer updating “order paid”:

1. Read message `payment_captured` for `order_id=o1`.
2. In one DB transaction: insert into `processed_events(event_id)` (unique) **and** update order status.
3. If insert conflicts → already processed → commit/skip (ack).
4. Ack Kafka offset only after successful commit (or use transactional patterns carefully).

**Outbox pattern:** write business row + outbox event in same DB transaction; publisher relays outbox → bus. Avoids “DB committed but event never sent” and the reverse.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Idempotency keys | Safe client retries | Storage/TTL for key map |
| At-least-once + idempotent consumer | Reliable processing | Dedup store / careful txn design |
| True exactly-once protocols | Simpler mental model (rare) | Complexity, vendor limits, still edge cases |
| At-most-once | Simple | Data loss |

## Pitfalls

- **Retrying non-idempotent POSTs** at every layer.
- **Deduping only in memory** — lost on restart → double apply.
- **Ack before side effect** — crash → lost update; or **side effect before dedup record** → double apply on retry.
- **Saying “Kafka exactly-once” as magic** — understand it's within limited scopes; side effects still need care.

## Interview trigger phrase

> “I'd assume **at-least-once** delivery and make handlers **idempotent** with an idempotency key or unique event-id table — that's how you get **effectively exactly-once** side effects.”

## Exercise

Design charge API retries for a flaky mobile network. What does the client send? What does the server store? What happens on a retry after success vs after a crash mid-charge?
