# 09 · Distributed Systems — Replication & Partitioning

> Copying data for safety/scale, and splitting data to fit and spread load.

---

## Replication models

**Definition:** Strategies for keeping copies of data on multiple nodes: **single-leader**, **multi-leader**, and **leaderless**.

**Simple explanation:**
- **Single-leader:** one node takes all writes, replicates to followers. Simple, consistent, but the leader is a write bottleneck/SPOF.
- **Multi-leader:** several nodes accept writes (e.g., one per region). Great for multi-region latency, but writes can conflict.
- **Leaderless (Dynamo-style):** any replica takes writes; consistency via quorums. Highly available, more complex reads.

**Example:**
- Single-leader: classic PostgreSQL primary + read replicas.
- Multi-leader: a DB with a writable node in US and EU for local low-latency writes, syncing across.
- Leaderless: Cassandra/DynamoDB writing to any node with quorum reads/writes.

---

## Sync vs async replication

**Definition:** Whether the leader waits for replicas to confirm a write (**sync**) before acknowledging the client, or acknowledges immediately and replicates in the background (**async**).

**Simple explanation:** Sync = durable and consistent (no data loss if leader dies) but slow (you wait for replicas). Async = fast (client isn't blocked) but risks losing recent writes if the leader crashes before replicating — and readers on replicas may see stale data (**replication lag**).

**Example:** Async: leader confirms `order placed`, then crashes 5ms later before the replica copied it → that order is lost on failover. Sync would have waited for the replica, so the order survives — but every order would have been slightly slower to confirm. Many systems use **semi-sync**: wait for at least one replica.

---

## Partitioning / sharding

**Definition:** Splitting a large dataset across multiple nodes so no single machine holds everything. Common schemes: range, hash, consistent-hash, directory.

**Simple explanation:** When data outgrows one machine, you divide it. **Range** partitioning splits by key ranges (A–M, N–Z) — good for range scans but prone to hotspots. **Hash** partitioning spreads keys evenly by hashing — good balance but kills range queries. **Directory** uses a lookup table for flexibility.

**Example:** A `users` table of 5B rows. Hash-partition by `user_id % 16` across 16 shards so load spreads evenly. Range partitioning by `signup_date` would instead pile all new users onto the newest shard — a hotspot.

---

## Consistent hashing

**Definition:** A hashing scheme that maps both data keys and nodes onto a ring, so adding/removing a node only relocates a small fraction of keys.

**Simple explanation:** Naive `key % N` reshuffles *almost everything* when N changes (a node added/removed) — catastrophic for caches. Consistent hashing places nodes around a ring; each key goes to the next node clockwise. Adding a node only steals keys from its neighbor. **Virtual nodes** (many ring positions per physical node) keep the load balanced.

**Example:** A 4-node cache using `key % 4`: adding a 5th node changes `% 4`→`% 5` and invalidates ~80% of entries (cache stampede). With consistent hashing, adding node 5 only moves ~20% of keys — the rest stay put.

---

## Rebalancing

**Definition:** Moving partitions between nodes when capacity changes, ideally without downtime or a huge data-movement storm.

**Simple explanation:** As you add nodes or data grows unevenly, you must redistribute partitions. Good rebalancing moves the *minimum* data, throttles the transfer so it doesn't saturate the network, and keeps serving traffic throughout. Fixed-number-of-partitions schemes make this predictable.

**Example:** A cluster pre-creates 256 partitions spread over 4 nodes (64 each). Adding a 5th node moves ~51 partitions over so each node holds ~51 — a bounded, controlled shuffle rather than a full re-hash.

---

## Read/write splitting

**Definition:** Directing writes to the leader/primary and reads to replicas to scale read-heavy workloads.

**Simple explanation:** Most apps read far more than they write. Sending reads to replicas offloads the primary and scales throughput. The catch: replication lag means a replica might not yet have a just-written value, causing "I saved it but don't see it" bugs. Mitigate with read-your-writes routing (send a user's reads to the primary briefly after they write).

**Example:** An analytics dashboard reads from 5 replicas (scaling reads 5x), while all `INSERT/UPDATE` go to the single primary. Right after a user updates their profile, their next read is routed to the primary so they see their own change immediately.

---

## Hot spots / skew

**Definition:** Uneven distribution where certain partitions receive disproportionate load, becoming bottlenecks.

**Simple explanation:** Even with sharding, one "celebrity" key or a monotonically increasing key can concentrate traffic on a single node while others idle. You fix it by adding randomness/salting to keys, splitting hot keys, or caching them separately.

**Example:** Sharding tweets by `user_id` works until a celebrity with 100M followers overwhelms their shard. Mitigation: give hot accounts a dedicated cache/fan-out path, or salt the key (`user_id + random_bucket`) to spread their writes across shards.
