# NoSQL Databases — Interview Revision (Q&A)

Basics → advanced, focused on the most frequently asked interview questions. Each item = **question → concise answer → example** (where useful).

---

## A. Fundamentals

**Q1. What is NoSQL and why does it exist?**
"Not Only SQL" — a family of non-relational databases built for scale, flexible schemas, and high write/read throughput that traditional relational DBs struggle with at web scale. They typically scale horizontally and relax some SQL guarantees (like strict schema or immediate consistency) for performance and availability.

**Q2. What are the main types of NoSQL databases?**


| Type        | Model                                                 | Examples                   | Good for                          |
| ----------- | ----------------------------------------------------- | -------------------------- | --------------------------------- |
| Key-Value   | key → opaque value                                    | Redis, DynamoDB, Riak      | caching, sessions, simple lookups |
| Document    | key → JSON-like document                              | MongoDB, Couchbase         | flexible/nested app data          |
| Wide-column | rows with dynamic columns, grouped in column families | Cassandra, HBase, Bigtable | huge write volumes, time-series   |
| Graph       | nodes + edges                                         | Neo4j, Neptune             | relationship-heavy queries        |


**Q3. SQL vs NoSQL — key differences?**

- **Schema:** SQL fixed/rigid; NoSQL flexible/dynamic.
- **Scaling:** SQL usually vertical (+read replicas); NoSQL horizontal by design.
- **Joins:** SQL native; NoSQL usually none (denormalize instead).
- **Consistency:** SQL strong/ACID; many NoSQL eventual (tunable).
- **Query:** SQL is powerful/standard; NoSQL queries are model-specific and simpler.

**Q4. When would you choose NoSQL over SQL?**
When you have huge scale/throughput, flexible or rapidly changing schema, simple access patterns (key lookups), or need multi-region high availability. Choose SQL when you need complex queries/joins, strong consistency, and multi-row transactions (e.g., financial systems).

---



## B. CAP, BASE & Consistency

**Q5. Explain the CAP theorem in the NoSQL context.**
Under a network partition, you can guarantee **Consistency** or **Availability**, not both.

- **CP** systems (e.g., MongoDB default, HBase) sacrifice availability to stay consistent.
- **AP** systems (e.g., Cassandra, DynamoDB, Riak) stay available and reconcile later (eventual consistency).

**Q6. What is BASE (vs ACID)?**
NoSQL often follows **BASE**: **B**asically **A**vailable, **S**oft state, **E**ventually consistent — the opposite philosophy of ACID. It favors availability and performance over immediate consistency.

**Q7. What is eventual consistency? Give an example.**
Replicas may temporarily disagree, but converge to the same value if writes stop. Example: you update your profile picture; a friend in another region might see the old one for a second until replication catches up.

**Q8. What is tunable consistency (quorum)?**
Systems like Cassandra let you choose consistency *per query* via read (R) and write (W) counts against N replicas. If **R + W > N**, you get strong consistency; lower values favor speed/availability.
Example (N=3): `W=QUORUM(2), R=QUORUM(2)` → strong; `W=1, R=1` → fast but possibly stale.

---



## C. Key-Value Stores (Redis / DynamoDB)

**Q9. What is a key-value store and when is it ideal?**
The simplest model: a giant hash map of key → value. Blazing-fast O(1) lookups by key. Ideal for caching, session storage, rate limiting, and feature flags. Weakness: you can only query by key (no rich queries on the value).

**Q10. Why is Redis so fast, and what data structures does it offer?**
It's in-memory (RAM) and single-threaded for command execution (no lock contention). Beyond strings it offers hashes, lists, sets, sorted sets (ZSET), bitmaps, HyperLogLog, and streams.
Example uses: sorted set → leaderboard; list → job queue; string+TTL → cache; ZSET → rate limiter.

**Q11. How does Redis handle persistence?**

- **RDB:** periodic point-in-time snapshots (compact, risk losing recent writes).
- **AOF:** append-only log of every write (more durable, larger/slower).
Often both are used together.

**Q12. Key design principle in DynamoDB?**
Design around **access patterns**, not entities. Choose a good **partition key** (for even distribution) plus an optional **sort key** (for range queries within a partition). Use **single-table design** and secondary indexes (GSI/LSI) to serve multiple query patterns.

---



## D. Document Stores (MongoDB)

**Q13. What is a document database?**
Stores semi-structured documents (BSON/JSON) with nested fields and arrays. Each document is self-contained, and documents in a collection can have different fields (flexible schema).

```json
{ "_id": 1, "name": "Sam", "orders": [ {"id": 991, "total": 50} ] }
```

**Q14. Embedding vs referencing — the core modeling decision.**

- **Embed** related data inside a document when it's accessed together and bounded in size (one-to-few). Fast reads, no joins.
- **Reference** (store an ID pointing to another document) for one-to-many/large or independently-changing data, to avoid huge documents and duplication.

Example: embed a user's address in the user doc; reference orders (could be thousands) by `user_id`.

