# 08 · Distributed Systems — Consensus & Coordination

> Getting independent machines to agree on something despite failures.

---

## Consensus

**Definition:** The problem of getting multiple nodes to agree on a single value (or ordering of events) even when some nodes or messages fail.

**Simple explanation:** If five servers each think they're in charge, chaos follows. Consensus algorithms let a group pick one agreed answer that survives crashes — the foundation for leader election, replicated logs, and distributed locks. The catch: agreement requires a majority (quorum), so you need an odd number of nodes.

**Example:** Five replicas must agree on "who is the leader" and "what's the next entry in the log." As long as 3 of 5 are reachable, they can agree and keep operating; if only 2 remain, they correctly refuse to act (to avoid split-brain).

---

## Raft

**Definition:** A consensus algorithm designed to be understandable, based on leader election + replicated log + safety rules.

**Simple explanation:** Raft elects one leader; all writes go through it. The leader appends entries to its log and replicates them to followers. An entry is "committed" once a majority store it. If the leader dies, followers time out and elect a new one (using term numbers to avoid confusion). It's the algorithm behind etcd, Consul, and many modern systems.

**Example:** 3-node cluster. Leader receives `SET x=5`, sends it to both followers; once 2 of 3 (majority) acknowledge, it's committed and applied. Leader crashes → a follower whose log is up to date wins the next election and continues.

---

## Paxos

**Definition:** The original proven consensus algorithm (proposers, acceptors, learners) that guarantees safety under failures.

**Simple explanation:** Paxos solves the same problem as Raft but is famously hard to understand and implement. You mostly need to know it exists, that it's the theoretical ancestor, and that Raft was created as a more understandable alternative. Google's Chubby and Spanner use Paxos variants.

**Example:** In interviews, "how do nodes agree?" — you can say "via a consensus protocol like Paxos or, more practically, Raft," and then explain Raft because it's easier to reason about.

---

## Leader election

**Definition:** The process of designating one node as the coordinator/primary, and re-designating when it fails.

**Simple explanation:** Many systems need exactly one node "in charge" (to serialize writes, assign work, etc.). Leader election picks that node and, crucially, ensures there's never *two* leaders at once (**split-brain**), which would corrupt data. Usually done via consensus + timeouts + term/epoch numbers.

**Example:** A database with one primary for writes. The primary crashes; replicas detect missed heartbeats, hold an election, and promote a new primary. Fencing (epoch numbers) ensures the old primary, if it revives, can't keep writing as a zombie leader.

---

## ZooKeeper / etcd

**Definition:** Coordination services that provide a reliable, consistent, small key-value store for distributed config, locks, leader election, and service discovery.

**Simple explanation:** Rather than each team building consensus from scratch, they lean on ZooKeeper (used by Kafka, Hadoop) or etcd (used by Kubernetes). These give strongly consistent primitives — "who's the leader," "here's the current config," "grant this lock" — backed by consensus internally.

**Example:** Kubernetes stores all cluster state (what pods should run where) in **etcd**. Every controller reads/writes etcd as the single source of truth, trusting it to stay consistent across node failures.

---

## Distributed locks

**Definition:** A mechanism ensuring only one node performs a critical action at a time across a cluster.

**Simple explanation:** Sometimes you need "only one worker may process this job." A distributed lock enforces that across machines. But they're tricky: the lock holder can pause (GC/network) past its lease and think it still holds the lock. **Fencing tokens** (monotonic numbers) let the resource reject a stale holder. Redlock (Redis) is popular but debated for correctness.

**Example:** Two workers try to charge an invoice. Worker A acquires the lock with fencing token 34 and starts, then stalls. Its lease expires; Worker B gets token 35 and proceeds. When A wakes and tries to write, the datastore sees token 34 < 35 and rejects it — preventing a double charge.

---

## Quorum (R + W > N)

**Definition:** In a system with N replicas, requiring W replicas to acknowledge a write and R replicas to respond to a read, chosen so that R + W > N guarantees read/write overlap.

**Simple explanation:** In leaderless systems, you tune consistency with these numbers. If reads and writes always share at least one replica (R + W > N), a read is guaranteed to see the latest write. You trade: higher W = safer writes but slower; higher R = safer reads but slower.

**Example:** N=3. Choose W=2, R=2 → R+W=4 > 3, so any read overlaps any write on at least one node → strong-ish consistency. If instead W=1, R=1, you get fast but possibly stale reads (eventual consistency).

---

## Two-phase / three-phase commit

**Definition:** Protocols to make a transaction atomic across multiple nodes. **2PC:** a coordinator asks all participants to *prepare*, then tells them all to *commit* or *abort*. **3PC:** adds an extra phase to reduce blocking.

**Simple explanation:** 2PC guarantees all-or-nothing across databases, but has a fatal flaw: if the coordinator crashes after "prepare," participants are stuck holding locks, waiting (blocking). 3PC adds a "pre-commit" phase so nodes can make progress if the coordinator dies — at the cost of more messages and still not handling network partitions perfectly. This is why modern systems often prefer Sagas.

**Example:** Transfer money across two banks' databases. **Phase 1 (prepare):** both lock the rows and reply "ready." **Phase 2 (commit):** coordinator says "commit," both apply. If either says "no" in phase 1, coordinator tells both to abort. If the coordinator dies mid-phase-2, participants block — the well-known 2PC weakness.
