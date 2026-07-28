# Normalization vs Denormalization

> **Normalize** to remove duplication and protect integrity; **denormalize** to make hot reads fast — intentionally copying data.

## Plain English

Normalization puts each fact in one place. Denormalization copies data (or precomputes) so hot reads skip joins. Juniors only normalize; seniors break rules on purpose with an update strategy.

## Essentials (must-know for this topic)

### Normal forms (interview-depth, not textbook)

| Form | One-liner |
|------|-----------|
| **1NF** | Atomic columns; no repeating groups |
| **2NF** | No partial dependency on part of a composite key |
| **3NF** | No transitive dependency (non-key → non-key) |
| **BCNF** | Stricter 3NF variant interviewers may name |

### Normalize vs denormalize

| | **Normalize** | **Denormalize** |
|--|---------------|-----------------|
| Goal | Integrity, one source of truth | Read latency / simpler queries |
| Writes | Cleaner updates | Must update copies / rebuild summaries |
| Reads | More joins | Fewer joins / prejoined docs |
| Fit | OLTP source of truth | CQRS read models, caches, warehouses |

### Common denorm patterns

| Pattern | Example |
|---------|---------|
| Copied attribute | `orders.customer_name` |
| Summary table | `daily_sales(date, total)` |
| Counter cache | `posts.comment_count` |
| JSON snapshot | Order stores line items as JSON |

### Update strategies when you denorm

| Strategy | When |
|----------|------|
| App dual-write | Simple; drift risk |
| Trigger / DB job | Centralized; watch performance |
| Async event → rebuild | Scalable; accept lag |
| Accept stale | Rarely changing display fields |

## Why seniors get asked

Schema design interviews: juniors only normalize; seniors know when to break rules for latency and why consistency gets harder.

## Simple example

Normalized:

```sql
CREATE TABLE customers (id PK, name, email);
CREATE TABLE orders (id PK, customer_id REFERENCES customers, total_cents);
```

Denormalized for read:

```sql
CREATE TABLE orders (
  id PK,
  customer_id,
  customer_name,      -- copied
  total_cents
);
-- must update customer_name when customers.name changes (trigger, app, or accept stale)
```

## When to use / when not / trade-offs

| Normalize when… | Denormalize when… |
|-----------------|-------------------|
| Integrity matters; many write shapes | Read QPS huge; joins dominate latency |
| Data changes often in one place | Warehouses / CQRS read models |
| Early product stage | You’ve measured a real bottleneck |

**Trade-offs:** normalization → more joins, cleaner writes; denormalization → faster reads, sync bugs and storage growth.

## Common pitfalls

- Denormalizing “for speed” with no measurement
- Forgetting to update copies when source changes
- Over-normalizing into awkward 6-table inserts for every click
- Mixing OLTP and huge analytical tables without thought

## Interview trigger phrase

> “I’d keep OLTP normalized for integrity, and denormalize or add read models only where measured read paths need it.”

## Exercise

A product page needs product + seller + average rating. Propose (a) normalized query and (b) a denormalized/cache approach. What becomes hard when a seller renames?
