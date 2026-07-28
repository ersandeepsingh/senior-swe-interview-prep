# Redis — Senior Engineer Revision

**What it is:** An in-memory data-structure store used as a cache, database, and message broker. Single-threaded for command execution, extremely fast (sub-millisecond), with rich data types and optional persistence.

---

## 1. Why Redis is fast
- **In-memory** — data lives in RAM, not disk.
- **Single-threaded command execution** — no lock contention, no context-switching; commands are atomic by nature. (Redis 6+ adds multi-threaded I/O for network, but command logic is still effectively serialized.)
- **Efficient data structures** implemented in C.

*Implication:* a slow command (e.g., `KEYS *`, big `SORT`) **blocks everything** because it's single-threaded. Never run O(N) blocking commands on large keysets in production.

---

## 2. Core data types (know which fits which problem)

| Type | Description | Typical use |
|---|---|---|
| **String** | bytes up to 512MB; ints for counters | cache values, counters, flags |
| **Hash** | field→value map | store an object (user:42 → {name, email}) |
| **List** | ordered linked list | queues, recent-activity feeds |
| **Set** | unordered unique members | tags, unique visitors, relationships |
| **Sorted Set (ZSET)** | set ordered by score | leaderboards, rate limiters, priority queues |
| **Bitmap** | bit operations on strings | daily active users, feature flags |
| **HyperLogLog** | probabilistic cardinality | count unique items in ~12KB |
| **Stream** | append-only log w/ consumer groups | event streaming, Kafka-lite |
| **Geospatial** | lat/long with radius queries | "nearby" features |

**Examples:**
```bash
# String counter (atomic)
INCR page:views              # -> 1, 2, 3...

# Hash as an object
HSET user:42 name "Sam" email "s@x.com"
HGETALL user:42

# Cache with expiry (TTL)
SET session:abc "{...}" EX 3600      # expires in 1 hour

# Sorted set leaderboard
ZADD leaderboard 100 "alice" 250 "bob"
ZREVRANGE leaderboard 0 9 WITHSCORES  # top 10

# Set operations
SADD user:1:follows 2 3 4
SINTER user:1:follows user:5:follows  # mutual follows
```

---

## 3. Key expiration & eviction (frequently asked)
- **TTL:** `EXPIRE key 60`, `SET key val EX 60`, `TTL key`. Keys auto-delete when expired.
- **Expiration is lazy + sampled:** deleted on access, plus a background sampler — so an expired key can briefly still occupy memory.
- **Eviction policies** (when `maxmemory` is hit):
  - `noeviction` — reject writes (default).
  - `allkeys-lru` / `allkeys-lfu` — evict least-recently/least-frequently used across all keys (typical for pure caches).
  - `volatile-lru` / `volatile-ttl` — evict only keys with a TTL.
- **LRU vs LFU:** LRU = recency; LFU = frequency (better when some keys are consistently hot).

---

## 4. Persistence (Redis as more than a cache)
- **RDB (snapshot):** periodic point-in-time dump. Compact, fast restart, but you can lose the writes since the last snapshot.
- **AOF (append-only file):** logs every write; replayed on restart. More durable (`fsync` every second by default), larger files, slower.
- **Both together** is common: AOF for durability + RDB for fast restarts.

*Trade-off to state:* Redis is not a guaranteed-durable database — even AOF `everysec` can lose ~1s of writes on crash. Don't treat it as a system of record unless you accept that.

---

## 5. Atomicity, transactions & Lua
- Every single command is atomic.
- **MULTI/EXEC** queues commands and runs them atomically (no other client interleaves), but **no rollback** on logical errors.
- **WATCH** enables optimistic locking (CAS): abort the transaction if a watched key changed.
- **Lua scripts** (`EVAL`) run atomically server-side — the right tool for "read-modify-write" logic that must be atomic (e.g., a correct rate limiter or conditional decrement).

```lua
-- Atomic "decrement stock if available"
if tonumber(redis.call('GET', KEYS[1])) > 0 then
  return redis.call('DECR', KEYS[1])
else
  return -1
end
```

---

## 6. Common backend patterns (interview gold)

**Cache-aside (most common):**
```
read: check Redis → hit? return; miss? read DB, write to Redis (with TTL), return
write: update DB, then invalidate/update the Redis key
```

**Rate limiting (fixed window):**
```bash
INCR user:42:req
EXPIRE user:42:req 60   # allow N per minute; reject if INCR result > N
```
(For accuracy use a sliding-window ZSET or a Lua script.)

**Distributed lock:**
```bash
SET lock:resource <uuid> NX EX 10   # acquire only if not set, auto-expire
# release via Lua: delete only if value == my uuid (avoid deleting someone else's lock)
```
*Caveat:* single-node locks can be lost on failover; **Redlock** spans multiple masters but is debated. Use fencing tokens for correctness-critical locks.

**Pub/Sub:** `SUBSCRIBE channel` / `PUBLISH channel msg` — fire-and-forget, **no persistence** (offline subscribers miss messages). For durable messaging use **Streams** instead.

**Streams (durable):** `XADD`, `XREAD`, consumer groups (`XREADGROUP`, `XACK`) — like a lightweight Kafka with at-least-once delivery and replay.

---

## 7. Scaling & HA (senior topics)
- **Replication:** primary → replicas (async). Replicas serve reads; async means possible small lag/data loss on failover.
- **Redis Sentinel:** monitors primaries, does automatic failover + service discovery. HA without sharding.
- **Redis Cluster:** shards data across nodes using **16384 hash slots** (key → CRC16 % 16384 → slot → node). Scales writes/memory horizontally.
  - **Multi-key ops must be in the same slot** — use **hash tags** `{user1}:profile`, `{user1}:cart` to co-locate related keys.
- **Client-side sharding / proxies** (e.g., twemproxy) are older alternatives.

---

## 8. Gotchas & senior talking points
- **Big keys** (huge lists/sets) and O(N) commands block the single thread — use `SCAN` not `KEYS`, avoid huge `HGETALL`.
- **Hot keys** overload a single shard — replicate or split.
- **Cache stampede/thundering herd:** many misses hit the DB at once when a popular key expires → use jittered TTLs, locks, or `EXPIRE` refresh-ahead.
- **Cache penetration:** requests for non-existent keys always miss and hit DB → cache negative results or use a bloom filter.
- **Memory fragmentation** and eviction under pressure — size `maxmemory` deliberately.
- **Persistence ≠ durability guarantee** — know the loss window.

---

## 9. Redis vs Memcached (classic question)
| | Redis | Memcached |
|---|---|---|
| Data types | rich (list/set/zset/hash/stream) | strings only |
| Persistence | yes (RDB/AOF) | no |
| Replication/HA | yes (Sentinel/Cluster) | no (client sharding) |
| Threading | single-threaded logic | multi-threaded |
| Pub/Sub, Lua, Streams | yes | no |

Use **Memcached** for a simple, multi-threaded, pure-cache; **Redis** for anything richer.

---

## 10. Quick interview Q&A
- **Why single-threaded and still fast?** In-memory + no lock contention; CPU rarely the bottleneck, network/memory is.
- **How does Redis handle failover?** Sentinel/Cluster detect a down primary and promote a replica (async replication → possible small data loss).
- **Strong consistency?** No — async replication and no rollback; it's AP-leaning. Use Lua for atomic multi-step logic.
- **How to cache safely?** Cache-aside + TTL + invalidation on write; guard against stampede (jitter/locks) and penetration (negative caching).
- **When NOT to use Redis?** As a durable system of record for critical data, or for huge datasets that don't fit economically in RAM.
