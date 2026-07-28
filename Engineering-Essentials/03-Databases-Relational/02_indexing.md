# Indexing

> An index is a side data structure (usually a **B-tree**) that makes lookups and sorts fast — at the cost of **extra writes and storage**.

## Plain English

Without an index, finding `email = 'a@b.com'` may **scan** the whole table. Indexes speed reads; every write must update them too. Seniors choose **which** index — and when not to add one.

## Essentials (must-know for this topic)

### B-tree vs hash (and friends)

| Index type | Good for | Weak for |
|------------|----------|----------|
| **B-tree** (default) | `=`, `<`, `>`, `BETWEEN`, `ORDER BY`, prefix `LIKE 'foo%'` | Leading-wildcard `LIKE '%foo'` |
| **Hash** | Equality only (`=`) | Ranges / sorting (engine-dependent; rare as default) |
| **GIN / GiST** (Postgres) | Arrays, JSONB, full-text | Point lookups you’d do with B-tree |
| **Partial** | `WHERE status='open'` subset | Queries outside the predicate |
| **Covering / INCLUDE** | Index-only scans | Extra storage |

### Composite indexes — leftmost prefix

Index on `(status, created_at)`:

| Query filter | Uses index? |
|--------------|-------------|
| `status = ?` | Yes (leftmost prefix) |
| `status = ? AND created_at > ?` | Yes |
| `created_at = ?` alone | **No** (skips leading column) |

**Order rule:** equality columns first, then range/sort columns — match your `WHERE` + `ORDER BY`.

### Selectivity & write tax

| Idea | Meaning |
|------|---------|
| **Selectivity** | Fraction of rows matching — low-cardinality alone (`boolean`) often weak |
| **Write amplification** | Each INSERT/UPDATE/DELETE updates indexes |
| **Unused index** | Pure cost — drop after verifying |

## Why seniors get asked

“This query is slow” is a daily senior problem. Knowing which index to add — and when *not* to — is the signal.

## Simple example

```sql
CREATE INDEX idx_orders_customer ON orders (customer_id);
CREATE INDEX idx_orders_status_created ON orders (status, created_at DESC);

-- Likely uses composite index
SELECT id FROM orders
WHERE status = 'open'
ORDER BY created_at DESC
LIMIT 20;

-- Covering (Postgres INCLUDE)
CREATE INDEX idx_orders_cover ON orders (status) INCLUDE (total_cents);
```

## When to use / when not / trade-offs

| Add an index when… | Skip / be careful when… |
|--------------------|-------------------------|
| Hot WHERE/JOIN/ORDER BY columns | Column is nearly unique random writes only |
| High read QPS on large tables | Write-heavy tables with many unused indexes |
| Selective predicates | Low-cardinality alone (`boolean`) without composite |

**Trade-offs:** reads faster, writes slower, more disk; wrong composite order = unused index.

## Common pitfalls

- Indexing every column “just in case”
- Wrong column order in composites
- Functions on columns (`WHERE LOWER(email)=`) defeating indexes — use functional indexes if needed
- Ignoring bloat / unused indexes

## Interview trigger phrase

> “I’d add a composite B-tree matching filter+sort order, check it’s selective, and remember every index taxes writes.”

## Exercise

Table `events(user_id, type, created_at)` queried as `WHERE user_id=? AND created_at BETWEEN ? AND ?`. Propose one index. Would `(created_at, user_id)` be as good? Why/why not?