**Q15. Does MongoDB support joins and transactions?**
Yes-ish: `$lookup` in the aggregation pipeline does left-outer-join-like operations (less efficient than SQL joins), and modern MongoDB supports multi-document ACID transactions — but the idiomatic approach is to model data so you rarely need them.

**Q16. What is the aggregation pipeline?**
A multi-stage data-processing framework (`$match`, `$group`, `$sort`, `$project`, `$lookup`) — MongoDB's analog to complex SQL queries.

```js
db.orders.aggregate([
  { $match: { status: "paid" } },
  { $group: { _id: "$user_id", total: { $sum: "$amount" } } }
]);
```

**Q17. How does MongoDB scale?**
**Sharding** distributes documents across shards by a shard key; **replica sets** provide HA (one primary for writes, secondaries for reads/failover). Choosing a good shard key (high cardinality, even distribution) is critical to avoid hotspots.

---



## E. Wide-Column Stores (Cassandra)

**Q18. What is a wide-column store?**
Data is stored in rows identified by a key, but each row can have a huge, dynamic set of columns grouped into column families. Optimized for massive write throughput and horizontal scale.

**Q19. Why is Cassandra "query-first" (model around queries)?**
Cassandra has no joins and limited ad-hoc querying. You design tables to serve specific queries — often duplicating data across multiple tables (one per query pattern). You must know your queries before designing the schema.

**Q20. Explain partition key vs clustering key in Cassandra.**

- **Partition key:** decides which node stores the row (distribution). Queries must include it.
- **Clustering key:** orders rows *within* a partition (enables range scans/sorting).

```
PRIMARY KEY ((user_id), created_at)
-- partition by user_id, rows sorted by created_at within each user
```

**Q21. Why is Cassandra write-heavy optimized?**
Writes are appended to a commit log + in-memory memtable, then flushed to immutable **SSTables** (LSM-tree). No in-place updates or read-before-write, so writes are extremely fast. Reads may merge multiple SSTables (compaction keeps this efficient).

**Q22. How does Cassandra achieve high availability?**
Peer-to-peer (no master), data replicated to multiple nodes, gossip protocol for membership, and tunable consistency. Any node can serve any request; there's no single point of failure.

---



## F. Graph Databases (Neo4j)

**Q23. What is a graph database and when is it the right choice?**
Stores data as **nodes** (entities) and **edges** (relationships), both with properties. Ideal when relationships are first-class and you traverse them a lot — social networks, fraud detection, recommendations, knowledge graphs.

**Q24. Why not just use SQL joins for relationships?**
Deep/variable-length traversals ("friends of friends of friends") require many expensive recursive joins in SQL. Graph DBs store relationships directly (index-free adjacency), so traversals are constant-time per hop regardless of total data size.
Example (Cypher): `MATCH (a:Person)-[:FRIEND*2]->(fof) WHERE a.name='Sam' RETURN fof`.

---



## G. Modeling, Indexing & Operations

**Q25. How does data modeling differ in NoSQL vs SQL?**
SQL: model the *data* (normalize, then query). NoSQL: model the *queries/access patterns* first, then denormalize to serve them efficiently — even if it means duplicating data.

**Q26. How is denormalization handled and what's the trade-off?**
You duplicate data so a read hits one place (fast, no joins). The trade-off: writes get harder — you must update all copies, and risk temporary inconsistency. NoSQL favors fast reads over write simplicity.

**Q27. Do NoSQL databases have indexes?**
Yes. MongoDB supports secondary/compound/text/geo indexes; DynamoDB has GSIs/LSIs; Cassandra has (limited) secondary indexes. But scans without a suitable index/partition key are expensive, so indexing/partitioning strategy is central.

**Q28. What is a hotspot / hot partition and how do you avoid it?**
When one partition key gets disproportionate traffic (e.g., partitioning by `country` when 90% are one country), that node is overwhelmed while others idle. Avoid with high-cardinality, evenly-distributed keys, or by salting/bucketing hot keys.

**Q29. How do NoSQL databases handle conflicts from concurrent writes?**
Options: **last-write-wins** (timestamp-based, can lose data), **vector clocks** to detect concurrent versions, or **CRDTs** for automatic conflict-free merges. DynamoDB/Cassandra commonly use LWW; Riak historically exposed vector clocks.

**Q30. What is a TTL and where is it useful?**
Time-to-live auto-expires records after a set duration — perfect for caches, sessions, and ephemeral data. Supported natively in Redis, DynamoDB, Cassandra, MongoDB.

---



## H. Comparison & Decision Questions (senior favorites)

**Q31. "You're designing X — SQL or NoSQL, and which NoSQL?" How do you reason?**
Anchor on **access patterns + consistency needs + scale**:

- Complex relationships/transactions, moderate scale → **SQL**.
- Simple key lookups, caching, sessions → **key-value (Redis)**.
- Flexible nested app documents, varied queries → **document (MongoDB)**.
- Massive write throughput / time-series / known queries → **wide-column (Cassandra)**.
- Deep relationship traversal → **graph (Neo4j)**.

