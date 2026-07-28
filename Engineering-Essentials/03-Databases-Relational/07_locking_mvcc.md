# Locking & MVCC

> **Locks** stop others from using a row/table; **MVCC** keeps multiple row versions so readers don’t block writers as much.

## Plain English

Concurrency control is how databases let many transactions run without corrupting data. You’ll choose **pessimistic** vs **optimistic** locks, and explain **MVCC** (Postgres/InnoDB) so readers aren’t stuck behind writers.

## Essentials (must-know for this topic)

### Pessimistic vs optimistic

| | **Pessimistic** | **Optimistic** |
|--|-----------------|----------------|
| Idea | Lock first (`FOR UPDATE`) | Write if version unchanged |
| Best when | High conflict, few hot rows | Low conflict, hate waiting |
| Failure mode | Blocking / deadlock | `rowcount=0` → retry |
| Example | Flash-sale inventory row | Edit-form save with `version` |

### MVCC in one glance

| Idea | Meaning |
|------|---------|
| **MVCC** | Multiple row versions; readers see a snapshot |
| Benefit | Readers don’t block writers as much (and vice versa, often) |
| Cost | Old versions need cleanup (**VACUUM** / undo) |
| Still true | Two writers on **same row** can still block |

### Lock types (vocab)

| Lock | Meaning |
|------|---------|
| **Row lock** | One row (common) |
| **Table lock** | Whole table — avoid on hot OLTP |
| **Shared vs exclusive** | Read vs write intent |
| **Deadlock** | Cycle of waits → engine kills one → **retry** |

### Deadlock interview line

T1 locks A waits B; T2 locks B waits A → victim aborted → application **retries** the transaction. Keep lock order consistent; keep critical sections short; never hold locks across external HTTP.

## Why seniors get asked

Concurrency bugs and deadlocks are senior on-call material. Interviewers want lock strategy + MVCC intuition.

## Simple example

```sql
-- Pessimistic
BEGIN;
SELECT qty FROM inventory WHERE sku='TSHIRT' FOR UPDATE;
UPDATE inventory SET qty = qty - 1 WHERE sku='TSHIRT';
COMMIT;

-- Optimistic
UPDATE inventory
SET qty = qty - 1, version = version + 1
WHERE sku='TSHIRT' AND version = 7 AND qty >= 1;
-- if rowcount=0 → conflict → reload & retry
```

## When to use / when not / trade-offs

| Prefer pessimistic when… | Prefer optimistic when… |
|--------------------------|-------------------------|
| High conflict on few hot rows | Low conflict; hate waiting |
| Short critical sections | UI “edit form” save conflicts |

**MVCC trade-off:** great concurrent reads; long transactions and bloat if not vacuumed; writers can still block writers on same row.

## Common pitfalls

- `FOR UPDATE` then calling external APIs (holds locks forever)
- Ignoring deadlock retries
- Optimistic lock without retry/backoff UX
- Giant table locks for DDL during peak

## Interview trigger phrase

> “I’d use MVCC for concurrent reads, FOR UPDATE for hot inventory, optimistic versions for low-contention updates, and always retry deadlocks.”

## Exercise

Flash sale: 1 item, 10k shoppers. Choose pessimistic vs optimistic and justify. What deadlock or stampede failure still remains?
