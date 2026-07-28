# Query Optimization

> Make SQL fast by reading **query plans** (`EXPLAIN`), using indexes, and avoiding patterns that explode work (full scans, N+1).

## Plain English

Optimization is a loop: measure → read the plan → fix index/SQL/app → re-measure. Guessing indexes without `EXPLAIN` is junior behavior.

## Essentials (must-know for this topic)

### Reading plans — vocab

| Term | Meaning |
|------|---------|
| **Seq Scan** | Read whole table — OK small; scary on huge hot tables |
| **Index Scan / Index Only Scan** | Use index (± heap fetch); covering = index only |
| **Bitmap Heap/Index Scan** | Combine indexes then fetch rows |
| **Nested Loop / Hash Join / Merge Join** | How tables combine |
| **Rows estimate vs actual** | Big mismatch → stale stats (`ANALYZE`) |

`EXPLAIN` = estimate; `EXPLAIN ANALYZE` = runs it and shows real times/rows.

### Optimization loop

1. Measure slow query (latency, frequency)  
2. `EXPLAIN ANALYZE`  
3. Fix: index, rewrite SQL, kill N+1, update stats  
4. Re-measure  

### N+1 (app + SQL)

| Pattern | Fix |
|---------|-----|
| 1 query for parents + N for children | `JOIN`, `WHERE id IN (…)`, batch loader |
| Huge `OFFSET` pagination | Keyset/cursor pagination |
| `SELECT *` | Select needed cols; enable covering indexes |

### Selectivity intuition

| Predicate | Likely plan |
|-----------|-------------|
| Highly selective (`id = ?`) | Index |
| Low selectivity (`status = 'active'` on 90% rows) | Seq scan may be cheaper |
| `OR` across columns | Sometimes rewrite as `UNION` for sargability |

## Why seniors get asked

Anyone can add an index randomly. Seniors prove it with plans and talk about selectivity, join order, and app-side N+1.

## Simple example

```sql
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 42 AND status = 'open';
```

Bad app pattern:

```python
orders = db.query("SELECT * FROM orders WHERE status='open'")
for o in orders:
    user = db.query("SELECT * FROM users WHERE id=%s", o.user_id)  # N+1
```

Better:

```sql
SELECT o.*, u.name
FROM orders o
JOIN users u ON u.id = o.user_id
WHERE o.status = 'open';
```

## When to use / when not / trade-offs

| Technique | When |
|-----------|------|
| Index scan | High selectivity filters |
| Rewrite OR → UNION | Sometimes helps sargability |
| Materialized summary table | Heavy dashboards |
| Denormalize carefully | Read path dominates |

**Trade-offs:** premature micro-optimization vs ignoring a seq scan on 50M rows; caching can hide a bad query until traffic spikes.

## Common pitfalls

- Trusting estimates without `ANALYZE` (stale stats)
- `SELECT *` preventing covering indexes
- Pagination with huge `OFFSET`
- Fixing symptoms in Redis instead of the plan

## Interview trigger phrase

> “I’d EXPLAIN ANALYZE it, look for seq scans and bad row estimates, kill N+1 with a join/batch, and only then add indexes.”

## Exercise

`GET /open-orders` takes 2s. Pseudocode does a query per order line. Sketch the plan you’d expect today vs after a single joined query, and name two metrics you’d plot.
