# PACELC

> If there is a **P**artition: choose **A** or **C**. **E**lse (no partition): choose **L**atency or **C**onsistency.

## Plain English

CAP only talks about the bad day (partition). Most of the time the network is fine — yet systems still disagree on design.

**PACELC** adds the normal day:

```text
        Is the network partitioned?
              │
      ┌───────┴───────┐
      YES             NO (Else)
      │               │
   CAP choice      PACELC "EL/EC"
   A vs C          Latency vs Consistency
```

| Shorthand | Meaning |
|-----------|---------|
| **PA/EL** | On partition → Availability; Else → favor Latency (often eventual consistency) |
| **PC/EC** | On partition → Consistency; Else → favor Consistency (even if slower) |
| **PA/EC** | Available under partition, but when healthy still wait for strong consistency (rarer mix) |
| **PC/EL** | Consistent under partition, but when healthy optimize for latency (unusual combo) |

Interview default name-drops:

- **Dynamo / Cassandra-style → PA/EL** — stay up; when healthy, don’t wait for every replica on every read.
- **Spanner / tightly synced DBs → PC/EC** — stay correct; when healthy, still coordinate for strong consistency (higher latency).

## Simple example

You post a photo. Friend in another city refreshes the feed.

```text
                    Healthy network (Else)
                              │
         ┌────────────────────┴────────────────────┐
         ▼                                         ▼
   PA/EL (Dynamo-like)                      PC/EC (Spanner-like)
   Return feed fast from                    Wait until write is
   local replica — photo may                visible on quorum /
   appear 1–2s later                        globally ordered
   Latency: ~20–50ms                        Latency: higher RTT cost
```

Under a **partition**, PA systems still serve (maybe divergent). PC systems may refuse or block until safe.

## Why prefer one over the other

| Prefer **PA/EL** when… | Prefer **PC/EC** when… |
|------------------------|------------------------|
| Global users, latency budget is tight | Global correctness matters more than 50ms |
| Shopping cart browse, social, IoT metrics | Banking ledgers, inventory locks, ads billing |
| OK to reconcile conflicts asynchronously | Conflicts must not exist |

**Why not always PC/EC?** Cross-region strong consistency means waiting on the farthest replica or consensus round-trips. That’s often **tens to hundreds of ms** added to every write — death for a feed API aiming at p99 < 100ms.

**Why not always PA/EL?** You pay with stale reads, conflict resolution (LWW, CRDTs, app merges), and harder mental models for “did my write stick?”

## Trade-offs

| Axis | Faster / more available path | Safer / more consistent path |
|------|------------------------------|------------------------------|
| Partition | Answer from local copy (AP) | Block or error until quorum (CP) |
| No partition | Skip waiting on all replicas (EL) | Sync / consensus on every critical write (EC) |
| Ops complexity | Conflict handling, repair | Coordination, higher latency, capacity for sync |

## Diagram: where classic systems sit

```text
                 Consistency (C / EC)
                          ▲
                          │
              Spanner ●   │
                          │
         Postgres●        │        (single-region primary)
         (sync replica)   │
                          │
    ◄─────────────────────┼─────────────────────► Latency-friendly (EL)
    Availability focus    │
                          │
              Cassandra ● │  DynamoDB ●
              (tunable)   │  (tunable)
                          │
                          ▼
                    Availability (A)
```

(Positions are illustrative — most stores are **tunable** per table/query.)

## Interview trigger phrase

> “CAP is the partition story; **PACELC** is the everyday story. I’d run the feed **PA/EL** for latency, and the payment ledger **PC/EC** — Spanner-like consistency is worth the RTT there.”

## Exercise

**Compare “Design Instagram” vs “Design a stock-trading matching engine” using PACELC.**

1. Label each as roughly PA/EL or PC/EC (and say which part of the product might differ).
2. Pick one write path in each system and say what the user experiences if a write takes +80ms for consistency.
3. Write one sentence: *when healthy*, what you’re optimizing for in each system.
