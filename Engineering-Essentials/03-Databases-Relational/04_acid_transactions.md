# ACID & Transactions

> **ACID** is the promise of a relational transaction: all-or-nothing work that leaves data valid, isolated from others, and durable once committed.

## Plain English

A transaction groups statements so either all commit or none do. ACID is what interviewers mean by “the database keeps money/inventory correct” — within **one** database. Cross-service needs sagas/outbox, not wishful ACID.

## Essentials (must-know for this topic)

### One line each letter

| Letter | Meaning |
|--------|---------|
| **A**tomicity | All statements succeed or all roll back — no partial commit |
| **C**onsistency | Constraints/invariants hold after commit (FKs, checks, app rules enforced in txn) |
| **I**solation | Concurrent txns don’t see each other’s in-progress work beyond the chosen isolation level |
| **D**urability | After `COMMIT`, data survives crashes (WAL / fsync) |

### Transaction control vocab

| Command / idea | Meaning |
|----------------|---------|
| `BEGIN` / `COMMIT` / `ROLLBACK` | Start / persist / undo |
| **Autocommit** | Each statement is its own txn — insufficient for multi-row invariants |
| **WAL** | Write-ahead log — durability mechanism |
| **Savepoint** | Partial rollback inside a txn |

### What ACID does *not* cover

| Myth | Reality |
|------|---------|
| ACID across two microservices | Need saga / 2PC / outbox |
| Long txn while calling Stripe | Holds locks; keep external I/O **outside** |
| “We use transactions” ⇒ no lost updates | Still need isolation, locks, or version checks |

### Keep txns short

| Inside txn | After commit |
|------------|--------------|
| Multi-row DB invariants | Emails, webhooks, HTTP calls |
| Inventory decrement + order insert | Enqueue “send email” job |

## Why seniors get asked

Money, inventory, and bookings need transactional thinking. Seniors know what ACID guarantees — and what it doesn’t (cross-service transactions).

## Simple example

```sql
BEGIN;
INSERT INTO orders (id, user_id, total_cents) VALUES (43, 7, 1999);
INSERT INTO order_items (order_id, sku, qty) VALUES (43, 'TSHIRT', 2);
UPDATE inventory SET qty = qty - 2 WHERE sku = 'TSHIRT' AND qty >= 2;
-- if inventory update matched 0 rows → ROLLBACK
COMMIT;
```

## When to use / when not / trade-offs

| Use transactions when… | Avoid long transactions when… |
|------------------------|-------------------------------|
| Multi-row invariants | Holding locks during HTTP calls to Stripe |
| Money / inventory | Doing heavy reports inside one txn |
| All-or-nothing writes | Cross-microservice (use saga/outbox) |

**Trade-offs:** stronger safety vs more lock contention and latency; durability settings trade speed for crash safety.

## Common pitfalls

- Autocommit single statements when multi-step invariants matter
- Giant transactions that lock hot rows for seconds
- Assuming ACID across two databases/services
- Catching errors and committing anyway

## Interview trigger phrase

> “I’d wrap the multi-row invariant in one transaction for atomicity and durability — and keep external I/O out of the transaction.”

## Exercise

Place order: insert order, decrement stock, enqueue email. What’s inside the DB transaction vs after commit? How do you avoid emailing if the txn rolled back?
