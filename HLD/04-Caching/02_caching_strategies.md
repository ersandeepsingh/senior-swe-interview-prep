# Caching Strategies

> How reads and writes interact with the cache: **cache-aside**, **read-through**, **write-through**, and **write-back (write-behind)**. The strategy decides who loads the cache and when the DB sees writes.

## Plain English

| Strategy | Read path | Write path |
|----------|-----------|------------|
| **Cache-aside (lazy)** | App: get → miss → DB → put | App writes DB, then deletes/updates cache |
| **Read-through** | Cache lib loads DB on miss | Usually paired with write-through / aside |
| **Write-through** | As above | Write cache **and** DB synchronously |
| **Write-back** | Hit cache | Write cache first; flush to DB later (async) |

Cache-aside is the interview default for app-owned Redis. Write-back is for write-heavy workloads that can tolerate delay/loss risk with care.

```text
  Cache-aside READ:                 Write-through:
  App → Redis → miss → DB           App → Redis + DB (sync)
         │              │                  │
         └── put ◄──────┘                  └─ both durable before OK

  Write-back:
  App → Redis (OK) ⋯ async ⋯► DB
```

## Simple example

**User profile service:**

```text
  Cache-aside (typical):
    GET profile:{id}
      hit  → return
      miss → SELECT → SET profile:{id} TTL 10m → return
    PUT profile
      → UPDATE DB → DEL profile:{id}   (invalidate)

  Write-heavy game inventory (careful):
    Write-back buffer per shard → flush every 100ms / 1k ops
    On node crash → acknowledge loss window unless WAL’d
```

Most CRUD APIs: **cache-aside + invalidate on write**. Don’t write-back payment balances.

## Why prefer one over the other

| Prefer **cache-aside** when… | Prefer **read-through** when… |
|------------------------------|-------------------------------|
| App controls keys/TTLs clearly | You want caching opaque in a library/sidecar |
| Simple Redis + service code | Multiple apps share same cache loader |

| Prefer **write-through** when… | Prefer **write-back** when… |
|--------------------------------|-----------------------------|
| Read-after-write must see fresh data in cache | Extreme write QPS; coalesce updates |
| Simpler correctness than write-back | You can accept async durability + replay |

**Not “write-through is always safer than cache-aside.”** Cache-aside + DB-first write + delete is a solid, common pattern. Write-through still needs failure handling if one of two stores fails.

## Trade-offs

| Strategy | You gain | You give up |
|----------|----------|-------------|
| Cache-aside | Explicit control; easy to reason | App must handle miss logic; stampede risk |
| Write-through | Cache warm after writes | Higher write latency |
| Write-back | Fast writes; fewer DB writes | Durability risk; complex flush/retry |
| Update cache on write (vs delete) | Hot keys stay warm | Race: stale overwrite if not careful |

## Interview trigger phrase

> “Default is **cache-aside**: read fills Redis on miss, writes go to the DB then **invalidate** the key. I’d only use **write-back** for coalescable, non-critical counters — never for money.”

## Exercise

**Pick strategies for a social app.**

1. Profile bio, “like” counters, and payment card-on-file — one strategy each, why.  
2. Write-through succeeds on Redis but fails on DB — what should the API return, and what’s dirty?  
3. After cache-aside invalidate, a concurrent reader repopulates stale DB data — name the race and one mitigation.
