# 7. Messaging & Streaming ⭐

Decouple producers from consumers, absorb spikes, and move work off the request path. Interviewers expect you to **pick the right primitive** (queue vs pub/sub vs log) and name **delivery + ordering + failure** behavior out loud.

| # | Topic | One-line intent |
|---|-------|-----------------|
| 01 | [Message queues](01_message_queues.md) | RabbitMQ/SQS — decoupling, work queues, DLQs |
| 02 | [Kafka event streaming](02_kafka_event_streaming.md) | Partitions, offsets, consumer groups, replay |
| 03 | [Pub/Sub](03_pubsub.md) | Fan-out one event to many subscribers |
| 04 | [Delivery semantics](04_delivery_semantics.md) | At-most / at-least / exactly-once + idempotency |
| 05 | [Ordering & partitioning](05_ordering_partitioning.md) | Per-key ordering guarantees |
| 06 | [Event-driven architecture](06_event_driven_architecture.md) | Choreography vs orchestration, CQRS, sourcing |
| 07 | [Backpressure & DLQ](07_backpressure_dlq.md) | Poison messages, retries with backoff |

**How to use:** For each file — read Plain English → example → trade-offs → say the interview trigger phrase out loud → do the Exercise without peeking.
