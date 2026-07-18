# Hot Key & Thundering Herd

> A **hot key** is one entry that attracts disproportionate traffic. A **thundering herd** (cache stampede) is many clients missing at once — often when a hot key **expires** — and stampeding the DB. Control it with **coalescing**, **locks**, and **jittered TTLs**.

## Plain English

| Problem | What happens |
|---------|----------------|
| **Hot key** | One Redis key / shard pegs CPU or bandwidth |
| **Hot shard** | Consistent-hash puts too many hots on one node |
| **Thundering herd** | TTL ends → N requests miss → N identical DB queries |
| **Stampede on deploy** | Empty cache after flush → origin melts |

| Mitigation | Idea |
|------------|------|
| **Request coalescing** | One miss loads; others wait for that result |
| **Soft/hard TTL / early refresh** | Refresh before expiry; only one refresher |
| **Jittered TTL** | Expire at t+random so keys don’t align |
| **Lock / single-flight** | `SETNX` lock around DB load |
| **Local + replicate hot key** | Copy hot value to many cache nodes / local mem |
| **Read replica / precompute** | Don’t hit primary for the same join 100k times |

```text
  Without protection (TTL hits 0):
  10k clients ──miss──► DB × 10k  💥

  With single-flight:
  10k clients ──miss──► one loader → DB × 1
                 └── waiters ←────┘
                      then fan-out result
```

## Simple example

**Celebrity profile on a social app** (`user:1` gets 40% of traffic):

```text
  Problems:
    - Redis CPU on shard owning user:1
    - TTL 60s aligned → herd every minute

  Fixes:
    1) jitter TTL = 60 ± 10s
    2) single-flight on miss (or probabilistic early refresh)
    3) replicate hot key to N cache replicas / in-process cache 1–2s
    4) optional: split fields (bio vs counters) so writes don’t bust whole blob
```

Black Friday homepage JSON: never flush-all; warm keys before cutover; stagger TTLs.

## Why prefer one over the other

| Prefer **jitter + single-flight** when… | Prefer **local/replicated hot cache** when… |
|-----------------------------------------|-----------------------------------------------|
| Herds are expiry-driven | One key saturates a single Redis node |
| Shared Redis is otherwise fine | Read QPS exceeds one NIC/CPU |

| Prefer **precompute / materialize** when… | Prefer **just shorter path to replica** when… |
|-------------------------------------------|-----------------------------------------------|
| Expensive joins on every miss | DB can take coalesced load easily |

**Not “infinite TTL on hot keys.”** Without invalidation you serve forever-stale; combine long TTL with explicit invalidate or early refresh.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Jittered TTL | Smoother expiry | Slightly more complex ops mental model |
| Single-flight / lock | DB protected | Extra latency for waiters; lock failure modes |
| In-process hot cache | Absorbs insane QPS | Per-pod staleness; more invalidation |
| Replicate key everywhere | No single hot shard | Memory multiplication; consistency fan-out |
| Disable caching for hot key | Predictable DB path | You moved the herd to SQL |

## Interview trigger phrase

> “For hot keys I’d add **TTL jitter** and **single-flight** so expiry doesn’t stampede the DB — and if one Redis shard still melts, I’d **replicate that key** or add a tiny **local cache** in front.”

## Exercise

**Protect a viral “live score” API.**

1. Score key expires every 2s by design — why is naive caching dangerous, and what refresh pattern fits?  
2. 100k clients miss together after a flush — design coalescing without a split brain of 100 loaders.  
3. One Redis shard CPU is 100% on `match:finals` — give two distinct fixes (data plane vs key design).
