# Design a Payment System / Wallet 🔴

> **Crux:** **Exactly-once money movement** via an append-only **ledger** + **idempotency** — never “UPDATE balance” as the source of truth.

## Clarify (say this first)

**Functional**
- Top-up, P2P transfer, pay merchant, refund, statement
- Multi-currency optional; hold/capture for merchants
- Webhooks to merchants on payment status

**Non-functional**
- **Strong consistency** on balances / ledger; no double spend
- Idempotent APIs (client retries are normal)
- Durability: committed payment survives crashes
- Latency: p99 < few hundred ms for authorize; settlement can be async
- Auditability & compliance (immutable history)

## Back-of-envelope

- 10M DAU × 3 payments/day → ~350 write TPS avg; peaks 10× on sales
- Ledger rows grow forever → partition by account + time; hot accounts need care
- Read statements >> writes → replicas OK if lag acceptable for history views
- External PSP calls: timeout + retry → idempotency mandatory

## API + data model

```text
POST /wallets/{id}/transfers     # Idempotency-Key required
POST /payments                   # authorize / capture
POST /payments/{id}/refunds
GET  /wallets/{id}/ledger?cursor=
GET  /payments/{id}
```

| Entity | Key fields |
|--------|------------|
| Account | id, owner, currency, status |
| LedgerEntry | id, account_id, amount(+/-), type, transfer_id, ts |
| Transfer | id, from, to, amount, state, idem_key |
| IdempotencyRecord | key, request_hash, response, status |

Balance = sum(ledger) or materialized under same txn as insert.

## High-level architecture

```text
Client ──► API GW ──► Payment Svc
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
         Idempotency   Ledger DB    Outbox ──► Queue ──► PSP / Notify
         Store         (CP, ACID)
```

## Deep dive: the crux

**Ledger + dual control**
- Every movement = ≥2 ledger lines (double-entry) in one DB transaction.
- Transfer state machine: PENDING → POSTED / FAILED; never mutate posted lines (corrections = new entries).

**Exactly-once (practical)**
- At-least-once transport + **idempotency key** + unique constraints.
- Outbox pattern: commit ledger + outbox row together → async worker delivers to PSP/webhooks.

| Alternative | When to pick |
|-------------|--------------|
| Single `balance` column UPDATE | Tiny / demo only |
| Ledger + idempotency + outbox | Real wallets (**default**) |
| Saga across banks/PSP | Cross-system; compensate on fail |
| Serializable DB + row lock per account | Hot account contention — shard or queue per account |

**Ordering:** serialize debits per account (row lock or per-account queue) to prevent overdraft races.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Strong CP ledger | Correct money | Lower availability under partition |
| Sync PSP authorize | Certainty before UX success | Higher latency / coupling |
| Async settlement | Throughput | Temporary PENDING states |
| Per-account serialization | No overdraft races | Hot celebrity accounts bottleneck |

## Failure modes & scale

- Retry after success → same Idempotency-Key returns original result
- Crash after ledger commit before webhook → outbox replay
- PSP timeout → unknown state; reconcile job; never double-capture
- Hot wallet → stripe accounts / shard; queue writers per account_id
- Scale: shard by account_id; separate read replicas for statements; freeze path for risk

## Interview trigger phrase

> “Balance isn't a field I set — it's a **ledger**. Retries use **idempotency keys**, and side effects go through an **outbox** so money posts exactly once from the client's perspective.”

## Exercise

1. Client POSTs transfer, times out, retries with same key — DB tables touched and final state.
2. How do you prevent overdraft when two transfers debit the same account concurrently?
3. Merchant capture fails after authorize — compensation flow and user-visible states.
