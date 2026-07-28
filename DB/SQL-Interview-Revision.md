# SQL Databases — Interview Revision (Q&A)

Basics → advanced, focused on the most frequently asked interview questions. Each item = **question → concise answer → example** (where useful).

---

## A. Fundamentals

**Q1. What is SQL and what are its sub-languages?**
SQL (Structured Query Language) manages relational data. Sub-categories:
- **DDL** (define schema): `CREATE`, `ALTER`, `DROP`, `TRUNCATE`
- **DML** (manipulate data): `SELECT`, `INSERT`, `UPDATE`, `DELETE`
- **DCL** (permissions): `GRANT`, `REVOKE`
- **TCL** (transactions): `COMMIT`, `ROLLBACK`, `SAVEPOINT`

**Q2. Primary key vs unique key vs foreign key?**
- **Primary key:** uniquely identifies a row; not null; one per table.
- **Unique key:** enforces uniqueness but allows one NULL (varies by DB); can have many.
- **Foreign key:** a column referencing another table's primary key, enforcing referential integrity.

```sql
CREATE TABLE orders (
  id INT PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  user_id INT REFERENCES users(id)  -- foreign key
);
```

**Q3. What is NULL? How does it behave?**
NULL means "unknown/missing," not 0 or empty string. Any comparison with NULL yields NULL (not true), so use `IS NULL` / `IS NOT NULL`. `NULL = NULL` is *not* true.

```sql
SELECT * FROM users WHERE phone IS NULL;   -- correct
SELECT * FROM users WHERE phone = NULL;    -- returns nothing!
```

