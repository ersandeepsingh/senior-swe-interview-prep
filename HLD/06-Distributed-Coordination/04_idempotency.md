# Idempotency

> Retries are mandatory in distributed systems. **Idempotency** means doing the same logical request **N times** has the same effect as doing it **once** — critical for payments.

## Plain English

Networks timeout. Clients retry. Load balancers retry. Queues deliver at-least-once. Without protection, “charge ₹500” twice = ₹1000 charged.

**Idempotency key:** client (or gateway) sends a unique key per logical operation. Server stores `(key → result)` and on replay returns the **same** outcome without re-executing side effects.

| Delivery promise | What you actually build |
|------------------|-------------------------|
| At-most-once | May lose messages — rare for money |
| At-least-once | Default; **requires idempotent handlers** |
| Exactly-once | Marketing term; usually at-least-once + idempotency |

```text
  Client                    Payment API                 Ledger / Stripe
    │  POST /charge           │                            │
    │  Idempotency-Key: K1    │                            │
    │────────────────────────►│  first time:               │
    │                         │  store K1→pending          │
    │                         │───────────────────────────►│ charge
    │                         │◄───────────────────────────│ ok txn=T9
    │                         │  store K1→{ok,T9}          │
    │◄────────────────────────│  200 {txn:T9}              │
    │  (timeout, retry!)      │                            │
    │  same Key: K1           │  seen K1 → return cached   │
    │────────────────────────►│  NO second charge          │
    │◄────────────────────────│  200 {txn:T9}              │
```

## Simple example

Mobile app: user taps Pay; radio drops after bank debit but before JSON returns. App retries with **same** `Idempotency-Key`. Server recognizes key → returns original success. User sees one charge.

Different key = different logical payment (user intentionally pays twice).

**Implementation sketch:** unique index on `idempotency_key`; begin txn → insert key or fetch existing → if new, do work → store response → commit. Concurrent duplicates serialize on the unique constraint.

## Why prefer one over the other

| Prefer **idempotency keys** when… | Prefer **only natural keys** when… |
|-----------------------------------|------------------------------------|
| Money, bookings, email send, webhooks | Operation is naturally idempotent (PUT absolute state) |
| At-least-once queues / client retries | You control exactly-once end-to-end (rare) |
| External side effects (Stripe, SMS) | Pure reads |

**Keys alone aren’t enough** if handlers aren’t designed carefully: check key → execute → store result must handle races (unique constraint on key, or lock row for key).

**Scope the key:** usually per-user or per-API-key namespace so two clients can’t collide.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Store responses by key | Safe retries | Storage + TTL/GC for keys |
| Short key TTL | Less storage | Late retry may double-apply |
| Long key TTL | Safer late retries | More storage; key reuse risk if client bugs |
| Natural key = order_id | No client key needed | Harder for “pay again on same order” cases |

**Trap:** “Exactly-once delivery.” Say **at-least-once + idempotent consumers**. Queue dedup helps but keys at the **effect** boundary (payment provider) are the real guarantee.

**Stripe-shaped APIs** already honor `Idempotency-Key` — your service should too, and pass a stable key downstream so retries don’t double-hit the PSP.

**In-flight states:** if first request is still `pending`, a concurrent retry should wait or return 409 — not start a second charge.

## Interview trigger phrase

> “I’d make the charge path **idempotent with client keys** stored with the payment record — retries return the first result, so at-least-once messaging can’t double-charge.”

## Exercise

**Design “Pay for order O” with mobile flaky network.**

1. Who generates the idempotency key — app, API gateway, or order service — and why?
2. What happens if two **different** keys race for the same order_id?
3. One sentence: how you’d expire or recycle keys without allowing a double charge a week later.
