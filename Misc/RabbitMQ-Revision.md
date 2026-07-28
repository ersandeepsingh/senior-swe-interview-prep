# RabbitMQ — Senior Engineer Revision

**What it is:** A traditional **message broker** implementing (primarily) AMQP. Producers publish to **exchanges**, which route messages to **queues** based on rules; consumers pull from queues and **ack** each message. Strength = flexible routing and per-message reliability, not massive-throughput streaming.

---

## 1. Core concepts (the AMQP model)

- **Producer** — publishes a message (never directly to a queue — always to an exchange).
- **Exchange** — receives messages and routes them to queues using bindings + routing keys.
- **Queue** — buffer that holds messages until consumed and acked.
- **Binding** — the rule linking an exchange to a queue (with a routing key / pattern).
- **Routing key** — a label on the message the exchange uses to decide routing.
- **Consumer** — receives messages (push model) and **acknowledges** them.
- **Connection / Channel** — a TCP connection carries multiple lightweight channels (multiplexing).
- **Virtual host (vhost)** — logical isolation/namespacing within a broker.

```
Producer → [Exchange] --binding(routing key)--> [Queue] → Consumer(s)
```

---

## 2. Exchange types (the heart of RabbitMQ, always asked)

| Type | Routing behavior | Example |
|---|---|---|
| **Direct** | exact routing-key match | route `payment.success` to the payments queue |
| **Topic** | wildcard pattern match (`*`=one word, `#`=zero+ words) | `order.*.eu` → European order events |
| **Fanout** | broadcast to all bound queues (ignores key) | publish an event to email + analytics + audit queues |
| **Headers** | route on message headers instead of routing key | route by `{format: pdf, type: report}` |

**Topic example:**
```
Binding "order.#"     → all order events
Binding "order.*.eu"  → order.created.eu, order.shipped.eu (not order.created)
```

---

## 3. Message acknowledgement & reliability (senior focus)

- **Manual ack** (`basic.ack`): consumer confirms after successful processing → RabbitMQ removes it. If the consumer dies before acking, the message is **requeued** and redelivered → at-least-once → **make consumers idempotent**.
- **Auto-ack:** message removed on delivery (fast, at-most-once — risk of loss). Avoid for important work.
- **`basic.nack` / `basic.reject`:** negatively acknowledge; `requeue=true` puts it back, `requeue=false` drops or sends to DLX.
- **Prefetch (`basic.qos`)**: limits unacked messages per consumer → fair dispatch and backpressure (e.g., prefetch=1 means "don't give me a new task until I ack the current one").

---

## 4. Durability & persistence (avoid data loss)
Three things must all hold to survive a broker restart:
1. **Durable queue** (`durable=true`) — queue definition survives restart.
2. **Persistent messages** (`delivery_mode=2`) — messages written to disk.
3. **Publisher confirms** — broker acks the producer once it has safely taken responsibility (so the producer knows it wasn't lost).

*Note:* persistence has a throughput cost (disk writes). Also, `durable + persistent` still has a tiny window unless publisher confirms + mirrored/quorum queues are used.

---

## 5. Dead Letter Exchange (DLX) & retries
- A **DLX** receives messages that are rejected (`nack` with requeue=false), expire (TTL), or exceed queue length.
- Pattern: main queue → on repeated failure → **dead-letter queue** for inspection/replay, so one poison message doesn't block the pipeline.
- **Delayed retry:** route failures to a "wait" queue with a TTL that dead-letters back to the main queue after a delay (exponential backoff without busy-looping).

```
main.queue --(nack, no requeue)--> DLX --> dead.letter.queue (inspect/replay)
```

---

## 6. Advanced features / message controls
- **TTL** — per-message or per-queue expiry.
- **Priority queues** — higher-priority messages delivered first.
- **Lazy queues** — keep messages on disk to handle very large backlogs without eating RAM.
- **Quorum queues** — Raft-based replicated queues (modern replacement for classic mirrored queues) for HA and data safety.
- **RPC pattern** — request/reply using a `reply_to` queue + `correlation_id`.

---

## 7. Delivery patterns
- **Work queue (competing consumers):** one queue, multiple consumers share the load (each message to exactly one consumer). Scale by adding consumers.
- **Pub/Sub (fanout):** one message copied to many queues (each subscriber gets its own copy).
- **Routing (direct/topic):** selective delivery based on keys/patterns.
- **RPC:** synchronous-style request/response over queues.

*Scaling reads:* unlike Kafka (offset-based, all groups read everything), RabbitMQ removes a message once acked — adding consumers to one queue **splits** work, it doesn't duplicate it. To fan out, bind multiple queues.

---

## 8. HA & clustering
- **Clustering:** multiple nodes act as one broker (shared metadata). By default a queue lives on one node.
- **Quorum queues** (recommended) replicate a queue across nodes via Raft for automatic failover and data safety.
- **Mirrored queues** = the older HA approach (deprecated in favor of quorum queues).
- Use a load balancer / connection retry so clients reconnect on node failure.

---

## 9. Gotchas & senior talking points
- **Throughput ceiling:** great for tens of thousands msg/s; not designed for Kafka-scale millions/s with long retention.
- **Messages disappear after ack** — no replay like Kafka; if you need history/replay, RabbitMQ is the wrong tool (or use Streams plugin).
- **Unbounded queues** can exhaust memory → use TTL, max-length, lazy queues, and backpressure (prefetch).
- **Poison messages** requeued forever block progress → cap retries + DLX.
- **Auto-ack data loss** — a classic mistake; use manual ack for important work.
- **Ordering** is per-queue and only with a single consumer + no requeue; concurrency/redelivery can reorder.
- **Connection churn** — reuse connections, use channels; opening a connection per message kills performance.

---

## 10. When to use RabbitMQ (vs Kafka)
Choose **RabbitMQ** when you need:
- Complex/flexible **routing** (topic/header/fanout exchanges).
- **Per-message** reliability, acks, redelivery, priorities, TTL.
- **Task/work queues** and RPC-style request/reply.
- Moderate throughput with low operational complexity.

Choose **Kafka** when you need: huge throughput, long retention/replay, event streaming, multiple independent consumer groups reading the same data, ordered logs.

*One-liner:* **RabbitMQ = smart broker / dumb consumer** (broker does routing, tracks delivery). **Kafka = dumb broker / smart consumer** (broker just stores a log, consumers track offsets).

---

## 11. Quick interview Q&A
- **How does routing work?** Producer → exchange → (bindings + routing key) → queue(s). Four exchange types: direct, topic, fanout, headers.
- **How do you guarantee a message isn't lost?** Durable queue + persistent message + publisher confirms + manual consumer ack (+ quorum queues for HA).
- **How do you handle a failing/poison message?** `nack` (requeue=false) → DLX → DLQ, with a retry limit and optionally delayed retry via TTL.
- **How do you apply backpressure / fair dispatch?** Prefetch (`basic.qos`) to limit unacked messages per consumer.
- **RabbitMQ vs Kafka?** Routing + per-message workflows vs streaming + replay + high volume.
- **How do you scale consumers?** Add competing consumers to a queue (work splits); for fan-out, bind multiple queues to a fanout/topic exchange.
