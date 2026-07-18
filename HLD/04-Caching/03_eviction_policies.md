# Eviction Policies

> When the cache is **full** (or an entry is **stale**), something must leave. **LRU**, **LFU**, and **TTL** are the policies interviewers expect you to choose with a workload story — not buzzwords.

## Plain English

| Policy | Evicts… | Works well when… |
|--------|---------|------------------|
| **LRU** (least recently used) | Entries not touched lately | Temporal locality — “hot set” shifts smoothly |
| **LFU** (least frequently used) | Rarely accessed overall | Stable popularity skew (always-hot catalog) |
| **TTL** | Entries past expiry | Freshness bound; soft upper age on data |
| **LRU + TTL** | Common combo | Memory pressure *and* max staleness |
| **Random / FIFO** | Simple victims | Benchmarks / when policy cost matters more |

TTL is not only an eviction policy — it’s a **correctness budget** (“at most N seconds stale”).

```text
  Cache capacity full
           │
           ▼
  ┌────────────────────────────┐
  │  Policy picks victim       │
  │  LRU: oldest untouched     │
  │  LFU: lowest hit count     │
  │  TTL: expired first / also │
  │       expire in background │
  └────────────────────────────┘
           │
           ▼
  Free slot → insert new entry
```

## Simple example

**Music streaming metadata cache (10GB Redis):**

```text
  Track metadata   → LRU + TTL 24h   (users browse recently played)
  Global top-100   → LFU or pinned   (always hot; don’t let one-off scans evict)
  Search typo keys → short TTL 60s   (huge cardinality; must die fast)
```

A one-time analytics scan touching 2M cold keys under pure LRU can **evict the working set** (cache pollution). Mitigate with separate caches, size caps per keyspace, or tiny TTLs on scan paths.

## Why prefer one over the other

| Prefer **LRU** when… | Prefer **LFU** when… |
|----------------------|----------------------|
| Working set = “recent” | Working set = “popular forever” |
| Default for most app caches | You can afford frequency tracking |

| Prefer **short TTL** when… | Prefer **long TTL + invalidate** when… |
|----------------------------|----------------------------------------|
| Stale is costly; writes rare to signal | Hit rate matters; you have a solid invalidation path |
| Keyspace is huge / abusive | Keys are well-known product IDs |

**Not “LFU always beats LRU.”** LFU can keep ancient popular keys forever and adapt slowly to shifts; LRU adapts faster but can be scanned away.

## Trade-offs

| Policy | You gain | You give up |
|--------|----------|-------------|
| LRU | Simple, adapts to recency | Scan / one-hit wonders pollute |
| LFU | Protects true hot keys | Cold-start bias; slower to forget old celebs |
| TTL-only | Bounded staleness | May evict still-hot keys; need memory too |
| Tiny cache | Cheap | Constant origin load |
| Huge cache | Hit rate | Cost; longer inconsistency windows if no TTL |

## Interview trigger phrase

> “I’d use **LRU plus TTL** for general object caches, **pin or LFU** the true global hot set, and **short TTLs** on high-cardinality keys so one-off scans can’t wash out the working set.”

## Exercise

**Tune eviction for an e-commerce Redis.**

1. Product pages, “recently viewed,” and unbounded autocomplete fragments — policy/TTL for each.  
2. Black Friday: traffic shifts to new SKUs overnight — how does LFU vs LRU behave?  
3. Cache hit rate is high but p99 spikes after a bulk CSV import touch — what pollution happened?
