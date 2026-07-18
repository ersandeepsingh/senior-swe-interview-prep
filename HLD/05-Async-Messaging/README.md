# 5. Asynchronous Processing & Messaging

Decouple producers from consumers, absorb traffic spikes, and fan work out without making the request path wait. Interviewers expect you to **pick the right primitive** (queue vs pub/sub vs log) and name **delivery + failure** behavior out loud.

| # | Concept | One-line intent |
|---|---------|-----------------|
| 01 | [Message queue](01_message_queue.md) | Decouple producer/consumer; buffer spikes |
| 02 | [Pub/Sub](02_pubsub.md) | Fan-out one event to many subscribers |
| 03 | [Event streaming](03_event_streaming.md) | Kafka-style durable ordered log |
| 04 | [Delivery semantics](04_delivery_semantics.md) | At-most / at-least / exactly-once + idempotency |
| 05 | [DLQ & retries](05_dlq_retries.md) | Poison messages, backoff, dead-letter queues |
| 06 | [CDC](06_cdc.md) | Change data capture to sync search, caches, warehouses |
| 07 | [Batch vs stream](07_batch_vs_stream.md) | Nightly ETL vs live aggregation |

**How to use:** For each file — read Plain English → diagram → trade-offs → say the interview trigger phrase out loud → do the Exercise without peeking at notes.
