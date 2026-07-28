# Isolation Levels

> Isolation controls **what concurrent transactions are allowed to see** — from “dirty reads OK” up to full serializability.

## Plain English

Even inside ACID, “I” is tunable. Weaker isolation = more throughput and more anomalies; stronger = fewer races and more aborts/locks. Defaults differ by engine.

## Essentials (must-know for this topic)

### Anomalies

| Anomaly | Meaning |
|---------|---------|
| **Dirty read** | See **uncommitted** data from another txn |
| **Non-repeatable read** | Same row’s values **change** if you re-read |
| **Phantom read** | **New rows** appear matching a `WHERE` on re-query |
| **Lost update** | Two writers overwrite each other based on stale reads |

### Levels vs anomalies (weak → strong)

| Level | Dirty | Non-repeatable | Phantom | Notes |
|-------|-------|----------------|---------|-------|
| **Read Uncommitted** | Possible | Possible | Possible | Rarely used |
| **Read Committed** | Prevented | Possible | Possible | **Postgres default** |
| **Repeatable Read** | Prevented | Prevented | Engine-dependent | **MySQL InnoDB default**; Postgres RR ≈ snapshot |
| **Serializable** | Prevented | Prevented | Prevented | May abort → **retry** |

### Engine defaults to remember

| Engine | Default |
|--------|---------|
| PostgreSQL | Read Committed |
| MySQL InnoDB | Repeatable Read |

### Practical patterns for lost updates

| Approach | How |
|----------|-----|
| `SELECT … FOR UPDATE` | Pessimistic lock row |
| Optimistic version | `UPDATE … WHERE version=?` |
| Serializable + retry | On serialization failure |
| Unique constraint | One-time coupon / idempotency key |

## Why seniors get asked

Seniors must pick a level for “double spend” or inventory races — and know stronger isolation costs throughput.

## Simple example

```sql
-- Postgres
BEGIN ISOLATION LEVEL SERIALIZABLE;
SELECT balance FROM accounts WHERE id = 1;
-- ... another txn might conflict → serialization failure → retry
COMMIT;
```

Lost update sketch at weak isolation:

```text
T1 reads balance 100
T2 reads balance 100
T1 writes 100-10=90
T2 writes 100-20=80   -- T1's debit lost
```

## When to use / when not / trade-offs

| Level | Fit |
|-------|-----|
| Read Committed | Most web apps (default OK) |
| Repeatable Read / Snapshot | Reports needing stable snapshots |
| Serializable | Hot financial invariants when retries OK |

**Trade-offs:** stronger isolation → more aborts/retries or locks; weaker → subtle races.

## Common pitfalls

- Assuming “transactions” alone prevent lost updates (need proper isolation, locks, or `UPDATE ... RETURNING` patterns)
- Not retrying serialization failures
- Holding serializable txns open too long
- Confusing engine-specific RR behavior (Postgres vs MySQL)

## Interview trigger phrase

> “I’d default to read committed, use row locks or optimistic versioning for lost updates, and reach for serializable only where invariants demand it — with retries.”

## Exercise

Two requests concurrently redeem the same one-time coupon. Explain the race at read committed and two ways to fix it (unique constraint / row lock / serializable).
