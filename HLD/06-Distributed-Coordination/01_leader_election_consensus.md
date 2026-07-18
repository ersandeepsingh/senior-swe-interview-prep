# Leader Election & Consensus

> When many nodes must act as **one**, they elect a **leader** via **consensus** — a majority agrees who is in charge and what the log says. Without it, you get split-brain.

## Plain English

**Leader election:** pick one node that coordinates writes / decisions.

**Consensus:** a protocol so a majority of nodes agree on the same sequence of values (who is leader, what commands committed) even if some crash or messages reorder.

| Name | Role in interviews |
|------|--------------------|
| **Raft** | Understandable log replication + leader; etcd, Consul |
| **Paxos** | Classic theory; Multi-Paxos ≈ same job as Raft |
| **ZooKeeper / etcd** | CP coordination stores; ephemeral nodes → leadership |

Key Raft ideas to name-drop: **terms**, **leader election**, **log replication**, **commit only after majority ack**, **followers reject stale terms**.

```text
        Clients
           │
           ▼
     ┌───────────┐
     │  Leader   │  ← only one accepts client writes
     │  (term N) │
     └─────┬─────┘
           │ replicate log entries
     ┌─────┴─────┐
     ▼           ▼
  Follower    Follower
  (majority must ack before commit)
```

## Simple example

Three Postgres-style nodes; primary dies.

```text
  Before:  [L]  F  F     After crash:  ?  F  F
                              │
                         Raft election
                              │
                              ▼
                         [L'] F     (old L stays down)
```

New leader wins only with **majority votes** in a new term. Old leader, if it wakes up partitioned, cannot commit — majority won’t follow its stale term. **No two leaders** for the same term’s committed log.

**Client view during election:** brief window of errors / leader-not-found (often 1–5s). Design the API tier to retry idempotently.

## Why prefer one over the other

| Prefer **consensus leader** when… | Prefer **no single leader** when… |
|-----------------------------------|-----------------------------------|
| Strong ordering, config, locks, metadata | Extreme write fan-out across regions |
| Must avoid split-brain (money, leases) | AP / eventual path (likes, metrics) |
| Cluster size small (3–7 voters) | Huge shard rings (Dynamo-style) |

**Raft vs Paxos in interviews:** say Raft for clarity (leader + log); mention Paxos as the theoretical family. **ZK vs Raft-backed etcd:** same job — coordination, not your primary app DB.

**Odd number of voters:** 3 or 5 is typical. Two nodes cannot form a safe majority after one failure.

### Real systems (interview name-drops)

- **etcd / Consul / ZooKeeper** — service discovery, config, locks, leader leases.
- **Kafka controller / Raft KRaft** — cluster metadata consensus.
- **MongoDB replica set / Postgres Patroni** — primary election flavored by consensus or fencing.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Majority consensus | Safety under partitions / crashes | Need odd N; minority can’t make progress |
| Strong leader | Simple client mental model | Leader is a hotspot; election pause |
| More voters | Survive more failures | Slower commits (more acks) |
| Using consensus as app DB | Strong consistency | Throughput / ops cost wrong tool |

**Trap:** “We elect a leader with Redis SETNX.” Without fencing / consensus, two leaders under network blips.

## Interview trigger phrase

> “I’d put **Raft/etcd** (or ZK) in front of anything that must have **one writer** — leadership leases with fencing tokens — and keep the hot path off the consensus cluster.”

## Exercise

**Design “primary election for a sharded chat write path.”**

1. Why is a 2-node cluster a bad consensus setup for production?
2. What does the user see during a 2–5s leader election (writes)?
3. One sentence: how a fencing token stops a stale primary from corrupting state after it reconnects.
