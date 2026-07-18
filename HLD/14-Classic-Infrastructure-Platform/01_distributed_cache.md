# Design a Distributed Cache 🔴

> **Crux:** Place keys on a growing fleet with **consistent hashing** (minimal remaps) and keep values honest with a clear **invalidation** story — not just “put Redis in front.”

## Clarify (say this first)

**Functional**
- `GET` / `SET` / `DEL` by key; optional TTL
- Multi-tenant namespaces (optional)
- Cache-aside vs read-through (pick one for the round)
- Eviction when memory full (LRU/LFU)

**Non-functional**
- Latency: sub-ms–few ms p99 on hit
- Availability: survive node loss without full flush
- Consistency: stale window OK vs must invalidate on write
- Scale: 100k–1M+ ops/s; tens–hundreds of nodes

## Back-of-envelope

```text
Assumptions: 50M active keys, avg value 2 KB, 200k QPS (80% hit)
Working set ≈ 50M × 2KB ≈ 100 GB → ~20 nodes × 8–16 GB usable
Hit path: 200k × 0.8 = 160k cache ops/s across ring
Miss path: 40k QPS to origin DB
On add 1 node: remapped ≈ 1/N of keys (~5%) if consistent hash + vnodes
```

## API + data model

```text
GET  /cache/{ns}/{key}
PUT  /cache/{ns}/{key}   body={value, ttl_sec?}
DEL  /cache/{ns}/{key}
```

| Entity | Fields |
|--------|--------|
| Entry | `ns`, `key`, `value`, `ttl`, `version?` |
| Node | `node_id`, `vnode_tokens[]`, `capacity` |
| Ring | membership view + hash function |

## High-level architecture

```text
  Clients / App servers
           │
           ▼
     ┌───────────┐
     │  Router / │  hash(key) → owner (+ replicas)
     │  proxy    │
     └─────┬─────┘
           │
    ┌──────┼──────┐
    ▼      ▼      ▼
  Cache  Cache  Cache   ← memory + LRU; optional replica copies
  N1     N2     N3
           │
           │ miss / write-through
           ▼
       Origin DB / service
```

## Deep dive: the crux

**Placement:** `hash % N` remaps almost everything on resize. **Consistent hashing + virtual nodes** remaps ~`1/N` and spreads load.

**Invalidation:**
| Approach | When |
|----------|------|
| TTL-only | Slightly stale OK (feeds, sessions) |
| DEL on write (cache-aside) | Default; writer updates DB then deletes key |
| Versioned keys | Contested keys; kill stale SET races |
| Pub/sub flush | Many local in-process caches |

**Pick:** ring + vnodes for the fleet; **DB write → DEL + short TTL safety net**; version hot keys. Replicate each key to N successors for availability — accept brief replica staleness or use primary-only reads.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Consistent hash + vnodes | Scale without stampede | Harder “who owns key?” debugging |
| Cache-aside + DEL | Simple coherence | Extra miss after every write |
| Multi-replica cache | Survive node death | Stale/inconsistent reads possible |
| Aggressive LRU | Bound memory | Cold misses under churn |
| Write-through | Fresher cache | Write latency + origin coupling |

## Failure modes & scale

- **Node death:** remount keys on neighbors; expect miss storm → request coalescing + jittered TTL
- **Hot key:** one vnode overloaded → local replicas, client-side cache, or key salting
- **Split brain membership:** two rings → wrong owner; use gossip + epoch / config service
- **Invalidation loss:** pub/sub drop → rely on TTL; never assume perfect flush
- **Scale:** add nodes gradually; migrate only remapped arcs; monitor hit ratio & eviction rate

## Interview trigger phrase

> “I’d put the cache on a **consistent-hash ring with vnodes** so add/remove remaps ~`1/N` of keys, and on write I’d **update the source then delete the cache key**, with TTL as a safety net.”

## Exercise

1. App grows from 8 → 16 cache nodes — contrast remapping with `% N` vs consistent hash.  
2. Flash-sale SKU is a hot key — three mitigations and which you’d ship first.  
3. Writer deletes cache key but a slow reader SETs stale data back — how do versions fix it?
