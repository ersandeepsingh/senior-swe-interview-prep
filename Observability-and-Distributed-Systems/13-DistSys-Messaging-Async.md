# 13 · Distributed Systems — Messaging & Async Distribution

> Decoupling services in time so they don't have to be up and fast simultaneously.

---

## Message queues vs event streams

**Definition:** **Message queues** (RabbitMQ, SQS) deliver a message to a consumer and typically remove it once processed. **Event streams** (Kafka) are durable, replayable, ordered logs that many consumers read independently at their own offset.

**Simple explanation:** A queue is like a task list — a worker takes a job and it's gone. A stream is like a shared logbook — messages stay for a retention period, multiple consumer groups each read all of them, and you can rewind. Queues suit work distribution; streams suit event broadcasting, replay, and analytics.

**Example:**
- Queue: image-resize jobs — one worker grabs each job, does it, job removed.
- Stream: `user.signed_up` events — the email service, analytics service, and CRM sync each independently consume the whole stream; a new consumer can replay history from the beginning.

---

## Kafka internals

**Definition:** Kafka's core mechanics: **topics** split into **partitions**, messages addressed by **offset**, consumers grouped into **consumer groups**, partitions **replicated** across brokers with an **in-sync replica (ISR)** set, and messages kept per a **retention** policy.

**Simple explanation:** A topic is divided into partitions for parallelism. Each message in a partition has a sequential offset. Within a consumer group, each partition is read by exactly one consumer (so parallelism ≤ partition count). Replication keeps copies on other brokers; the ISR is the set of replicas caught up enough to be promoted if the leader fails. Data is kept for a retention window (time or size), enabling replay.

**Example:** Topic `orders` has 6 partitions and replication factor 3. A consumer group of 3 consumers gets 2 partitions each. If a broker holding a partition leader dies, an ISR replica is promoted with no data loss. A new analytics job can reset its offset to 0 and reprocess a week of orders.

---

## Ordering guarantees

**Definition:** The promises about the sequence in which messages are delivered — typically ordering *within* a partition, not across partitions.

**Simple explanation:** Kafka guarantees order only within a single partition. To keep related events ordered (e.g., all events for one user/order), you route them to the same partition using a partition key. Global total ordering would require a single partition — killing parallelism — so you scope ordering to the key that matters.

**Example:** All events for `order_id=991` use `991` as the partition key, so they always land in the same partition and are consumed in order (`Created → Paid → Shipped`). Events for different orders may interleave across partitions — which is fine.

---

## Backpressure

**Definition:** Handling the situation where producers generate work faster than consumers can process it.

**Simple explanation:** If input outpaces processing, something must give — or you run out of memory. Backpressure is the feedback that slows producers, buffers with bounds, or sheds load. Streams like Kafka naturally buffer on disk (consumers just fall behind, measured as *consumer lag*); in-memory systems must actively signal "slow down."

**Example:** A consumer's Kafka lag grows to 2M messages — a clear backpressure signal. You respond by scaling out consumers (up to the partition count) or optimizing processing. In a reactive HTTP stream, the consumer instead requests only N items at a time so the producer can't overwhelm it.

---

## Dead-letter queues & poison messages

**Definition:** A **poison message** is one that repeatedly fails processing; a **dead-letter queue (DLQ)** is where such messages are moved after N failed attempts so they stop blocking the pipeline.

**Simple explanation:** One malformed message shouldn't jam the queue forever by being retried infinitely. After a few failures, you shunt it to a DLQ for later inspection/repair, and the pipeline moves on. Engineers monitor the DLQ and fix or replay its contents.

**Example:** A message with corrupt JSON fails parsing 5 times. Instead of retrying forever (and blocking everything behind it), it's routed to `orders.DLQ`. An engineer later inspects it, finds the bug, fixes the producer, and replays the DLQ.

---

## Idempotent consumers

**Definition:** Consumers built so that processing the same message more than once produces the same result as processing it once.

**Simple explanation:** Because messaging is at-least-once, consumers *will* occasionally see duplicates (e.g., after a rebalance or redelivery). Idempotent consumers dedupe — usually by tracking processed message IDs or using upserts — so duplicates don't double-charge, double-ship, or double-count.

**Example:** A payment consumer records each processed `payment_id` in a `processed` table. If Kafka redelivers the same event after a consumer restart, the consumer sees `payment_id` already recorded and skips it — the customer is charged exactly once despite at-least-once delivery.
