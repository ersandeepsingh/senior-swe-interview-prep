# Consensus Algorithms

Consensus algorithms are protocols that allow a distributed system (a set of independent computers or nodes) to agree on a single data value or state, even in the presence of failures. They are fundamental to ensuring data consistency and reliability in distributed systems, especially when no single node is trusted completely.

---

## Why Consensus Is Needed

In distributed systems, nodes can fail, become unreachable, or behave maliciously. Despite this, the system must function correctly — for example, databases must agree on the sequence of transactions, or blockchain nodes must agree on the state of the ledger. Consensus algorithms solve the "state agreement" problem by ensuring that:

- All non-faulty nodes agree on the same value (agreement)
- The agreed value must be a value proposed by a node (validity)
- Nodes eventually decide on a value (termination/liveness)

---

## Classic Consensus Algorithms

### 1. **Paxos**

Paxos is one of the oldest and most influential consensus algorithms, used primarily in systems where nodes may crash (crash-fault tolerance).

#### How Paxos Works (simplified):

1. **Proposer** suggests a value to be chosen.
2. **Acceptors** receive proposals, promise not to accept older proposals, and can accept a value if a majority agrees.
3. Once a majority of acceptors agree, the value is chosen (consensus reached).

Paxos ensures that even if some nodes crash, as long as a majority are alive, progress can be made.

#### Example

Imagine 5 nodes (A, B, C, D, E). Nodes must agree on the next "leader" node.

- Node A proposes "B" as the next leader, and sends a proposal to all nodes.
- Each node replies with a "promise" to not accept older proposals.
- If A gets promises from a majority (at least 3 nodes), it asks them to "accept" B as leader.
- Once a majority "accepts", consensus is reached: B is the leader.

---

### 2. **Raft**

Raft is a consensus algorithm designed to be more understandable than Paxos and is widely used in production systems (like etcd, Consul).

#### Main Concepts

- **Leader election**: One node acts as leader; others are followers.
- **Log replication**: All changes go through the leader, who replicates log entries to followers.
- **Commitment**: Once a log entry is on a majority of nodes, it is committed and applied.

#### Example (Log Replication)

Consider a distributed key-value store with 3 nodes (A, B, C):

1. **Leader election**: After startup, A becomes leader.
2. **Client writes**: Client asks to write key `foo=42`. A appends this to its log and sends "append" requests to B and C.
3. **Replication**: B and C add the entry to their logs and reply "OK".
4. **Commitment**: Once A sees a majority (incl. itself, e.g. A+B), it commits the entry and tells B, C to commit as well.
5. **State machine**: All three nodes apply the entry to their local DBs.

If the leader fails, a new leader is elected and log continuity is enforced.

---

### 3. **Byzantine Fault Tolerance (BFT), e.g. PBFT**

Some consensus algorithms, like **Practical Byzantine Fault Tolerance (PBFT)**, tolerate not only crashes but malicious ("Byzantine") nodes.

- **PBFT** works in steps where nodes exchange signed votes and require supermajority agreement (e.g., ⅔ or more).
- Used in some blockchains and mission-critical applications.

---

## Real-World Example: Raft in etcd

[etcd](https://etcd.io/docs/v3.5/faq/#how-does-etcd-achieve-consensus) is a distributed key-value store used by Kubernetes.

- etcd uses Raft.
- Every config change (e.g., create a pod) goes through Raft consensus.
- Guarantees that all cluster nodes agree on the cluster state.

---

## Trade-Offs

| Algorithm | Fault Tolerance | Performance | Understandability | Applications |
|-----------|----------------|-------------|------------------|--------------|
| Paxos     | Crash-fault    | Moderate    | Complex          | DBs, config  |
| Raft      | Crash-fault    | Good        | Accessible       | etcd, Consul |
| PBFT      | Byzantine      | Slower      | Complex          | Blockchains  |

- Classic algorithms handle **crash faults** (nodes go offline)
- BFT algorithms also handle **Byzantine faults** (nodes act arbitrarily/maliciously)

---

## In Summary

- Consensus allows a distributed system to agree on a single value/state in the face of failures.
- **Paxos**, **Raft**, and **PBFT** are representative consensus algorithms.
- You pick the algorithm based on fault model (crash vs. Byzantine), performance, and system complexity.

**Interview tip:**  
_"If asked about maintaining consistency across distributed nodes, I’d discuss consensus algorithms like Paxos and Raft, explaining leader election and log replication, and how these enable all nodes to agree on the same sequence of operations. For adversarial environments, I'd mention Byzantine Fault Tolerance (e.g., PBFT) used in blockchains."_

---