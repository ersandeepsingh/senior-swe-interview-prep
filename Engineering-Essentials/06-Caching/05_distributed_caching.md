# Distributed Caching

> One Redis box won’t hold the world. Distributed caching means **sharding**, **routing**, and surviving **hot keys** and **stampedes** when many nodes and clients share the load.

## Plain English

| Concern | What it means |
|---------|----------------|
| **Sharding** | Split keyspace across nodes (hash slots / shards) |
| **Consistent hashing** | Add/remove nodes without reshuffling *everything* |
| **Replication** | Replicas for read scale / HA (failover story) |
| **Hot key** | One key gets disproportionate traffic |
| **Cache stampede / thundering herd** | Many clients miss the same key at once and hammer the DB |

```text
  Keys ──hash──► shard A / B / C
                      │
                 hot key "celeb"
                      │
                 one shard melts 🔥
```

## Essentials (must-know for this topic)

### Core distributed-cache vocabulary

| Term | Meaning |
|------|---------|
| **Shard / partition** | Slice of keyspace on one node |
| **Consistent hashing** | Add/remove nodes with minimal key remapping |
| **Replica** | Copy for HA / read scale (lag possible) |
| **Hot key** | One key overwhelms a shard |
| **Cache stampede / thundering herd** | Many clients miss same key → hammer DB |
| **L1 + L2** | In-process cache in front of shared Redis |

### Stampede mitigations (know 3)

| Technique | Idea |
|-----------|------|
| **Singleflight / coalescing** | One loader; others wait on same key |
| **Lock (SETNX)** | Winner loads DB; losers serve stale or wait |
| **TTL jitter** | Don’t expire a million keys at once |
| **Soft TTL / early refresh** | Refresh before hard expiry on a fraction of requests |
| **Hot-key split / local cache** | Replicate or shard the celebrity key |

**Client-side sharding vs Redis Cluster:** app hashes keys vs server-managed hash slots — same goal, different ops story.

## Simple example

**Consistent hashing (idea):**

```text
  Ring: 0 … 2^32
  Nodes hashed onto ring; key goes to next clockwise node
  Add node D → only nearby keys move (not full remap)
```

**Stampede control for `product:1` after expiry:**

```text
  1. Singleflight / request coalescing — one loader, others wait
  2. Probabilistic early refresh / soft TTL
  3. Lock (SETNX) — winner loads DB; losers serve stale or wait
  4. Jitter TTLs so keys don’t expire in sync
```

**Hot key mitigations:** local in-process cache, replicate key to many nodes, split key (`likes:post:shardN`), CDN for public reads.

## When to use / trade-offs

| Prefer **client-side sharding** when… | Prefer **Redis Cluster / managed** when… |
|---------------------------------------|------------------------------------------|
| Simple Memcached pools | You want server-managed slots + resharding |
| Full control in app | Less custom routing code |

| Prefer **local + distributed** when… | Prefer **distributed only** when… |
|--------------------------------------|-----------------------------------|
| Extreme hot keys / ultra-low latency | Consistency across app instances matters more |
| Read-heavy public objects | Memory per instance is tight |

| Decision | You gain | You give up |
|----------|----------|-------------|
| More shards | Capacity, parallelism | Cross-key ops harder; ops complexity |
| Replicas | HA, read scale | Replication lag; failover drama |
| Local L1 cache | Hot-key relief | Another invalidation layer |

## Pitfalls

- Hot partition: celebrity key pins one shard CPU/network.  
- No jitter → mass expiry → DB meltdown.  
- Multi-key transactions across shards (Redis Cluster limits).  
- “Cache is down” without **fail-open / degrade** plan → total outage instead of slower path.

## Interview trigger phrase

> “I’d shard with **consistent hashing or Redis Cluster**, add **TTL jitter** and **singleflight** against stampedes, and treat **hot keys** with L1 cache or key splitting — not just ‘buy a bigger box.’”

## Exercise

**Black Friday product page.**

1. One SKU is 40% of traffic — three mitigations you’d propose.  
2. Cache cluster loses a node — what happens to keys, and how do clients behave?  
3. Design stampede protection for a 5-second DB query that caches for 60s.
