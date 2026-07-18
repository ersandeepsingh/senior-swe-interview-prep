# 3. Data Storage & Modeling

How you **store and shape data** drives latency, consistency, cost, and how painful scaling feels later. Interviewers expect you to pick a store from the **access pattern**, not from habit (“we always use Postgres”).

| # | Concept | One-line intent |
|---|---------|-----------------|
| 01 | [SQL vs NoSQL](01_sql_vs_nosql.md) | Relational vs document / column / KV / graph by access pattern |
| 02 | [Indexing](02_indexing.md) | B-tree / hash / inverted — speed reads without full scans |
| 03 | [Normalization vs denormalization](03_normalization_vs_denormalization.md) | Joins vs read-optimized duplication |
| 04 | [Partitioning & sharding](04_partitioning_sharding.md) | Range / hash / directory / geo — split data across nodes |
| 05 | [Consistent hashing](05_consistent_hashing.md) | Minimize reshuffle when nodes join or leave |
| 06 | [Replication](06_replication.md) | Leader-follower / multi-leader / leaderless |
| 07 | [Read/write splitting](07_read_write_splitting.md) | Writes to primary, reads to replicas |
| 08 | [Multi-region geo-replication](08_multi_region_geo_replication.md) | Active-active vs active-passive across regions |
| 09 | [Specialized stores](09_specialized_stores.md) | Time-series / columnar / graph for fit-for-purpose workloads |
| 10 | [Blob / object storage](10_blob_object_storage.md) | S3-style for media, dumps, and cold archives |

**How to use:** For each file — read Plain English → diagram → trade-offs → say the interview trigger phrase out loud → do the Exercise without peeking at notes.
