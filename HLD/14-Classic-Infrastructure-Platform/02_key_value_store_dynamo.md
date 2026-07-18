# Design a Key-Value Store (Dynamo-style) 🔴

> **Crux:** Partition with **consistent hashing**, replicate for durability, and expose **tunable consistency** via quorum (`R`/`W`/`N`) — not a single primary for everything.

## Clarify (say this first)

**Functional**
- `put(key, value)` / `get(key)` — opaque blobs
- Optional: versioning / conflict detection
- TTL / deletes (tombstones)
- Range queries? (usually **out of scope** for Dynamo)

**Non-functional**
- Always-writable under partitions (AP / PA-EL lean)
- Tunable: latency vs freshness via `R`/`W`
- Multi-AZ; survive node + rack failure
- Millions of keys; high write QPS

## Back-of-envelope

```text
1B keys × 1 KB avg ≈ 1 PB raw; RF=3 → ~3 PB on disk
100k write QPS → ~100 MB/s ingest (1 KB values) before amplification
N=3, W=2, R=2 → R+W>N strong-ish read-after-write for that key
Partition count: thousands of virtual nodes / tokens across cluster
```

## API + data model

```text
PUT /v1/kv/{key}   body={value, context?}
GET /v1/kv/{key}   → {value, context} | conflicts[]
DEL /v1/kv/{key}
```

| Entity | Fields |
|--------|--------|
| Item | `key`, `value`, `vector_clock` / version, `timestamp` |
| Preference list | ordered N nodes for key |
| Sloppy quorum | first N *healthy* in list |

## High-level architecture

```text
  Client
    │
    ▼
  Coordinator (any node)
    │  hash(key) → preference list [N1,N2,N3,...]
    │
    ├─ put: send to N replicas, wait W acks
    └─ get: read R replicas, reconcile versions

  Nodes on consistent-hash ring
  ┌────┐ ┌────┐ ┌────┐ ┌────┐
  │ N1 │─│ N2 │─│ N3 │─│ N4 │ ...
  └────┘ └────┘ └────┘ └────┘
     │ hinted handoff / anti-entropy (Merkle)
```

## Deep dive: the crux

**Partitioning:** key → token on ring; owner = first clockwise; **vnodes** for balance. Preference list = next N distinct nodes (or racks).

**Tunable consistency:**
| Setting | Behavior | When |
|---------|----------|------|
| `W=N, R=1` | Fast reads; durable writes | Read-heavy, can wait on write |
| `W=1, R=N` | Fast writes; careful reads | Write-heavy ingest |
| `R+W>N` | Overlap → see latest (if no fork) | Default “read-your-writes” story |
| `W=1, R=1` | Max availability | Stale OK; conflicts later |

**Conflicts:** vector clocks detect concurrent writes; client merge or LWW. **Hinted handoff** + **Merkle tree sync** repair after failures. **Sloppy quorum** keeps writes alive if preferred nodes down.

**Pick for interview:** N=3, W=2, R=2; vector clocks; eventual anti-entropy — Dynamo paper story.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Leaderless + quorum | Write availability under partitions | Conflict handling complexity |
| Consistent hash | Incremental scale | Membership / rebalance care |
| Sloppy quorum | Survive preferred-node outage | Temporary wrong homes |
| LWW | Simple | Silent data loss on concurrent writes |
| Strong quorum always | Fewer surprises | Higher latency / less availability |

## Failure modes & scale

- **Node down:** hinted handoff to neighbor; replay when back
- **Network partition:** both sides accept writes → divergent versions → merge
- **Hot partition:** popular key range — salt key or split vnode
- **Read repair:** sporadic GET fixes replicas; background Merkle for bulk
- **Scale-out:** add nodes → steal token ranges; stream data; dual-write during move

## Interview trigger phrase

> “I’d use a **consistent-hash ring with N replicas** and let the client pick **R/W quorums** so we can trade latency for consistency — default **N=3, R=2, W=2**, with vector clocks for concurrent writes.”

## Exercise

1. With N=3, can W=2 and R=2 guarantee you never read stale after a successful put? Caveats?  
2. Two clients write the same key during a partition — what does the next GET return?  
3. Why hinted handoff alone isn’t enough — what does anti-entropy add?
