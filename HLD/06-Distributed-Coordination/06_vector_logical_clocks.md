# Vector Clocks & Logical Clocks

> Wall clocks **disagree** across machines. **Logical clocks** (Lamport) and **vector clocks** order events by causality — so you know “happened-before” without trusting NTP.

## Plain English

Distributed systems cannot rely on “who has the larger `updated_at`” when servers’ clocks skew by tens of ms (or more after NTP blips).

| Clock | What it gives you |
|-------|-------------------|
| **Wall clock** | Human time; skew → wrong “who was last” |
| **Lamport clock** | Integer counter; total order consistent with causality (not unique concurrency) |
| **Vector clock** | One counter per node; detect **concurrent** vs **causal** updates |
| **HLC** | Hybrid logical + physical — Spanner-flavored storytelling |

**Happened-before (→):** A → B if A could have caused B (same process order, or message send before receive). Concurrent if neither → the other.

```text
  Node X:  [1,0] --msg-->  Node Y: [1,1]
             │                    │
             │                    ▼
           [2,0]              concurrent write [1,2]
             │
             ▼
        X's VC [2,0] vs Y's [1,2]:
        neither ≥ other → CONFLICT (concurrent)
```

Compare vectors component-wise: `Va ≥ Vb` if every component ≥ and at least one >. Otherwise incomparable → concurrent.

## Simple example

Two shopping-cart replicas, offline merge (classic Dynamo).

```text
  Replica A adds milk     Replica B adds eggs
  VC_A = (A:1)            VC_B = (B:1)
         \                   /
          \                 /
           v               v
        reconcile: versions concurrent
        → keep both items (union) or flag conflict
        new VC = (A:1, B:1)
```

If B had seen A’s milk first, B’s clock would dominate → eggs **after** milk, not a conflict.

**Lamport example:** assign timestamps so if A → B then L(A) < L(B). Useful for debugging/logs; cannot tell “concurrent vs ordered” the way vectors can.

## Why prefer one over the other

| Prefer **vector clocks** when… | Prefer **Lamport / hybrid** when… | Prefer **wall time (LWW)** when… |
|--------------------------------|-----------------------------------|----------------------------------|
| Multi-writer, need conflict detect | Need cheap total order for logs | Conflicts rare; last writer OK |
| Carts, shopping lists, presence | Debugging causal order | Simple caches, soft prefs |
| Replica count small (VC size) | Don’t need concurrency detection | Ops simplicity > perfect merge |

**VC size problem:** one entry per writer — prune carefully or use dotted version vectors in advanced designs.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Vector clocks | Precise concurrency detection | Metadata size grows with writers |
| Lamport only | Tiny metadata | Can’t tell concurrent vs ordered |
| Trust wall clock | Simple LWW | Skew → silent data loss |
| HLC | Better physical meaning | Still not true global time |

**Trap:** Sorting by `updated_at` from app servers as “truth.” Say you’d use **causality metadata** or a consensus log when order must be correct.

## Interview trigger phrase

> “I wouldn’t trust server timestamps for concurrent cart edits — I’d use **vector clocks** (or CRDTs) to detect conflicts and merge, not last-write-wins on skewed clocks.”

## Exercise

**Two users edit the same doc offline.**

1. Draw vector clocks showing a concurrent edit vs a causal follow-up edit.
2. When is Lamport enough for your design, and when do you need vectors?
3. One sentence you’d say about NTP and LWW in this interview.
