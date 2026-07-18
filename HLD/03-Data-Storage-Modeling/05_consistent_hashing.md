# Consistent Hashing

> Classic `hash(key) % N` **moves almost everything** when N changes. **Consistent hashing** places keys and nodes on a ring so adding/removing a node reshuffles only ~`1/N` of keys.

## Plain English

Nodes and keys map to points on a circle. A key belongs to the **first node clockwise** (or the nearest). Virtual nodes (vnodes) smear load so one physical server isn’t a hot arc.

```text
              key X
                │
         ┌──────▼──────┐
    N3 ●─┤             ├─● N1
         │   HASH RING │
    N2 ●─┤             │
         └─────────────┘
                │
         key Y owned by N1
         (walk clockwise to next node)

  Add N4 between N1 and N2:
    only keys in that arc move to N4
    rest stay put  ✓
```

| Approach | On add/remove node |
|----------|--------------------|
| `hash % N` | Most keys remapped |
| Consistent hash | ~`K/N` keys remapped |
| + vnodes | Smoother balance |

## Simple example

**Cache cluster:** 3 Redis nodes → add a 4th.

```text
  % N world:
    user:42 was on node 1 → suddenly node 2  💥 cache stampede

  Consistent hash:
    only keys whose arc now hits node 4 move
    others still hit warm cache
```

Same idea for **Dynamo-style** stores and CDN / edge caches.

## Why prefer one over the other

| Prefer **consistent hashing** when… | Prefer **simple % N / fixed shards** when… |
|-------------------------------------|--------------------------------------------|
| Nodes churn (autoscaling caches) | Stable shard count; rare reshard |
| You need minimal remapping | You control a planned migration tool |
| Distributed caches, DHT, some DBs | Static routing table is fine |

**Why virtual nodes?** One physical node → many positions on the ring → load more uniform; remove node → its vnodes’ keys spread to many peers, not one lucky neighbor.

**Why not always?** Debugging “who owns this key?” is harder; need a membership view everyone agrees on.

### Real systems (interview name-drops)

- **Caches / proxies:** Ketama, many Redis Cluster conceptual relatives.
- **Stores:** Amazon Dynamo paper; Cassandra token ring; Riak.
- **CDN / load balancing:** Maglev / ring-based peer selection variants.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Consistent hash ring | Minimal reshuffle on scale | More complex routing / membership |
| Virtual nodes | Better balance; safer removals | Larger ring metadata |
| Replication along ring (N successors) | Fault tolerance | Careful quorum / hinted handoff |
| Stick with `% N` | Dead simple | Cache wipe / data move on every resize |

**Common interview trap:** Saying “consistent hashing” without explaining **why** (`% N` remaps everything) or mentioning **virtual nodes** for hotspots.

## Interview trigger phrase

> “For a growing cache tier I’d use **consistent hashing with vnodes** so adding a node only remaps about `1/N` of keys instead of thrashing the whole cache.”

## Exercise

**Design cache placement for session data across 8 → 12 nodes.**

1. Sketch what happens to `session:user123` when you add 4 nodes with `% N` vs consistent hash.  
2. Why might one physical node still run hot even on a ring — and how do vnodes help?  
3. One sentence on whether you’d store durable user rows the same way as ephemeral cache keys.
