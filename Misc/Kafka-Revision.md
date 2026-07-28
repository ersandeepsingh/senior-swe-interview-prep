# Apache Kafka — Senior Engineer Revision

**What it is:** A distributed, durable, replayable **event streaming platform** (a distributed commit log). Producers append events to topics; many consumers read them independently at their own pace. Built for very high throughput and retention, not per-message routing.

---

## 1. Core concepts

- **Topic** — a named stream of events (like a category/log).
- **Partition** — a topic is split into partitions; each is an **ordered, append-only, immutable log**. Partitions are the unit of parallelism and ordering.
- **Offset** — a monotonically increasing ID of a message within a partition. Consumers track their offset (where they've read up to).
- **Producer** — writes events; chooses the partition via a key (same key → same partition → ordering) or round-robin if no key.
- **Consumer** — reads events; commits offsets to remember progress.
- **Consumer group** — a set of consumers sharing the work of a topic. **Each partition is consumed by exactly one consumer in a group** → parallelism is capped by partition count.
- **Broker** — a Kafka server; a **cluster** is many brokers.
- **Replication** — each partition has a **leader** + follower replicas on other brokers; the **ISR** (in-sync replicas) are those caught up enough to be promoted.
- **Retention** — messages are kept for a time/size window (e.g., 7 days) regardless of consumption → **replay** is possible.
- **Coordination:** historically **ZooKeeper**; modern Kafka uses **KRaft** (built-in Raft) to remove the ZooKeeper dependency.

```
Topic "orders" (3 partitions)
 P0: [o0][o1][o2][o3...]     ← ordered by offset
 P1: [o0][o1...]
 P2: [o0][o1][o2...]
Consumer group "billing" (3 consumers) → 1 partition each
```

---



## 2. Ordering & partitioning (key interview point)

- **Ordering is guaranteed only within a partition**, not across a topic.
- To keep related events ordered, give them the **same key** so they land in the same partition.

*Example:* key every event by `order_id` → all events for an order (`Created → Paid → Shipped`) stay ordered on one partition. Different orders spread across partitions for parallelism.

- **Trade-off:** global total ordering would require a single partition → no parallelism. Scope ordering to the key that matters.

---



## 3. Delivery semantics (very frequently asked)

- **At-most-once:** commit offset *before* processing → crash loses the message. Rare.
- **At-least-once (default/common):** process, *then* commit offset → a crash between the two causes redelivery (duplicates). **Consumers must be idempotent.**
- **Exactly-once (EOS):** Kafka supports it *within Kafka* via **idempotent producers** (dedup by producer ID + sequence) and **transactions** (atomic write across partitions + offset commit). True end-to-end exactly-once to an external system still needs idempotent writes on your side.

*Senior line:* "In practice I design for at-least-once + idempotent consumers (dedupe on a business key), which gives effectively-once. I only reach for Kafka transactions when I need atomic read-process-write within Kafka."

---



## 4. Durability & acks (producer side)

- `acks=0` — fire and forget (fastest, can lose data).
- `acks=1` — leader acknowledges (loses data if leader dies before replication).
- `acks=all` — leader + all ISR acknowledge (safest). Combine with `min.insync.replicas=2` so a write fails rather than under-replicating.
- **Idempotent producer** (`enable.idempotence=true`) prevents duplicates from producer retries.

*Durability recipe:* `acks=all` + `replication.factor=3` + `min.insync.replicas=2` → survives one broker loss with no data loss.

---



## 5. Consumers, offsets & rebalancing

- **Offset commit:** auto (periodic) or manual (`commitSync` after processing — safer for at-least-once).
- **Consumer lag** = latest offset − committed offset. Rising lag = consumers can't keep up (backpressure signal) → add consumers (up to partition count) or optimize processing.
- **Rebalancing:** when consumers join/leave, partitions are reassigned. During a rebalance consumption pauses briefly; frequent rebalances hurt. **Cooperative/incremental rebalancing** reduces the "stop-the-world" effect.
- `__consumer_offsets` — internal topic where Kafka stores committed offsets.

---



## 6. Scaling

- **Add partitions** to increase parallelism (but you can't decrease, and adding changes key→partition mapping, breaking ordering for existing keys — plan partition count upfront).
- **Add brokers** to spread partitions/replicas and increase cluster capacity.
- **Add consumers** to a group up to the number of partitions (extra consumers sit idle).
- **Throughput levers:** batching (`linger.ms`, `batch.size`), compression (`lz4`/`zstd`), and Kafka's zero-copy disk→network path (why it's so fast despite using disk).

---



## 7. Common patterns

- **Event-driven microservices:** services publish domain events; others subscribe (decoupling).
- **Log/metrics pipeline:** high-volume ingest → stream processors → storage.
- **CQRS / event sourcing:** the Kafka log as the source of truth; rebuild state by replay.
- **CDC:** stream DB changes (via Debezium) into Kafka to sync caches/search/warehouses.
- **Stream processing:** Kafka Streams / ksqlDB / Flink for joins, windowed aggregations.
- **Dead-letter topic:** route messages that repeatedly fail processing to a separate topic.

---



## 8. Gotchas & senior talking points

- **Partition count is hard to change later** — under-provisioning caps parallelism; over-provisioning adds overhead. Choose deliberately.
- **Ordering only per partition** — a frequent bug source when people assume global order.
- **Poison messages** can stall a partition (Kafka won't skip ahead) — use retry topics / DLQ + max retries.
- **Rebalance storms** from short session timeouts or slow processing → tune `max.poll.interval.ms`, use static membership.
- **Not a queue for per-message routing** — no per-message ack/redelivery like RabbitMQ; consumers manage offsets.
- **Retention vs storage** — long retention = big disk; know your policy.

---



## 9. Kafka vs RabbitMQ (the classic comparison)


|             | Kafka                                           | RabbitMQ                                                 |
| ----------- | ----------------------------------------------- | -------------------------------------------------------- |
| Model       | distributed log (pull)                          | message broker/queue (push)                              |
| Retention   | keeps messages (replayable)                     | usually deleted after ack                                |
| Ordering    | per partition                                   | per queue                                                |
| Consumption | consumers track offset; many groups read all    | competing consumers; message removed after ack           |
| Throughput  | very high (millions/s)                          | high but lower                                           |
| Routing     | simple (topic/partition)                        | rich (exchanges, routing keys, topics)                   |
| Best for    | event streaming, analytics, replay, high volume | task queues, complex routing, per-message workflows, RPC |


*Rule of thumb:* **streaming/event log & replay → Kafka**; **work queue & flexible routing → RabbitMQ**.

---



## 10. Quick interview Q&A

- **How does Kafka guarantee ordering?** Only within a partition; key your messages to control partition assignment.
- **How does Kafka scale consumers?** Consumer groups: one partition per consumer, so parallelism ≤ partitions.
- **How do you avoid data loss?** `acks=all` + RF≥3 + `min.insync.replicas=2` + idempotent producer.
- **How do you handle duplicates?** Idempotent consumers (dedupe on a business key) or Kafka transactions/EOS.
- **What happens if a broker dies?** An ISR replica is promoted to leader; producers/consumers reconnect; no data loss if replicated.
- **How do you replay?** Reset the consumer group's offset (e.g., to earliest) — messages are still retained.
- **Kafka vs RabbitMQ?** See table — streaming/replay/high-volume vs routing/task-queue.

