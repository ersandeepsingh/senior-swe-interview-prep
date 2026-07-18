# 7. Reliability, Resilience & Observability

Stay up when parts fail, fail safely when you can’t, and **see** what’s broken. Seniors talk **blast radius**, **RPO/RTO**, and **SLOs** — not only “we’ll add retries.”

| # | Concept | One-line intent |
|---|---------|-----------------|
| 01 | [Replication & failover](01_replication_failover.md) | Redundancy + promotion → survive node loss |
| 02 | [Circuit breaker / bulkhead / timeout](02_circuit_breaker_bulkhead_timeout.md) | Contain cascading failures |
| 03 | [Graceful degradation](03_graceful_degradation.md) | Serve reduced functionality under stress |
| 04 | [Rate limiting & quotas](04_rate_limiting_quotas.md) | Per-tenant fairness + protection |
| 05 | [Monitoring / logging / tracing](05_monitoring_logging_tracing.md) | Metrics, logs, traces — 3 pillars |
| 06 | [Disaster recovery](06_disaster_recovery.md) | RPO / RTO, backups, multi-region |
| 07 | [Chaos / fault injection](07_chaos_fault_injection.md) | Deliberately test resilience |

**How to use:** For each file — read Plain English → diagram → trade-offs → say the interview trigger phrase out loud → do the Exercise without peeking at notes.
