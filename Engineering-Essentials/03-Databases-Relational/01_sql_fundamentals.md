# SQL Fundamentals

> Declarative language to **query and change** relational data: joins, aggregation, subqueries, and window functions.

## Plain English

You describe *what* you want; the engine picks *how*. Interview SQL is mostly joins, `GROUP BY`, and knowing when a **window function** beats a messy self-join.

## Essentials (must-know for this topic)

### JOIN types

| Join | Keeps rows when… |
|------|------------------|
| **INNER** | Match on both sides |
| **LEFT** | All left + matches (NULL right if none) |
| **RIGHT** | All right + matches (less common) |
| **FULL** | All from both (NULLs where no match) |
| **CROSS** | Cartesian product |

Trap: `WHERE right.col = …` after `LEFT JOIN` filters away non-matches → acts like **INNER**.

### Aggregation vs windows

| Tool | Effect on rows |
|------|----------------|
| **GROUP BY** + `COUNT`/`SUM` | Collapses groups to one row |
| **Window** `OVER (PARTITION BY …)` | Keeps row count; adds computed columns |

| Window function | Typical use |
|-----------------|-------------|
| `ROW_NUMBER()` | “Latest per group” (`rn = 1`) |
| `RANK()` / `DENSE_RANK()` | Leaderboards |
| `SUM() OVER (…)`, `LAG`/`LEAD` | Running totals / previous row |

### Query shape vocab

| Term | Meaning |
|------|---------|
| **Subquery** | Query inside a query (FROM/WHERE/SELECT) |
| **Correlated subquery** | Re-runs per outer row — often slow |
| **HAVING** | Filter **after** aggregation (`WHERE` is before) |
| **sargable** | Predicate can use an index (`col = ?`, not `LOWER(col)=?` unless functional index) |

### Execution order (mental model)

`FROM/JOIN → WHERE → GROUP BY → HAVING → WINDOW → SELECT → ORDER BY → LIMIT`

## Why seniors get asked

Almost every backend interview has SQL. Seniors write correct joins and reach for windows instead of messy self-joins.

## Simple example

```sql
-- Orders with customer name (INNER JOIN)
SELECT o.id, c.name, o.total_cents
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.status = 'open';

-- Totals per customer
SELECT customer_id, COUNT(*) AS order_count, SUM(total_cents) AS spent
FROM orders
GROUP BY customer_id
HAVING SUM(total_cents) > 10000;

-- Latest order per customer (window)
SELECT id, customer_id, total_cents
FROM (
  SELECT id, customer_id, total_cents,
         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at DESC) AS rn
  FROM orders
) t
WHERE rn = 1;
```

## When to use / when not / trade-offs

| Prefer | When |
|--------|------|
| JOIN in SQL | DB can use indexes; less N+1 in app |
| Window functions | Rankings, running totals, “latest per group” |
| App-side merge | Tiny datasets or cross-database sources |

**Trade-off:** complex SQL is powerful but harder to test/debug; over-fetching in the app causes N+1.

## Common pitfalls

- `WHERE` on LEFT JOIN’s right table turns it into an INNER JOIN
- Forgetting `GROUP BY` non-aggregated columns
- `SELECT *` in production paths
- Correlated subqueries that run per row

## Interview trigger phrase

> “I’d join on indexed keys, aggregate with GROUP BY, and use window functions for ‘top-N per group’ instead of procedural loops.”

## Exercise

Write SQL for: each customer’s most recent order total, and how many orders they placed in 2025. Prefer window + filter or `DISTINCT ON` (Postgres) — explain your choice.
