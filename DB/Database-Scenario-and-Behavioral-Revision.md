# Database Scenario & Behavioral — Interview Revision

Operational "what would you do if…" questions (the ones senior interviewers love) plus behavioral questions. Each scenario gives a **structured framework** so you can reason out loud instead of guessing — interviewers grade the *approach*, not one magic answer.

---

## PART 1 — SCENARIO / TROUBLESHOOTING

### S1. "The database suddenly became slow. Walk me through how you'd diagnose and fix it."

The key signal here is a **structured, layered approach** — never jump to "add an index." Say you'd work from symptom → measurement → root cause → fix.

**Step 1 — Scope & measure (don't guess).**
- Is it *everything* slow or *specific queries*? All users or one tenant/region? Sudden or gradual?
- Check dashboards: DB CPU, memory, disk I/O, connection count, replication lag, cache hit ratio.
- Correlate with events: a recent deploy, a schema/index change, a data-volume spike, a new cron job, a traffic surge.

**Step 2 — Find the offending queries.**
- Look at the **slow query log** and active sessions (`SHOW PROCESSLIST` / `pg_stat_activity`).
- Identify the top queries by total time (frequency × latency), not just the single slowest.

**Step 3 — Analyze the query plan.**
- Run `EXPLAIN ANALYZE` on the culprit. Look for: full table scans, missing/unused indexes, bad join order, huge row estimates vs actual, sorts/temp tables spilling to disk.

**Step 4 — Common root causes & fixes.**
- **Missing index** → add an appropriate (often composite) index.
- **Non-sargable query** (e.g., `WHERE YEAR(created)=2024`, leading wildcard `LIKE '%x'`) → rewrite to use a range/index.
- **N+1 queries** → batch with a JOIN or `IN (...)`.
- **Lock contention / long transactions** → shorten transactions, check for blocking/deadlocks.
- **Stale statistics** → run `ANALYZE` so the planner has good estimates.
- **Connection exhaustion** → add connection pooling (PgBouncer), cap app pool sizes.
- **Cache cold/evicted** → warm or resize the cache; check cache hit ratio.
- **Data growth** → a query fine at 10k rows dies at 10M → index/partition/archive old data.
- **Resource saturation** → I/O bound? consider faster storage, more RAM (bigger buffer pool), or offloading reads to replicas.

**Step 5 — Verify & prevent.**
- Re-measure to confirm the fix; compare before/after plan and latency.
- Add monitoring/alerting on the metric so you catch regressions; document in a runbook.

> One-line summary to say: *"Measure first, isolate the worst queries, read the query plan, fix the specific root cause (usually indexing, query shape, locks, or resources), then verify and add monitoring."*

---

### S2. "The number of users / traffic has increased significantly (say 10x). How do you scale the database?"

Frame it as **quick wins → read scaling → write scaling → architecture**, cheapest/least-risky first.

**1. Optimize before you scale (cheapest).**
- Fix slow queries and add missing indexes — often reclaims huge headroom.
- Add **connection pooling** (10x users = 10x connections; DBs die on too many connections).

**2. Add caching (biggest bang for read-heavy loads).**
- Put Redis/Memcached in front for hot reads (cache-aside). Most apps are read-heavy, so this offloads the DB dramatically.
- Add a CDN for static/derived content.

**3. Scale reads.**
- **Read replicas** + read/write splitting: send reads to replicas, writes to primary. Watch replication lag → route read-your-writes to the primary.

**4. Scale writes / storage (harder).**
- **Vertical scaling** first if simple (bigger box) — buys time, has a ceiling.
- **Sharding / horizontal partitioning**: split data by a shard key (e.g., user_id hash). Scales writes and storage but adds cross-shard query complexity and rebalancing.
- **Partition large tables** (by date/range) to keep indexes and scans small.

**5. Offload & separate workloads.**
- Move analytics/reporting off the OLTP DB to a warehouse/replica (OLAP).
- Use async processing (queues) to smooth write spikes instead of hammering the DB synchronously.
- Consider a purpose-built store for specific patterns (search → Elasticsearch, sessions → Redis, event logs → Cassandra) — polyglot persistence.

**6. Consider the data store itself.**
- If access patterns are simple key lookups at extreme scale, a horizontally-scalable NoSQL store may fit better than forcing a relational DB.

> One-line summary: *"Optimize and pool first, cache aggressively, scale reads with replicas, then shard/partition for writes, and offload non-core workloads — scale up before scaling out where I can."*

---

### S3. "Writes are slow / write throughput is the bottleneck. What do you do?"
- Check if indexes are the cost — every index slows writes; drop unused ones.
- Batch inserts instead of row-by-row; use bulk/COPY operations.
- Shorten transactions and reduce lock contention.
- Use async writes / a write-behind queue to absorb spikes.
- Shard writes across nodes by key; consider a write-optimized store (LSM-tree based, e.g., Cassandra) if the workload is genuinely write-heavy.

---

### S4. "A query works fine in staging but is slow in production. Why?"
- **Data volume:** prod has millions of rows; staging has thousands (scan vs index matters only at scale).
- **Stale/different statistics** → planner picks a different plan.
- **Cache state:** prod cache may be cold or under eviction pressure.
- **Concurrency:** prod has locking/contention staging doesn't.
- **Parameter sniffing / different literal values** hitting skewed data.
Diagnose by comparing `EXPLAIN ANALYZE` plans and row counts across environments.

---

### S5. "Users report they saved data but don't see it immediately. What's happening?"
Classic **replication lag** with read replicas: the write hit the primary, but the read was served by a replica that hasn't caught up. Fixes: route a user's reads to the primary for a short window after they write (**read-your-writes**), read from primary for critical paths, or reduce replication lag.

---

### S6. "The database is the single point of failure. How do you make it highly available?"
- **Replication with automatic failover** (primary + standby; promote standby on failure).
- **Multi-AZ / multi-region** deployment for disaster tolerance.
- **Backups + tested restores** (define RPO/RTO); practice failover.
- **Health checks + monitoring** to detect failure fast (lower MTTD).
- For writes, consider multi-leader or a distributed DB if a single primary is unacceptable.

---

### S7. "How would you safely run a schema migration on a huge table with zero downtime?"
- Make changes **backward-compatible** and **incremental** (expand → migrate → contract).
- Add new nullable columns/tables first; deploy code that writes both old+new; backfill in batches (throttled) to avoid locking; then switch reads; then drop the old column later.
- Avoid long locks: use online-DDL tools (pt-online-schema-change, gh-ost) or the DB's online index build.
- Always have a rollback plan and test on a prod-sized copy.

---

### S8. "How do you decide what to index?"
- Index columns used in `WHERE`, `JOIN`, `ORDER BY`, and high-selectivity filters.
- Use composite indexes matching your query's leading-column order.
- Avoid indexing low-selectivity columns and over-indexing (write cost).
- Verify with `EXPLAIN` that the index is actually used; drop unused indexes.

---

## PART 2 — BEHAVIORAL QUESTIONS

Use the **STAR** method: **S**ituation → **T**ask → **A**ction → **R**esult. Keep it specific, quantify results, and focus on *your* actions. Below are common questions with what the interviewer is really probing + a mini answer skeleton.

### B1. "Tell me about a time you improved the performance of a system/database."
*Probing: analytical rigor, measurable impact.*
> STAR skeleton: "Our checkout API p99 hit 3s during peak (S/T). I profiled and found an unindexed `orders(user_id, status)` query doing full scans plus an N+1 loading order items (A). I added a composite index, batched the item fetch into one query, and added a Redis cache for the hot path (A). p99 dropped to 280ms and DB CPU fell 40% (R)." Emphasize you *measured before and after*.

### B2. "Describe a production incident/outage you handled."
*Probing: composure under pressure, structured debugging, ownership.*
> Skeleton: alert fired → you triaged impact and communicated → formed a hypothesis from metrics/logs → mitigated fast (rollback/scale/failover) → root-caused → wrote a blameless postmortem with action items. Stress *mitigate first, blame never, prevent recurrence*.

### B3. "Tell me about a time you made a technical decision with a trade-off (e.g., SQL vs NoSQL, consistency vs availability)."
*Probing: judgment, ability to weigh options, not dogmatic.*
> Skeleton: state the requirement (access patterns, scale, consistency need), the options you considered, *why* you chose one, what you consciously gave up, and how it played out. Showing you knew the downside is the point.

### B4. "Tell me about a time you disagreed with a teammate/manager on a design."
*Probing: collaboration, ego-free, data-driven persuasion.*
> Skeleton: describe the disagreement respectfully, how you brought data/prototypes rather than opinion, how you reached a decision, and that you committed to the outcome even if it wasn't your pick. Avoid making the other person look bad.

### B5. "Tell me about the hardest bug you've debugged."
*Probing: depth, persistence, systematic method.*
> Skeleton: why it was hard (intermittent, cross-service, data-dependent), how you isolated it (reproduced, added tracing/logging, bisected), the root cause, and what you changed to prevent recurrence. A DB-flavored one: a deadlock only under concurrency, found via lock logs, fixed by consistent lock ordering.

### B6. "Tell me about a time you had to deliver under a tight deadline / with ambiguous requirements."
*Probing: prioritization, communication, pragmatism.*
> Skeleton: you clarified scope with stakeholders, cut non-essentials, shipped a correct MVP, and communicated trade-offs/risks. Show you *reduced ambiguity by asking*, didn't just guess.

### B7. "Tell me about a time you made a mistake in production. What did you learn?"
*Probing: accountability and growth, not perfection.*
> Skeleton: own it plainly (e.g., a migration that locked a table), how you fixed it fast, and the systemic change you introduced (add migration to CI, canary, review checklist) so it can't recur. Honesty + a process improvement is what they want.

### B8. "How do you handle technical debt / decide when to refactor vs ship?"
*Probing: balancing pragmatism and quality.*
> Skeleton: you quantify the cost of the debt (slows delivery? risk?), weigh it against business urgency, and negotiate incremental cleanup alongside features rather than a big-bang rewrite. Data over dogma.

---

## Interview delivery tips
- For scenarios: **think out loud and go top-down** — clarify → measure → hypothesize → fix → verify. Interviewers want the framework.
- Always name the **trade-off** and the **failure mode** ("read replicas scale reads but introduce replication lag, so I'd route read-your-writes to the primary").
- For behavioral: 1–2 minutes, STAR, quantify the result, use "I" (your contribution) not just "we".
- It's fine to ask clarifying questions before answering a scenario — that itself is a positive signal.