**Q32. Can NoSQL be ACID / strongly consistent?**
Increasingly yes. MongoDB has multi-document transactions; DynamoDB offers transactions and strongly-consistent reads; Google Spanner is a globally-distributed strongly-consistent store. The old "NoSQL = no ACID" rule is outdated — it's now about trade-offs you can tune.

**Q33. What is polyglot persistence?**
Using multiple databases in one system, each for what it's best at — e.g., PostgreSQL for orders (transactions), Redis for caching/sessions, Elasticsearch for search, Cassandra for event logs. Common in modern architectures.

**Q34. How do you keep a NoSQL store in sync with a system of record?**
Patterns like **CDC** (change data capture) streaming DB changes, the **outbox pattern** for reliable event publishing, or dual writes (risky). Example: writes go to PostgreSQL; CDC streams changes to Elasticsearch so search stays fresh.

---



## I. Rapid-fire one-liners

- **Sharding vs replication:** sharding splits data (scale writes/storage); replication copies data (HA + read scaling). Most systems do both.
- **Strong vs eventual consistency:** strong = always latest, higher latency; eventual = fast, may be stale briefly.
- **Redis vs Memcached:** both in-memory caches; Redis has richer data types + persistence + pub/sub; Memcached is simpler, multi-threaded, pure cache.
- **Document vs wide-column:** document = flexible nested JSON, varied queries; wide-column = massive scale, query-first fixed access patterns.
- **Why avoid joins in NoSQL:** they don't scale horizontally well; denormalize instead.
- **BSON:** MongoDB's binary JSON — adds types (dates, ObjectId, binary) and is faster to parse.
- **LSM-tree vs B-tree:** LSM (Cassandra) optimizes writes (append + compaction); B-tree (SQL) optimizes reads/updates in place.
- **Secondary index caution (Cassandra):** can be slow/anti-pattern on high-cardinality or high-write columns — prefer a purpose-built table.

---



## Most-asked design/scenario questions to practice

1. Design a data model for an e-commerce catalog in MongoDB (embed vs reference).
2. Design a Cassandra schema for time-series/IoT data (partition + clustering keys).
3. When would you pick DynamoDB over MongoDB (and vice versa)?
4. Explain eventual consistency to a non-expert with an example.
5. How would you use Redis to build a rate limiter / leaderboard / cache?
6. Model a social network's "friends of friends" — why a graph DB?
7. How do you prevent hot partitions at scale?
8. SQL vs NoSQL for a banking ledger — defend your choice.



### How to debug MongoDB when its performance is degraded (Step-by-step)

1. **Confirm the problem is DB-side:**
   - Is the app, network, or cache slow — or is MongoDB actually the bottleneck? Check end-to-end latency breakdown if available.

2. **Check server and DB health:**
   - Run `mongostat` and `mongotop` to see basic metrics: inserts, queries, updates, flushes, locking, and collection-level activity.

3. **Look for obvious bottlenecks:**
   - Is **CPU**, **RAM**, or **disk I/O** spiking on the MongoDB box (via `top`, `htop`, `iostat`, or cloud metrics)?
   - Is **swap** being used? That’s bad — MongoDB needs to stay in RAM.

4. **Check for slow operations:**
   - Look in the **MongoDB logs** (`/var/log/mongodb/mongod.log` by default) for `"slow query"` entries (control with `slowms`).
   - You can also run:  
     ```js
     db.system.profile.find({ millis: { $gt: 100 } }).sort({ ts: -1 }).limit(10)
     ```
     (Requires **profiling** to be on.)

5. **Identify top slow queries:**
   - Use the **Atlas Performance Advisor** (if in Atlas), or manually aggregate `system.profile` to see most frequent/slow ops.

6. **Explain the slowest queries:**
   - Run `.explain("executionStats")` on the worst-performing operations.  
     Example:
     ```js
     db.orders.find({ user_id: X }).sort({ created_at: -1 }).limit(20).explain("executionStats")
     ```
   - Look for **COLLSCAN** (collection scan) = no useful index.

7. **Check your indexes:**
   - Run `db.collection.getIndexes()` — are there missing or suboptimal indexes for common queries? Slow queries often are missing indexes, or using them inefficiently.

8. **Check write performance:**
   - Are there lots of `update`, `insert`, or `delete` operations waiting? Are **write locks** high?
   - In logs or `mongostat`, high `locked %` (pre-4.0) is bad.

9. **Monitor replication/cluster state (if sharded/replicated):**
   - Are there replication lags? Run `rs.status()` for replica sets.
   - In a sharded cluster: are certain shards "hotter" than others (=unbalanced workload)? (`db.collection.getShardDistribution()`)

10. **Look for hardware/resource problems:**
    - Is storage nearly full? Any alerts from the host/VM/cloud provider?
    - Is the working set (hot data) able to fit in RAM?
    - Any recent changes or spikes (schema, deploys, traffic)?

**Summary:**  
> Always start with high-level system checks, then drill down: slow queries → missing indexes → resource exhaustion → sharding/replication issues.

**If you fix a slow query, always re-measure to confirm improvement.**

---