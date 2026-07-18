# 6. Distributed Systems Coordination

How nodes agree, exclude each other, and stay correct when clocks lie and networks fail. Interviewers expect you to **name the coordination primitive** and its failure mode — not hand-wave “we’ll use ZooKeeper.”

| # | Concept | One-line intent |
|---|---------|-----------------|
| 01 | [Leader election / consensus](01_leader_election_consensus.md) | Raft / Paxos / ZK → pick a primary safely |
| 02 | [Distributed locks](02_distributed_locks.md) | Mutual exclusion across nodes (with caveats) |
| 03 | [Distributed transactions](03_distributed_transactions.md) | 2PC / Saga / TCC → cross-service consistency |
| 04 | [Idempotency](04_idempotency.md) | Safe retries → idempotency keys on payments |
| 05 | [Quorum (R+W>N)](05_quorum.md) | Tunable consistency in leaderless stores |
| 06 | [Vector / logical clocks](06_vector_logical_clocks.md) | Order events without global time |
| 07 | [Conflict resolution](07_conflict_resolution.md) | LWW / CRDTs → merge divergent writes |
| 08 | [Heartbeats & failure detection](08_heartbeats_failure_detection.md) | Detect dead nodes → gossip, health checks |

**How to use:** For each file — read Plain English → diagram → trade-offs → say the interview trigger phrase out loud → do the Exercise without peeking at notes.
