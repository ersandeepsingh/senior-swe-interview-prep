# Quorum (R + W > N)

> In **leaderless** replication (Dynamo-style), you tune **how many** replicas must acknowledge a write (**W**) and answer a read (**R**) out of **N**. If **R + W > N**, a read overlaps a prior durable write — “quorum consistency.”

## Plain English

Leaderless stores (Dynamo, Cassandra, Riak-style) send a write to multiple replicas. You don’t wait for all — you wait for **W**. Reads contact **R** and merge versions.

| Symbol | Meaning |
|--------|---------|
| **N** | Replica count for a key |
| **W** | Min replicas that must ack a write |
| **R** | Min replicas contacted on read (then merge) |

**R + W > N** ⇒ read set and write set must intersect ⇒ you see the latest successful quorum write (assuming conflict resolution for concurrent writers).

```text
  N = 3 replicas:  A  B  C

  Write W=2:              Read R=2:
     A ✓  B ✓  C ✗           A ✓  C ✓
     write set {A,B}          read set {A,C}
                              intersection {A} → can see write
```

## Simple example

Shopping cart in Dynamo-style store, N=3.

| Setting | Behavior |
|---------|----------|
| **W=3, R=1** | Slow durable writes; fast maybe-stale reads |
| **W=1, R=3** | Fast writes; reads must gather all (or fail) |
| **W=2, R=2** | Balanced; classic quorum (2+2>3) |
| **W=1, R=1** | Fastest AP; stale reads until repair |

If you set **W=1, R=1** (R+W ≤ N), a read may miss the only replica that got the write → stale cart until repair.

```text
  Write W=1 hits only A
  Read R=1 hits only B  → miss 💥
```

**Sloppy quorum / hinted handoff:** under failure, write to backups then repair — availability ↑, temporary inconsistency ↑. Mention for Dynamo/Cassandra interviews.

## Why prefer one over the other

| Prefer **high W** when… | Prefer **high R** when… | Prefer **W=1 / R=1** when… |
|-------------------------|-------------------------|----------------------------|
| Durability of writes matters | Fresh reads matter more | Latency & availability over consistency |
| Can’t lose acks on crash | Clients tolerate slower gets | Metrics, caches, soft state |
| Smaller N still safe | Many readers OK with cost | You accept repair / conflict later |

**Per-use-case tuning:** same cluster can use quorum for orders and ONE for session blobs if the product allows.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| R+W>N | Read-your-quorum-write | Higher latency / fail if not enough nodes |
| Lower R or W | Latency, availability | Stale reads or lost durability |
| Larger N | Fault tolerance | Cost; slower if W or R grows |
| Read repair / anti-entropy | Converge replicas | Background I/O |

**Trap:** Claiming R+W>N gives “linearizability” always — concurrent writes still need vector clocks / LWW / CRDTs. Quorum is about **overlap**, not magic total order.

**Cassandra hint:** `ONE` / `QUORUM` / `ALL` are the dials — map them to (R,W) in the interview and say when you’d pick each.

**Client behavior:** on shortfall (not enough replicas), fail the request rather than silently relaxing W unless the product explicitly chose AP.

## Interview trigger phrase

> “For a Dynamo-style store I’d set **N=3, R=2, W=2** so R+W>N for the cart, and relax to **W=1** only for data where losing an ack is OK.”

## Exercise

**Tune quorum for “user session” vs “order ledger” on the same cluster.**

1. Propose (N,R,W) for each and justify with R+W ? N.
2. What does the client see if only 1 of 3 replicas is up and W=2?
3. One sentence: why read repair matters even when R+W>N.
