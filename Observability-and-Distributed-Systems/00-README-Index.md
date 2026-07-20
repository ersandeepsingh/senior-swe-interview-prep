# Observability & Distributed Systems — Detailed Study Notes

Deep-dive notes for senior SWE interviews. Every topic follows the same shape: **Definition** (precise), **Simple explanation** (plain-English intuition), and **Example** (concrete scenario).

## How to use these
Skim the definition to recall, read the simple explanation to understand, and use the example as the story you tell in an interview. The senior signal throughout is the same: **name the trade-off, name the failure mode, name the mitigation.**

---

## Part A — Observability

1. [Three Pillars](01-Observability-Three-Pillars.md) — logs, metrics, traces; observability vs monitoring; when to use each.
2. [Logging](02-Observability-Logging.md) — structured logs, levels, correlation IDs, centralization, sampling, PII, cost vs metrics.
3. [Metrics](03-Observability-Metrics.md) — metric types, RED/USE/four-golden-signals, percentiles, Prometheus, cardinality, dashboards, push vs pull.
4. [Distributed Tracing](04-Observability-Distributed-Tracing.md) — spans/traces, context propagation, OpenTelemetry, sampling, tools.
5. [Alerting & SRE](05-Observability-Alerting-SRE.md) — SLI/SLO/SLA, error budgets, alert on symptoms, alert fatigue, on-call, availability math, MTTR, postmortems.
6. [Health, Debugging & Profiling](06-Observability-Health-Debugging-Profiling.md) — liveness/readiness, synthetic vs RUM, prod profiling, anomaly detection.

## Part B — Distributed Systems

7. [Foundational Theorems](07-DistSys-Foundational-Theorems.md) — CAP, PACELC, consistency spectrum, latency vs throughput, FLP, fallacies.
8. [Consensus & Coordination](08-DistSys-Consensus-Coordination.md) — consensus, Raft, Paxos, leader election, ZooKeeper/etcd, distributed locks, quorum, 2PC/3PC.
9. [Replication & Partitioning](09-DistSys-Replication-Partitioning.md) — replication models, sync vs async, sharding, consistent hashing, rebalancing, read/write split, hotspots.
10. [Consistency, Time & Ordering](10-DistSys-Consistency-Time-Ordering.md) — Lamport & vector clocks, clock issues, conflict resolution, CRDTs, idempotency, delivery semantics.
11. [Distributed Transactions](11-DistSys-Distributed-Transactions.md) — saga, 2PC, outbox, CDC, event sourcing, CQRS, dual-write problem.
12. [Fault Tolerance & Resilience](12-DistSys-Fault-Tolerance-Resilience.md) — failure detection, retries+backoff+jitter, circuit breaker, bulkhead, timeouts/deadlines, graceful degradation, failover, load shedding, chaos.
13. [Messaging & Async](13-DistSys-Messaging-Async.md) — queues vs streams, Kafka internals, ordering, backpressure, DLQs, idempotent consumers.
14. [Scalability Building Blocks](14-DistSys-Scalability-Building-Blocks.md) — horizontal vs vertical, stateless services, caching/invalidation, CDN, load balancing, probabilistic structures.

---

## Highest-ROI to drill first
**Observability:** three pillars + when to use each, RED/USE/golden signals, SLI/SLO/error budgets, distributed tracing + context propagation, alert-on-symptoms, percentiles/tail latency.

**Distributed systems:** CAP/PACELC, consistency models, consistent hashing, replication (sync/async, leader models), quorums, idempotency & delivery semantics, saga/outbox/CDC, circuit breaker + retries-with-jitter, Raft at a high level, Kafka partition/consumer-group model.
