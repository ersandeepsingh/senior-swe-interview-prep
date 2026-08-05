# Database Tuning — Step-by-Step Playbook

> **Never start with “add an index.”**  
> Order is always: **symptom → measure → isolate worst queries → read the plan → fix root cause → verify → prevent regression.**

---

## 0. Mindset (say this first in interviews)

```text
  Slow DB ≠ always "needs more indexes"
  Could be: bad query, missing index, lock contention, I/O, CPU,
            connection stampede, cache miss, vacuum/bloat, OR app N+1
```

**Golden rule:** change one thing at a time and measure before/after.

---

## Phase 1 — Confirm it’s the database

### Step 1: Separate app vs DB vs network


| Check         | Question                                               |
| ------------- | ------------------------------------------------------ |
| App metrics   | High latency in service, but DB time low? → app/N+1/GC |
| DB metrics    | CPU / I/O / locks / connections spiking? → DB-side     |
| Dependency    | Only one endpoint slow? → that query path              |
| Recent change | Deploy, migration, traffic spike, cron job?            |


```text
  Request latency breakdown (ideal):
  [ network ][ app CPU ][ DB wait ][ DB execute ][ app serialize ]
                         ▲
                    tune here only if this dominates
```

**If DB time is small:** fix app (N+1, over-fetch, missing cache) — not Postgres knobs.

---



## Phase 2 — Find the bottlenecks (system level)



### Step 2: Look at host / managed-DB vitals


| Signal                            | Likely bottleneck                                          |
| --------------------------------- | ---------------------------------------------------------- |
| **CPU high**                      | Heavy queries, sort/hash, missing index → sequential scans |
| **I/O / disk util high**          | Big scans, poor caching, checkpoint storms                 |
| **Memory pressure / swap**        | `shared_buffers` / work_mem issues; too many connections   |
| **Connections near max**          | App pool too large; need PgBouncer                         |
| **Lock waits / blocked sessions** | Long transactions, missing indexes on FK updates           |
| **Replication lag**               | Heavy writes or long queries on primary                    |




### Step 3: See who is active right now (Postgres)

```sql
-- What is running / waiting now?
SELECT pid, usename, state, wait_event_type, wait_event,
       now() - query_start AS duration, left(query, 120) AS query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;
```

```sql
-- Who is blocked by whom?
SELECT blocked.pid AS blocked_pid,
       blocking.pid AS blocking_pid,
       blocked.query AS blocked_query,
       blocking.query AS blocking_query
FROM pg_stat_activity blocked
JOIN pg_locks bl ON bl.pid = blocked.pid AND NOT bl.granted
JOIN pg_locks kl ON kl.locktype = bl.locktype
  AND kl.database IS NOT DISTINCT FROM bl.database
  AND kl.relation IS NOT DISTINCT FROM bl.relation
  AND kl.page IS NOT DISTINCT FROM bl.page
  AND kl.tuple IS NOT DISTINCT FROM bl.tuple
  AND kl.transactionid IS NOT DISTINCT FROM bl.transactionid
  AND kl.classid IS NOT DISTINCT FROM bl.classid
  AND kl.objid IS NOT DISTINCT FROM bl.objid
  AND kl.objsubid IS NOT DISTINCT FROM bl.objsubid
  AND kl.granted
JOIN pg_stat_activity blocking ON blocking.pid = kl.pid
WHERE blocked.pid != blocking.pid;
```



### Step 4: Turn on / use slow-query evidence

**A. Slow query log (always useful)**  
Log statements over a threshold (e.g. `log_min_duration_statement = 500` ms).

**B. Aggregated stats (Postgres)** — `pg_stat_statements` extension:

```sql
-- Worst total time offenders
SELECT calls,
       round(total_exec_time::numeric, 2) AS total_ms,
       round(mean_exec_time::numeric, 2) AS mean_ms,
       rows,
       left(query, 120) AS query
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

Also sort by:

- `mean_exec_time` → individually slow
- `calls` → death by a thousand cuts
- `shared_blks_read` → disk-heavy

**Interview line:**  

> “I rank by **total time** first (impact), then **mean time** (severity), then **calls** (chatty patterns).”

---



## Phase 3 — Isolate the slow queries



### Step 5: Pick top offenders (triage)

For each candidate note:

1. Is it **OLTP** (user-facing) or **batch/analytics**?
2. Frequency × latency = user pain
3. Can it be cached / async / moved to replica?



### Step 6: Reproduce with realistic params

```sql
-- Use real-ish bind values from logs
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT ...
WHERE user_id = 42 AND created_at >= NOW() - INTERVAL '7 days';
```


| `EXPLAIN` clue                           | Meaning                                                   |
| ---------------------------------------- | --------------------------------------------------------- |
| **Seq Scan** on large table              | Often missing/wrong index (not always bad on tiny tables) |
| **Nested Loop** + huge rows              | Bad join / estimate; may need better stats/index          |
| **Hash Join / Sort** spilling            | `work_mem` low or query too wide                          |
| **Rows estimated ≪≫ actual**             | Stale stats → `ANALYZE`; bad plan                         |
| **Buffers: read high**                   | Not hitting cache; I/O bound                              |
| **Heap Fetches high** on index-only scan | Visibility map / vacuum lag                               |


```text
  EXPLAIN        = planner's guess (cheap)
  EXPLAIN ANALYZE = actually runs (use carefully on prod writes!)
```

On prod: prefer replicas / sampled explains; avoid `ANALYZE` on expensive writes without care.

---



## Phase 4 — Rectify (fix in this order)

Fix the **cheapest, highest-impact** causes first.

### Step 7: Fix the query shape (often #1)


| Bad pattern                | Better                                                       |
| -------------------------- | ------------------------------------------------------------ |
| `SELECT *`                 | Select needed columns                                        |
| N+1 from ORM               | Join / `IN` / dataloader / prefetch                          |
| `WHERE YEAR(col)=2024`     | `WHERE col >= '2024-01-01' AND col < '2025-01-01'`           |
| `LIKE '%foo'`              | Trigram index / search engine; avoid leading `%` if possible |
| `OR` across columns        | `UNION` / better indexes / rewrite                           |
| Function on indexed column | Expression index or rewrite                                  |
| Huge `OFFSET` pagination   | Keyset pagination (`WHERE id > last_id`)                     |


```sql
-- Keyset pagination (scales)
SELECT * FROM events
WHERE (created_at, id) < ($last_ts, $last_id)
ORDER BY created_at DESC, id DESC
LIMIT 50;
```



### Step 8: Add / adjust indexes (after seeing the plan)

```text
  Rule: index should match WHERE / JOIN / ORDER BY columns
        that filter early and are selective.
