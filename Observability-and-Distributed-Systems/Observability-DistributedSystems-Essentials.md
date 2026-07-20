# Observability & Distributed Systems — Interview Essentials (Senior SWE)

The concepts most frequently asked in senior interviews for these two areas. Organized by **category → topic → 1-line "what to know."**
The ⭐ marks the highest-frequency interview topics — the ones you should be able to explain *and* defend trade-offs on.

Legend: 🟢 know it · 🟡 use & compare · 🔴 design/defend · ⭐ high-frequency

---

# PART A — OBSERVABILITY

## 1. The Three Pillars ⭐

- **Logs** — discrete, timestamped events; structured (JSON) vs unstructured; when to log. 🟡⭐
- **Metrics** — numeric time-series, cheap to store/aggregate, good for alerting/trends. 🟡⭐
- **Traces** — request flow across services with causal timing; spans & parent-child. 🔴⭐
- **Pillars vs "observability"** — why 3 signals ≠ observability; unknown-unknowns. 🔴⭐
- **When to use which** — metric for "is it broken," trace for "where," log for "why." 🟡⭐

## 2. Logging ⭐

- **Structured logging** — key-value/JSON logs for machine parsing. 🟡⭐
- **Log levels** — DEBUG/INFO/WARN/ERROR/FATAL and choosing appropriately. 🟢⭐
- **Correlation / request IDs** — tie logs across services for one request. 🔴⭐
- **Centralized logging** — ELK/EFK stack (Elasticsearch + Logstash/Fluentd + Kibana), Loki. 🟡⭐
- **Log sampling & volume control** — cost vs completeness at scale. 🔴
- **PII & security in logs** — redaction, compliance, never log secrets. 🟡⭐
- **Logs vs metrics cost** — why you don't alert on raw logs at scale. 🔴

## 3. Metrics ⭐

- **Metric types** — counter, gauge, histogram, summary. 🟡⭐
- **RED method** — Rate, Errors, Duration (for request-driven services). 🔴⭐
- **USE method** — Utilization, Saturation, Errors (for resources). 🔴⭐
- **Four Golden Signals** — latency, traffic, errors, saturation (Google SRE). 🔴⭐
- **Percentiles** — p50/p95/p99, why averages lie, tail latency. 🔴⭐
- **Prometheus model** — pull-based scraping, PromQL, exporters, labels/cardinality. 🔴⭐
- **Cardinality explosion** — high-cardinality labels blow up storage. 🔴⭐
- **Aggregation & rollups** — downsampling, retention tiers. 🟡
- **Dashboards** — Grafana, what a good dashboard shows. 🟡⭐
- **Push vs pull metrics** — Prometheus (pull) vs StatsD/push gateways. 🟡

## 4. Distributed Tracing ⭐

- **Spans & traces** — trace = tree of spans; span attributes/events. 🔴⭐
- **Trace context propagation** — passing trace/span IDs across service calls (W3C Trace Context). 🔴⭐
- **OpenTelemetry** — vendor-neutral standard for traces/metrics/logs. 🔴⭐
- **Sampling** — head vs tail sampling, cost vs coverage trade-off. 🔴⭐
- **Tools** — Jaeger, Zipkin, Tempo, vendor APMs (Datadog/Honeycomb). 🟡
- **What tracing solves** — latency attribution & dependency mapping in microservices. 🔴⭐

## 5. Alerting & SRE Practices ⭐

- **SLI / SLO / SLA** — indicator vs objective vs agreement; examples. 🔴⭐
- **Error budgets** — spending budget to balance velocity vs reliability. 🔴⭐
- **Alerting philosophy** — alert on symptoms not causes; page on user pain. 🔴⭐
- **Alert fatigue** — reducing noise, actionable alerts only. 🟡⭐
- **On-call & runbooks** — escalation, playbooks, automation. 🟡
- **Availability math** — nines → downtime budget (99.9% ≈ 8.7h/yr). 🟡⭐
- **MTTR / MTBF / MTTD** — reliability metrics. 🟡
- **Incident response & blameless postmortems** — RCA, action items. 🟡⭐

## 6. Health, Debugging & Profiling

- **Health checks** — liveness vs readiness probes. 🟡⭐
- **Synthetic vs real-user monitoring** — proactive checks vs actual traffic. 🟡
- **Profiling in prod** — continuous profiling (pprof, flame graphs). 🔴
- **Anomaly detection** — baselines, alerting on deviation. 🔴

---

# PART B — DISTRIBUTED SYSTEMS

## 7. Foundational Theorems & Trade-offs ⭐

- **CAP theorem** — Consistency / Availability / Partition-tolerance; pick 2 under partition. 🔴⭐
- **PACELC** — else (no partition): Latency vs Consistency. 🔴⭐
- **Consistency spectrum** — strong, sequential, causal, eventual, read-your-writes, monotonic. 🔴⭐
- **Latency vs throughput** — response time vs volume; tail latency. 🟡⭐
- **FLP impossibility** — no guaranteed consensus in fully async with failures (conceptual). 🔴
- **Fallacies of distributed computing** — network is NOT reliable/fast/free/secure. 🔴⭐

## 8. Consensus & Coordination ⭐

- **Consensus** — agreeing on a value across nodes despite failures. 🔴⭐
- **Raft** — leader election, log replication, safety (the "understandable" one). 🔴⭐
- **Paxos** — classic consensus; know it exists & the idea. 🔴
- **Leader election** — picking a primary; split-brain avoidance. 🔴⭐
- **ZooKeeper / etcd** — coordination services, distributed config/locks. 🟡⭐
- **Distributed locks** — Redlock and its caveats, fencing tokens. 🔴⭐
- **Quorum (R + W > N)** — tunable consistency in leaderless systems. 🔴⭐
- **Two-phase / three-phase commit** — atomic commit across nodes, blocking problem. 🔴⭐

