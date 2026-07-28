# Redis / Memcached

> Two classic **in-memory** stores. Memcached is a simple distributed KV cache. Redis is a richer data-structure server (and often more than a cache). Seniors pick by **data model need**, not brand loyalty.

## Plain English

| | **Memcached** | **Redis** |
|---|---------------|-----------|
| Model | Plain key → blob | Strings, hashes, lists, sets, sorted sets, streams, … |
| Persistence | None (pure cache) | Optional AOF/RDB |
| Clustering | Client-side sharding | Cluster / Sentinel / managed |
| Multithreading | Multi-threaded | Mostly single-threaded event loop (I/O threads in newer versions) |
| Sweet spot | Simple object cache at huge QPS | Cache + queues, locks, counters, pub/sub |

Both live in RAM → microsecond–low-ms latency. Neither replaces your database of record for durable business data (unless you deliberately design for that and accept risk).

```text
  App ──GET key──► Redis/Memcached
         │              │
         │ hit          │ miss
         ▼              ▼
      return          load DB → SET → return
```

## Essentials (must-know for this topic)

### Redis vs Memcached — what belongs in the comparison

| Dimension | **Memcached** | **Redis** |
|-----------|---------------|-----------|
| Data model | Opaque bytes (KV only) | Strings, hashes, lists, sets, zsets, streams, … |
| Persistence | None | Optional RDB / AOF |
| Eviction / TTL | Yes (simple) | Rich policies + per-key TTL |
| Replication / HA | Limited story | Sentinel / Cluster / managed |
| Extra jobs | Cache only | Locks, counters, pub/sub, light queues |
| Threading | Multi-threaded | Mostly single-threaded event loop |

### Key terms

| Term | Meaning |
|------|---------|
| **Hit / miss** | Key found in cache vs must load origin |
| **TTL** | Max age before entry expires |
| **Eviction** | Drop entries under memory pressure |
| **Source of truth** | Durable DB — cache is a speed layer |
| **Hot key** | One key absorbs disproportionate traffic |

**Rule of thumb:** Memcached = dumb fast blob cache. Redis = cache + coordination primitives. Don’t put money in either without a durability design.

## Simple example

**Session + product catalog:**

```text
  Memcached:  session:{sid} → opaque blob, TTL 30m
  Redis:      product:{id}  → HASH {name, price, stock}
              cart:{user}   → HASH sku → qty
              likes:{post}  → INCR (counter)
```

Memcached wins if you only need “blob in, blob out.” Redis wins the moment you need atomic increments, sorted leaderboards, or a short-lived lock.

## When to use / trade-offs

| Prefer **Memcached** when… | Prefer **Redis** when… |
|----------------------------|------------------------|
| Simple KV cache only | You need structures, TTL per field patterns, Lua, streams |
| Very high QPS, multi-core cache nodes | Cache + rate limit + lock on one platform |
| You want “dumb cache, fail open” | You may persist or replicate intentionally |

| Decision | You gain | You give up |
|----------|----------|-------------|
| In-memory cache | Speed, DB offload | Volatility; memory cost |
| Redis richness | One tool, many patterns | Ops complexity; misuse as primary DB |
| Memcached simplicity | Hard to over-engineer | No structures; no persistence story |

## Pitfalls

- Treating Redis as the **source of truth** for money without durability design.
- Huge values (multi-MB) → latency spikes and eviction thrash.
- No TTL on unbounded keyspaces → OOM.
- Assuming Redis is “single-threaded so slow” — for network-bound cache work it’s often fine; CPU-heavy Lua/scripts can block others.

## Interview trigger phrase

> “I’d default to **Redis** when I need structures or multi-purpose primitives; **Memcached** if I only need a simple distributed blob cache. Either way the DB stays the source of truth.”

## Exercise

**Choose a store for three keys.**

1. User session blob (opaque, 30 min).  
2. Real-time “online viewers” counter per livestream.  
3. Top-10 leaderboard by score with ties.  

For each: Redis or Memcached, which Redis type if Redis, and why.
