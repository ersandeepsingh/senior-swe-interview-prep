# Heartbeats & Failure Detection

> You can’t know a node is **dead** — only that it **stopped answering**. **Heartbeats**, **health checks**, and **gossip** estimate liveness so the cluster can failover without thrashing on false positives.

## Plain English

Failure detectors are **unreliable** by nature (FLP / network ambiguity). Systems pick timeouts and suspicion levels that trade **fast failover** vs **false positives**.

| Mechanism | Role |
|-----------|------|
| **Heartbeat** | Periodic “I’m alive” to peers / coordinator |
| **Health check** | Probe (HTTP/TCP) from LB or orchestrator |
| **Gossip** | Epidemic spread of membership & suspicion (SWIM) |
| **phi-accrual / adaptive FD** | Soft suspicion vs hard timeout |

```text
  Node A ──heartbeat──► Detector
  Node B ──heartbeat──► Detector
  Node C ── ✕ missed ──► Detector
                              │
                         timeout / phi high
                              │
                              ▼
                    mark C suspect → failover
                    (maybe C was GC-paused!)
```

## Simple example

Kafka / Raft follower misses several heartbeats → election. If the “dead” node was only **GC-paused**, it may return as a **zombie** — hence fencing tokens and epoch numbers.

```text
  LB ──GET /healthz──► Pod
         │ fail ×3
         ▼
  remove from pool
  (readiness: don't send traffic)
  (liveness: restart if stuck)
```

Load balancer: unhealthy instance removed after N failed probes. Too aggressive → flapping. Too slow → users hit dead pods.

**K8s interview point:** separate **liveness** (restart me) from **readiness** (don’t send traffic yet).

## Why prefer one over the other

| Prefer **short timeout** when… | Prefer **longer / adaptive** when… |
|--------------------------------|------------------------------------|
| Failover SLA is tight | GC pauses, flaky networks common |
| Stateless replicas plentiful | Leader election cost is high |
| False positive = mild | False positive = split-brain risk |

**Gossip vs central checker:** gossip scales membership (Cassandra, SWIM); central health is simpler (K8s kubelet + probe). Many systems combine both.

**phi-accrual:** instead of fixed timeout, compute suspicion from heartbeat inter-arrival history — fewer false positives under variable load.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Fast failure detect | Quicker failover | More false positives, churn |
| Slow detect | Stability | Longer outage window |
| Gossip membership | Scalable, no SPOF detector | Complexity, infection delay |
| Fencing after detect | Safety despite false positives | Extra protocol on storage |

**Trap:** Equating “process up” with “ready.” Also: detecting failure without **fencing** still allows split-brain writes.

**Flapping control:** require N consecutive failures before ejecting; hysteresis before re-adding. Otherwise the VIP oscillates and caches thrash.

**Cross-AZ heartbeats:** prefer detecting within the consensus/membership protocol rather than inventing a second ad-hoc ping mesh when Raft/SWIM already exists.

## Interview trigger phrase

> “I’d use **heartbeats with conservative timeouts plus fencing**, and separate **liveness vs readiness** — so GC pauses don’t cause split-brain or flap the VIP.”

## Exercise

**Design failure detection for a 3-node Raft DB and a 200-pod API tier.**

1. Why different timeout strategies for Raft vs the API pods?
2. What happens if the LB marks a pod unhealthy while it still holds an in-flight lock?
3. One sentence on gossip’s role in a large Cassandra-like ring.
