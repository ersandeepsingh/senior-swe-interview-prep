# Caching Strategies

> How reads and writes interact with the cache: **cache-aside**, **read-through**, **write-through**, and **write-back**. The strategy decides who loads the cache and when the DB sees writes.

## Plain English

| Strategy | Read path | Write path |
|----------|-----------|------------|
| **Cache-aside (lazy)** | App: get → miss → DB → put | App writes DB, then deletes/updates cache |
| **Read-through** | Cache layer loads DB on miss | Usually paired with write-through / aside |
| **Write-through** | As above | Write cache **and** DB synchronously |
| **Write-back (write-behind)** | Hit cache | Write cache first; flush to DB later |

Cache-aside is the interview default for app-owned Redis. Write-back is for write-heavy workloads that can tolerate delay/loss risk with care.

```text
  Cache-aside READ:                 Write-through:
  App → Redis → miss → DB           App → Redis + DB (sync)
         │              │                  │
         └── put ◄──────┘                  └─ both OK before ACK

  Write-back:
  App → Redis (OK) ⋯ async ⋯► DB
```

## Essentials (must-know for this topic)

### Cache-aside vs read-through vs write-through vs write-back

| Strategy | Who loads on miss? | When does DB see writes? | Typical use |
|----------|--------------------|--------------------------|-------------|
| **Cache-aside** | **App** reads DB, then `SET` | App writes DB, then invalidate/update cache | Default app + Redis |
| **Read-through** | **Cache library/sidecar** loads DB | Often paired with write-through / aside | Shared loader across apps |
| **Write-through** | As above on read | Cache **and** DB updated **synchronously** | Need warm cache after writes |
| **Write-back (write-behind)** | Hit cache | Cache first; **async flush** to DB later | Coalesce high write QPS (careful) |

### Related terms that belong here

| Term | Meaning |
|------|---------|
| **Invalidate on write** | `DEL` key after DB success (common with cache-aside) |
| **Update on write** | Write new value into cache (keep hot keys warm; race risk) |
| **Read-your-writes** | Caller sees their own update immediately — favors write-through or careful invalidate |
| **Stampede** | Many clients miss the same key → thundering DB |

**Interview default:** cache-aside + DB write then invalidate. Avoid write-back for money/inventory without a durability story.

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
    On node crash → loss window unless WAL’d / replicated carefully
```

Most CRUD APIs: **cache-aside + invalidate on write**. Don’t write-back payment balances.

## When to use / trade-offs

| Prefer **cache-aside** when… | Prefer **read-through** when… |
|------------------------------|-------------------------------|
| App controls keys/TTLs clearly | You want caching opaque in a library/sidecar |
| Simple Redis + service code | Multiple apps share the same loader |

| Prefer **write-through** when… | Prefer **write-back** when… |
|--------------------------------|-----------------------------|
| Read-after-write must see fresh data in cache | Extreme write QPS; coalesce updates |
| Simpler correctness than write-back | You can accept async durability + replay |

| Strategy | You gain | You give up |
|----------|----------|-------------|
| Cache-aside | Explicit control; easy to reason | App handles miss logic; stampede risk |
| Write-through | Cache warm after writes | Higher write latency |
| Write-back | Fast writes; fewer DB writes | Durability risk; complex flush/retry |
| Update on write (vs delete) | Hot keys stay warm | Race: stale overwrite if not careful |

## Pitfalls

- Write-back for **financial** state without a clear durability story.
- Updating cache on write without versioning → **stale overwrite** races.
- Forgetting stampede control on popular keys after invalidate.
- Claiming write-through is “always safer” — both paths need failure handling when one of two stores fails.

## Interview trigger phrase

> “Default is **cache-aside**: read fills Redis on miss, writes go to the DB then **invalidate** the key. I’d only use **write-back** for coalescable, non-critical counters — never for money.”

## Exercise

**Pick strategies for a social app.**

1. Profile bio, “like” counters, and payment card-on-file — one strategy each, why.  
2. Write-through succeeds on Redis but fails on DB — what should the API return, and what’s dirty?  
3. After cache-aside invalidate, a concurrent reader repopulates stale DB data — name the race and one mitigation.