## 9. Replication & Partitioning ⭐

- **Replication models** — single-leader, multi-leader, leaderless (Dynamo). 🔴⭐
- **Sync vs async replication** — durability vs latency; replication lag. 🔴⭐
- **Partitioning / sharding** — range, hash, consistent hashing, directory. 🔴⭐
- **Consistent hashing** — minimize reshuffling when nodes change; virtual nodes. 🔴⭐
- **Rebalancing** — moving partitions without downtime. 🔴
- **Read/write splitting** — replicas for reads, handling stale reads. 🟡⭐
- **Hot spots / skew** — uneven partition load and mitigation. 🔴

## 10. Consistency, Time & Ordering ⭐

- **Logical clocks** — Lamport timestamps for event ordering. 🔴⭐
- **Vector clocks** — detecting concurrent updates / causality. 🔴⭐
- **Physical clock issues** — clock skew, NTP, why wall-clock ordering is unsafe. 🔴⭐
- **Conflict resolution** — last-write-wins vs CRDTs vs app-level merge. 🔴⭐
- **CRDTs** — conflict-free replicated data types for eventual consistency. 🔴
- **Idempotency** — safe retries via idempotency keys. 🔴⭐
- **Exactly-once vs at-least-once vs at-most-once** — delivery semantics & dedup. 🔴⭐

## 11. Distributed Transactions & Data Patterns ⭐

- **Saga pattern** — long-lived txn as local steps + compensations; orchestration vs choreography. 🔴⭐
- **Two-phase commit (2PC)** — coordinator + participants, blocking on failure. 🔴⭐
- **Outbox pattern** — reliable event publishing with DB transaction. 🔴⭐
- **CDC (Change Data Capture)** — stream DB changes to downstream systems. 🔴⭐
- **Event sourcing** — store events as source of truth, rebuild state. 🔴⭐
- **CQRS** — separate read & write models. 🔴⭐
- **Dual-write problem** — why writing to DB + queue is unsafe; how outbox fixes it. 🔴⭐

## 12. Fault Tolerance & Resilience ⭐

- **Failure detection** — heartbeats, gossip, phi-accrual, timeouts. 🔴⭐
- **Retries with backoff + jitter** — avoiding retry storms/thundering herd. 🔴⭐
- **Circuit breaker** — stop calling a failing dependency; states. 🔴⭐
- **Bulkhead & isolation** — contain failures to one partition. 🟡⭐
- **Timeouts & deadlines** — bound waiting; propagate deadlines. 🟡⭐
- **Graceful degradation** — reduced functionality over total failure. 🔴⭐
- **Redundancy & failover** — active-active vs active-passive, automatic promotion. 🔴⭐
- **Rate limiting & load shedding** — protect under overload. 🟡⭐
- **Chaos engineering** — inject failures to validate resilience. 🔴

## 13. Messaging & Async Distribution ⭐

- **Message queues vs event streams** — RabbitMQ/SQS vs Kafka. 🟡⭐
- **Kafka internals** — partitions, offsets, consumer groups, replication, ISR, retention. 🔴⭐
- **Ordering guarantees** — per-partition ordering; global ordering cost. 🔴⭐
- **Backpressure** — handling faster producers than consumers. 🟡⭐
- **Dead-letter queues & poison messages** — failure isolation. 🟡⭐
- **Idempotent consumers** — surviving redelivery. 🔴⭐

## 14. Scalability Building Blocks

- **Horizontal vs vertical scaling** — scale out vs up. 🟡⭐
- **Stateless services** — push state to stores for easy scaling. 🟡⭐
- **Caching layers & invalidation** — read scaling; staleness. 🔴⭐
- **CDN & edge** — geo-distribution of static/media. 🟡
- **Load balancing** — L4/L7, algorithms, consistent-hash routing. 🟡⭐
- **Bloom filters / HyperLogLog / Count-Min Sketch** — probabilistic structures at scale. 🔴

---

## How these show up in interviews

Observability questions are usually **practical/design**: "How would you debug a latency spike across microservices?" (answer walks metrics → traces → logs), "Design monitoring for service X" (RED/golden signals + SLOs + alerting philosophy), "What's the difference between logs, metrics, traces and when do you use each?"

Distributed systems questions are usually **conceptual + trade-off**: "Explain CAP and where your system sits," "How do you guarantee exactly-once processing?" (spoiler: idempotency + at-least-once, not true exactly-once), "How would two services stay consistent without a distributed transaction?" (saga/outbox), "How does consistent hashing work?", "Handle a node failure without data loss."

### Highest-ROI to drill
Observability: three pillars + when to use each, RED/USE/four-golden-signals, SLI/SLO/error budgets, distributed tracing + context propagation, alert-on-symptoms philosophy, percentiles/tail latency.

Distributed systems: CAP/PACELC, consistency models, consistent hashing, replication (sync/async, leader models), quorums, idempotency & delivery semantics, saga/outbox/CDC, circuit breaker + retries-with-jitter, Raft at a high level, Kafka partition/consumer-group model.

The senior signal throughout: **name the trade-off, name the failure mode, name the mitigation.** e.g. "async replication → lower write latency but replication lag → stale reads → mitigate with read-your-writes or route critical reads to the leader."
