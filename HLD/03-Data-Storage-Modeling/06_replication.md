# Replication

> Keep **copies** of data on multiple nodes for durability and read scale. Topology decides who accepts writes and how conflicts appear: **leader-follower**, **multi-leader**, or **leaderless**.

## Plain English

| Model | Who writes | Typical feel |
|-------|------------|--------------|
| **Leader–follower** | One primary | Simple; followers replicate |
| **Multi-leader** | Several primaries | Write locally in each region; conflict resolve |
| **Leaderless** | Any node (quorum) | Dynamo-style; client/coordinator + R/W quorums |

```text
  Leader-follower              Multi-leader
  ┌────────┐                   ┌────┐     ┌────┐
  │ Leader │──async/sync──►    │ L1 │◄───►│ L2 │
  └───┬────┘   ┌────────┐      └────┘     └────┘
      ├───────►│ Follower│      both accept writes
      └───────►│ Follower│
               └────────┘

  Leaderless (quorum)
  Client ──► N replicas; succeed if W writes ack
             read if R replicas agree (R+W > N)
```

## Simple example

**Postgres primary + 2 replicas** for a blogging site.

```text
  Write post  → Leader only
  Read post   → Follower (may lag seconds) or Leader (strong)

  Leader dies → promote a follower (failover) → brief unavailability window
```

**Multi-region notes app (multi-leader):** Alice edits in Mumbai, Bob in Virginia offline-ish → both write → last-write-wins or CRDT/merge on sync.

## Why prefer one over the other

| Prefer **leader–follower** when… | Prefer **multi-leader** when… | Prefer **leaderless** when… |
|----------------------------------|-------------------------------|-----------------------------|
| You want one write truth | Regions must accept writes locally | Extreme availability; tunable quorum |
| Conflicts are unacceptable | Disconnected / regional autonomy | You can reason about R + W |
| Classic RDBMS ops model | Conflict resolution is designed | Dynamo-family stores |

**Why not multi-leader by default?** Conflict resolution is hard — two “set inventory to X” writes diverge.

**Why sync vs async replication?** Sync = stronger durability / less data loss on failover, higher write latency. Async = faster writes, possible loss on crash.

### Real systems (interview name-drops)

- **Leader–follower:** Postgres streaming, MySQL binlog, MongoDB replica set (primary).
- **Multi-leader:** CouchDB, some MySQL multi-source setups, mobile sync engines.
- **Leaderless:** Cassandra, Riak, DynamoDB under the hood (managed quorums).

## Trade-offs

| Choice | You gain | You give up |
|--------|----------|-------------|
| Single leader | Simple consistency story | Write ceiling = one node; failover drama |
| Async replicas | Low write latency; read scale | Replication lag; stale reads |
| Sync / quorum write | Safer failover | Higher latency; availability hit if replicas down |
| Multi-leader | Local write latency | Conflicts, harder invariants |
| Leaderless + quorum | Tunable C vs A | App must handle sibling conflicts / hinted handoff |

**Common interview trap:** “Replicas = strong consistency.” Seniors ask: *async or sync?* and *read-your-writes?*

## Interview trigger phrase

> “Default I’d use **single-leader replication** for a clear write path, scale reads with followers accepting lag, and only go multi-leader or leaderless when regional writes or availability force it.”

## Exercise

**Replicate a payments ledger and a product catalog.**

1. Pick a replication model for each — and why they might differ.  
2. Leader fails mid-write (async) — what can a newly promoted follower be missing?  
3. One sentence on R=1, W=1 vs R=2, W=2 in a 3-replica leaderless store for checkout vs browse.