```


| Need                    | Index idea                               |
| ----------------------- | ---------------------------------------- |
| Equality filter         | B-tree on `user_id`                      |
| Filter + sort           | Composite `(user_id, created_at DESC)`   |
| “Only active rows”      | Partial index `WHERE deleted_at IS NULL` |
| JSONB key lookup        | GIN on `JSONB`                           |
| FK parent delete/update | Index on FK columns                      |


**After creating index:**

```sql
ANALYZE table_name;   -- refresh stats
-- re-run EXPLAIN ANALYZE
-- watch write overhead / index size
```

**Don’t:** index every column “just in case” (hurts writes, bloats storage).

### Step 9: Fix locking & transactions


| Problem                    | Fix                                                       |
| -------------------------- | --------------------------------------------------------- |
| Long transactions          | Shorten; don’t hold tx during HTTP/external calls         |
| `SELECT` then update races | `SELECT … FOR UPDATE` sparingly; or optimistic versioning |
| Queue-table contention     | `SKIP LOCKED` pattern                                     |
| Idle in transaction        | App bug — close/rollback promptly                         |


```sql
-- Worker claiming jobs without pile-ups
UPDATE jobs
SET status = 'running'
WHERE id = (
  SELECT id FROM jobs
  WHERE status = 'pending'
  ORDER BY id
  FOR UPDATE SKIP LOCKED
  LIMIT 1
)
RETURNING *;
```



### Step 10: Caching & read path (if still hot)

1. **Application cache** (Redis) for hot keys — with TTL/invalidation
2. **Read replica** for heavy read-only queries (accept lag)
3. **Materialized view** for expensive aggregates (refresh strategy)
4. **CDN / HTTP cache** for public reads



### Step 11: Schema / data-volume tactics


| Symptom                                           | Action                                     |
| ------------------------------------------------- | ------------------------------------------ |
| Table multi-hundred GB, queries touch recent data | **Partition** by time                      |
| Old data rarely read                              | Archive / move cold tier                   |
| Wide rows always fetched                          | Vertical split hot columns                 |
| Hot counters                                      | Keep counters elsewhere or aggregate async |




### Step 12: Connection & server tuning (after query fixes)

Only now touch knobs — wrong order hides real bugs.


| Area             | Common action                                                 |
| ---------------- | ------------------------------------------------------------- |
| Connections      | PgBouncer / pool size ≈ `cores * 2–4` per DB (rule of thumb)  |
| `shared_buffers` | Often ~25% RAM on dedicated DB box (managed defaults OK)      |
| `work_mem`       | Raise carefully for heavy sorts; too high × connections = OOM |
| Autovacuum       | More aggressive on busy tables; watch bloat                   |
| Checkpoints      | Smooth write spikes if I/O storms                             |


**Interview line:**  

> “I tune queries and indexes before `shared_buffers`. Config is last-mile.”



### Step 13: Offload what doesn’t belong in OLTP


| Workload                | Move to                   |
| ----------------------- | ------------------------- |
| Heavy analytics / scans | Replica / warehouse (CDC) |
| Full-text relevance     | Search engine             |
| Huge fan-out reads      | Cache / precompute        |


---



## Phase 5 — Verify & hardenin



### Step 14: Prove the fix


| Check             | Pass criteria                                 |
| ----------------- | --------------------------------------------- |
| `EXPLAIN ANALYZE` | Seq scan gone / buffers read down / time down |
| p95/p99 latency   | Dropped for that endpoint                     |
| CPU / I/O         | Reduced under same load                       |
| Writes            | Insert/update latency not badly regressed     |
| Load test         | Staging replay of prod-like traffic           |




### Step 15: Prevent regression

1. Keep `pg_stat_statements` + dashboards (p95 query time, locks, connections)
2. Slow-query alerts
3. Review migrations for missing indexes on new FKs / filters
4. EXPLAIN critical queries in CI for huge plan regressions (optional)
5. Feature-flag expensive new reports

---



## Quick decision tree

```text
  Is DB time dominating request latency?
       │
       NO → fix app / network / cache
       YES
       │
       ▼
  Look pg_stat_activity + pg_stat_statements + vitals
       │
       ▼
  Top query → EXPLAIN (ANALYZE, BUFFERS)
       │
       ├─ bad query shape     → rewrite
       ├─ missing index       → add composite/partial
       ├─ lock waits          → shorter tx / SKIP LOCKED
       ├─ stale stats         → ANALYZE / autovacuum
       ├─ I/O on big table    → partition / archive / cache
       └─ connections stampede→ pooler
       │
       ▼
  Re-measure → watch writes → add monitors
```

---



## Mini example (end-to-end)

**Symptom:** Checkout API p99 = 2s after Black Friday traffic.

1. APM shows 1.7s in DB.
2. `pg_stat_statements`: `SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC LIMIT 20` — huge total time.
3. `EXPLAIN ANALYZE`: Seq Scan on `orders` (20M rows).
4. Fix: composite index `(user_id, created_at DESC)`; stop `SELECT *`.
5. p99 → 80ms; CPU drops; write latency unchanged.
6. Alert on query p95 + dashboard for seq scans on large tables.

---



## Interview trigger phrase

> “I’d confirm the DB is the bottleneck, pull top queries by total time from `pg_stat_statements`, run `EXPLAIN (ANALYZE, BUFFERS)`, then fix in order: query rewrite → indexes → locks/transactions → cache/replicas → partitioning → server/pool tuning — measuring after each change.”

---



## Exercise

1. A query is fast in staging (100k rows) and slow in prod (50M rows). What do you check first?
2. `EXPLAIN` shows Nested Loop with 5M rows on the inner side. What are 2 possible fixes?
3. CPU is low but latency is high; `wait_event` shows `Lock`. What’s your next step?