**Q4. `CHAR` vs `VARCHAR`?**
`CHAR(n)` is fixed length (padded with spaces); `VARCHAR(n)` is variable length (stores only what's used). Use CHAR for fixed codes (e.g., country codes), VARCHAR for names/emails.

**Q5. `DELETE` vs `TRUNCATE` vs `DROP`?**
- `DELETE` — removes rows (can use WHERE), logged, can rollback, triggers fire.
- `TRUNCATE` — removes *all* rows fast, minimal logging, usually can't rollback, resets identity.
- `DROP` — removes the entire table/structure.

---

## B. Joins (very frequently asked)

**Q6. Explain the join types.**
- **INNER JOIN** — only matching rows in both tables.
- **LEFT (OUTER) JOIN** — all left rows + matches (NULLs where no match).
- **RIGHT JOIN** — all right rows + matches.
- **FULL OUTER JOIN** — all rows from both, matched where possible.
- **CROSS JOIN** — Cartesian product (every combination).
- **SELF JOIN** — a table joined to itself.

```sql
SELECT u.name, o.id
FROM users u
LEFT JOIN orders o ON o.user_id = u.id;  -- users with or without orders
```

**Q7. Find users who have never placed an order.**
```sql
SELECT u.*
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.id IS NULL;
```
(The LEFT JOIN + `IS NULL` "anti-join" is a classic question.)

**Q8. What's the difference between `WHERE` and `ON` in a join?**
`ON` defines how rows match; `WHERE` filters the result *after* the join. For INNER JOINs the effect is often the same, but for OUTER JOINs a condition in `WHERE` can accidentally turn a LEFT JOIN into an INNER JOIN (filtering out the NULL rows).

---

## C. Aggregation & Grouping

**Q9. `WHERE` vs `HAVING`?**
`WHERE` filters rows *before* grouping; `HAVING` filters *after* aggregation (on group results).

```sql
SELECT user_id, COUNT(*) AS cnt
FROM orders
WHERE status = 'paid'      -- filter rows first
GROUP BY user_id
HAVING COUNT(*) > 5;       -- then filter groups
```

**Q10. Order of logical execution of a SELECT query?**
`FROM → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT`.
This explains why you can't use a `SELECT` alias in `WHERE` but can in `ORDER BY`.

**Q11. Common aggregate functions?**
`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`. Note `COUNT(*)` counts rows including NULLs; `COUNT(col)` skips NULLs.

**Q12. Find the second-highest salary (classic question).**
```sql
-- Approach 1: subquery
SELECT MAX(salary) FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);

-- Approach 2: window function (handles ties/N-th cleanly)
SELECT DISTINCT salary FROM (
  SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) rnk
  FROM employees
) t WHERE rnk = 2;
```

---

## D. Subqueries & CTEs

**Q13. Correlated vs non-correlated subquery?**
- **Non-correlated:** inner query runs once, independent of the outer query.
- **Correlated:** inner query references the outer row and runs per outer row (can be slower).

```sql
-- Correlated: employees earning above their dept average
SELECT e.* FROM employees e
WHERE e.salary > (
  SELECT AVG(salary) FROM employees
  WHERE dept_id = e.dept_id   -- references outer row
);
```

**Q14. What is a CTE (WITH clause)? Why use it?**
A named temporary result set improving readability and enabling recursion. Cleaner than nested subqueries.

```sql
WITH paid_orders AS (
  SELECT * FROM orders WHERE status = 'paid'
)
SELECT user_id, COUNT(*) FROM paid_orders GROUP BY user_id;
```

**Q15. Recursive CTE — when?**
For hierarchical/graph data (org charts, category trees).
```sql
WITH RECURSIVE subs AS (
  SELECT id, manager_id FROM employees WHERE id = 1
  UNION ALL
  SELECT e.id, e.manager_id FROM employees e
  JOIN subs s ON e.manager_id = s.id
)
SELECT * FROM subs;  -- all reports under employee 1
```

---

## E. Window Functions (senior favorite)

**Q16. What are window functions? How do they differ from GROUP BY?**
They compute across a set of rows *related to the current row* without collapsing rows. GROUP BY returns one row per group; window functions keep every row and add a computed column.

```sql
SELECT name, dept_id, salary,
  RANK()       OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rnk,
  AVG(salary)  OVER (PARTITION BY dept_id) AS dept_avg
FROM employees;
```

**Q17. `ROW_NUMBER` vs `RANK` vs `DENSE_RANK`?**
For ties on ordering:
- `ROW_NUMBER` — unique sequential (1,2,3,4) — ties broken arbitrarily.
- `RANK` — ties share rank, gaps follow (1,2,2,4).
- `DENSE_RANK` — ties share rank, no gaps (1,2,2,3).

**Q18. `LAG` / `LEAD`?**
Access a previous/next row's value — great for computing deltas (e.g., month-over-month growth).
```sql
SELECT month, revenue,
  revenue - LAG(revenue) OVER (ORDER BY month) AS mom_change
FROM monthly_sales;
```

---

## F. Indexing (heavily asked)

**Q19. What is an index and how does it work?**
A data structure (usually a **B-tree**) that lets the DB find rows without scanning the whole table — like a book's index. Speeds up reads/lookups/sorts, but slows writes (must be maintained) and uses storage.

**Q20. Clustered vs non-clustered index?**
- **Clustered:** determines the physical order of rows; one per table (often the primary key). The leaf *is* the data.
- **Non-clustered:** a separate structure pointing to rows; you can have many.

**Q21. What is a composite index and why does column order matter?**
An index on multiple columns `(a, b, c)`. It's usable for queries filtering on a leading prefix (`a`, or `a,b`, or `a,b,c`) — the **leftmost-prefix rule** — but not for `b` alone.

```sql
CREATE INDEX idx ON orders(user_id, status);
-- helps: WHERE user_id=1 AND status='paid'
-- helps: WHERE user_id=1
-- NOT used efficiently: WHERE status='paid'  (skips leading column)
```

**Q22. What is a covering index?**
An index that contains all columns a query needs, so the DB answers it from the index alone without touching the table ("index-only scan").

**Q23. When do indexes NOT help / hurt?**
- Low-selectivity columns (e.g., boolean `is_active`) — a scan may be cheaper.
- Functions on the column (`WHERE YEAR(created)=2024`) prevent index use — use a range or a functional index instead.
- Too many indexes slow down INSERT/UPDATE/DELETE.

**Q24. How do you diagnose a slow query?**
Use `EXPLAIN` / `EXPLAIN ANALYZE` to read the query plan — look for full table scans, missing index usage, bad join order, or huge row estimates, then add indexes or rewrite.

---

## G. Transactions & ACID (very frequently asked)

**Q25. What does ACID mean?**
- **Atomicity** — all-or-nothing; a transaction fully commits or fully rolls back.
- **Consistency** — moves the DB from one valid state to another (constraints hold).
- **Isolation** — concurrent transactions don't corrupt each other.
- **Durability** — once committed, survives crashes (persisted to disk/log).

**Q26. What is a transaction? Give an example.**
A unit of work executed atomically.
```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;   -- both succeed, or ROLLBACK undoes both
```

**Q27. Explain isolation levels and the anomalies they prevent.**
| Level | Dirty read | Non-repeatable read | Phantom read |
|---|---|---|---|
| Read Uncommitted | ❌ possible | ❌ | ❌ |
| Read Committed | ✅ prevented | ❌ | ❌ |
| Repeatable Read | ✅ | ✅ prevented | ❌ (mostly) |
| Serializable | ✅ | ✅ | ✅ prevented |

- **Dirty read:** reading another txn's uncommitted change.
- **Non-repeatable read:** same row read twice gives different values.
- **Phantom read:** same query returns new rows on re-run.
Higher isolation = more correctness, less concurrency.

**Q28. Optimistic vs pessimistic locking?**
- **Pessimistic:** lock rows up front (`SELECT ... FOR UPDATE`); others wait. Good under high contention.
- **Optimistic:** don't lock; check a version/timestamp at commit and retry if it changed. Good under low contention.

**Q29. What is a deadlock and how do you handle it?**
Two transactions each hold a lock the other needs, waiting forever. DBs detect it and kill one (victim) to break it. Prevent by acquiring locks in a consistent order and keeping transactions short.

---

## H. Schema Design & Normalization

**Q30. What is normalization? List the main normal forms.**
Organizing tables to reduce redundancy and anomalies.
- **1NF:** atomic values, no repeating groups.
- **2NF:** 1NF + no partial dependency on part of a composite key.
- **3NF:** 2NF + no transitive dependency (non-key depends only on the key).
- **BCNF:** stricter 3NF.

**Q31. When would you denormalize?**
For read performance — duplicate data to avoid expensive joins (e.g., store `user_name` on the orders table, or precompute a `comment_count`). Trade-off: faster reads, but you must keep duplicates in sync on writes.

**Q32. One-to-many vs many-to-many modeling?**
- One-to-many: foreign key on the "many" side (order → user_id).
- Many-to-many: a **junction/join table** (`student_id, course_id`).

---

## I. Scaling & Advanced

**Q33. Replication vs sharding (partitioning)?**
- **Replication:** copies of the same data on multiple nodes → read scaling + high availability.
- **Sharding:** splitting data across nodes by a shard key → write/storage scaling. (Adds cross-shard query complexity.)

**Q34. Vertical vs horizontal partitioning?**
- **Vertical:** split columns into separate tables (e.g., rarely-used blob columns).
- **Horizontal:** split rows (e.g., by date or hash) — same schema, different rows per partition.

**Q35. How do you scale reads on a SQL database?**
Read replicas + read/write splitting, caching (Redis) in front, proper indexing, and connection pooling. Beware replication lag causing stale reads.

**Q36. What is a materialized view?**
A view whose results are physically stored (and refreshed periodically), unlike a regular view which re-runs its query each time. Speeds up expensive aggregations at the cost of freshness.

**Q37. What causes the N+1 query problem and how do you fix it?**
Fetching a list (1 query), then a query per item (N queries) — e.g., loading 100 users then their orders one by one. Fix with a JOIN or a single `IN (...)` batch query (or ORM eager loading).

---

## J. Rapid-fire / commonly asked one-liners

- **`UNION` vs `UNION ALL`:** UNION removes duplicates (slower, sorts); UNION ALL keeps all.
- **`DISTINCT` vs `GROUP BY`:** both dedupe; GROUP BY is for aggregation, DISTINCT just for unique rows.
- **View:** a saved query (virtual table); simplifies access and can restrict columns.
- **Stored procedure vs function:** procedures perform actions (can modify data, no required return); functions return a value and are usable in queries.
- **Trigger:** code that auto-runs on INSERT/UPDATE/DELETE (e.g., audit logging).
- **OLTP vs OLAP:** OLTP = many small transactions (app DB); OLAP = complex analytical queries (warehouse).
- **`COALESCE`:** returns first non-null argument — `COALESCE(nickname, name, 'Guest')`.
- **`CASE`:** inline conditional — `SELECT CASE WHEN score>=50 THEN 'pass' ELSE 'fail' END`.

---

## Most-asked coding problems to practice
1. Second/Nth highest salary.
2. Find duplicates (`GROUP BY ... HAVING COUNT(*) > 1`).
3. Users with no orders (anti-join).
4. Running total / cumulative sum (window function).
5. Top N per group (`ROW_NUMBER` partitioned).
6. Month-over-month change (`LAG`).
7. Department with highest average salary.
8. Delete duplicate rows keeping one.
