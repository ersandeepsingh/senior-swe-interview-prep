# 14. Classic HLD — Infrastructure / Platform

Platform building blocks interviewers use to probe **distributed systems fundamentals**: hashing, quorum, logs, coordination, and metadata. These designs show up as the *system under design* or as a dependency you must reason about inside a larger product.

| # | Problem | Crux | Diff |
|---|---------|------|------|
| 01 | [Distributed Cache](01_distributed_cache.md) | Consistent hashing + invalidation | 🔴 |
| 02 | [Key-Value Store (Dynamo)](02_key_value_store_dynamo.md) | Consistent hashing + tunable consistency | 🔴 |
| 03 | [Distributed Message Queue (Kafka)](03_distributed_message_queue_kafka.md) | Durable ordered log + delivery | 🔴 |
| 04 | [Unique ID Generator](04_unique_id_generator.md) | Uniqueness + ordering without coordination | 🟡 |
| 05 | [Distributed Job Scheduler](05_distributed_job_scheduler.md) | Leader election + fault tolerance | 🔴 |
| 06 | [Distributed File System](06_distributed_file_system.md) | Metadata mgmt + replication | 🔴 |
| 07 | [API Rate Limiter as a Service](07_api_rate_limiter_as_service.md) | Distributed counting | 🟡 |
| 08 | [Config / Feature-Flag Service](08_config_feature_flag_service.md) | Low-latency reads + propagation | 🟡 |

**How to use:** Clarify → estimate → API/model → boxes → **deep-dive the crux** → failures. Say the trigger phrase out loud; do the Exercise without peeking.

**Building blocks to refresh first:** consistent hashing, replication/quorum, event streaming, leader election, cache invalidation, rate limiting.
