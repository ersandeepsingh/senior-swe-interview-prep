# Eviction & TTL

> When the cache is **full** (or an entry is **stale**), something must leave. **LRU**, **LFU**, and **TTL** are the policies interviewers expect you to choose with a workload story — not buzzwords.

## Plain English

| Policy | Evicts… | Works well when… |
|--------|---------|------------------|
| **LRU** (least recently used) | Entries not touched lately | Temporal locality — “hot set” shifts smoothly |
| **LFU** (least frequently used) | Rarely accessed overall | Stable popularity skew |
| **TTL** | Entries past expiry | Freshness bound; soft upper age |
| **LRU + TTL** | Common combo | Memory pressure *and* max staleness |
| **Random / FIFO** | Simple victims | When policy cost matters more than precision |

TTL is not only eviction — it’s a **correctness budget** (“at most N seconds stale”). Redis `maxmemory-policy` (e.g. `allkeys-lru`, `volatile-ttl`) decides who dies under pressure.

```text
  Cache capacity full
           │
           ▼
  Policy picks victim → free slot → insert new entry
  Meanwhile: TTL expiry reclaims stale keys in background
```

## Essentials (must-know for this topic)

### LRU vs LFU vs TTL

| Policy | Evicts / expires… | Good for | Weakness |
|--------|-------------------|----------|----------|
| **LRU** | Least **recently** used | Shifting “hot set” / temporal locality | One-off scans pollute working set |
| **LFU** | Least **frequently** used | Stable popularity skew | Slow to forget yesterday’s viral key |
| **TTL** | Past expiry time | Bound staleness; reclaim high-cardinality keys | May expire still-hot keys; sync expiry → herd |
| **LRU + TTL** | Combo (common) | Memory pressure **and** max age | Still need invalidate for instant freshness |

### Redis memory knobs (name-drop)

| Setting / idea | Meaning |
|----------------|---------|
| `maxmemory` | Hard memory cap |
| `allkeys-lru` / `volatile-lru` | Evict any key vs only keys with TTL |
| `volatile-ttl` | Prefer keys closest to expiry |
| **Jittered TTL** | Randomize expiry to avoid synchronized stampedes |

**TTL ≠ invalidation:** TTL is a safety net; business-critical freshness still needs delete-on-write.

## Simple example

**E-commerce Redis (10GB):**

```text
  Product metadata   → LRU + TTL 24h   (browse recently viewed)
  Global top-100     → LFU or pinned   (always hot)
  Autocomplete fragments → TTL 60s     (huge cardinality; must die fast)
```

A one-time analytics scan touching millions of cold keys under pure LRU can **evict the working set** (cache pollution). Mitigate with separate caches, size caps, or tiny TTLs on scan paths.

## When to use / trade-offs

| Prefer **LRU** when… | Prefer **LFU** when… |
|----------------------|----------------------|
| Working set = “recent” | Working set = “popular forever” |
| Default for most app caches | You can afford frequency tracking |

| Prefer **short TTL** when… | Prefer **long TTL + invalidate** when… |
|----------------------------|----------------------------------------|
| Stale is costly; hard to invalidate | Hit rate matters; solid invalidation path |
| Keyspace is huge / abusive | Keys are well-known product IDs |

| Policy | You gain | You give up |
|--------|----------|-------------|
| LRU | Simple, adapts to recency | Scan / one-hit wonders pollute |
| LFU | Protects true hot keys | Slower to forget old celebs |
| TTL-only | Bounded staleness | May evict still-hot keys |
| Tiny cache | Cheap | Constant origin load |

## Pitfalls

- No `maxmemory` policy → Redis OOM / rejects writes.
- Same TTL on every key → synchronized expiry → **thundering herd**.
- LFU that never forgets a yesterday’s viral SKU after demand dies.
- Relying on TTL alone for correctness when business needs instant invalidate (price change, permissions).

## Interview trigger phrase

> “I’d use **LRU plus TTL** for general object caches, **pin or LFU** the true global hot set, and **short TTLs** on high-cardinality keys so one-off scans can’t wash out the working set.”

## Exercise

**Tune eviction for an e-commerce Redis.**

1. Product pages, “recently viewed,” and unbounded autocomplete fragments — policy/TTL for each.  
2. Black Friday: traffic shifts to new SKUs overnight — how does LFU vs LRU behave?  
3. Hit rate is high but p99 spikes after a bulk CSV import — what pollution happened?
