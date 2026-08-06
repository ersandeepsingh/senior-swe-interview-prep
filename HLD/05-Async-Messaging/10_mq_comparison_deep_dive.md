# Messaging Deep Dive — Queue vs RabbitMQ vs Kafka vs SQS

> Pick the **primitive** first (work queue vs event log), then the **product**. This sheet ties the folder together with decision rules and one end-to-end example.

## Quick map

| Need | Reach for |
|------|-----------|
| “Do this job once, delete when done” | **SQS** / Rabbit work queue / Redis queue |
| “Route by key/pattern to many queues” | **RabbitMQ** (exchanges) |
| “Many teams consume + replay history” | **Kafka** (log) |
| “Fan-out notify, no retention needed” | Pub/Sub (SNS+SQS, Rabbit fanout, Redis pub/sub*) |

\*Redis pub/sub is fire-and-forget — not durable.

```text
  Classic queue          Smart broker           Event log
  (SQS)                  (RabbitMQ)             (Kafka)
  delete-after-ack       exchange → queues      retain + offset
  simple jobs            flexible routing       replay + fan-out
```

---

## Side-by-side

| Dimension | SQS | RabbitMQ | Kafka |
|-----------|-----|----------|-------|
| Model | Managed queue | Broker + exchanges | Distributed log |
| Retention after read | Gone (visibility timeout) | Gone after ack | Kept until retention |
| Replay | No (unless you designed it) | No | Yes |
| Routing | Limited (SNS fan-out) | Excellent | By key → partition |
| Ordering | Best-effort / FIFO queues | Per-queue | Per-partition |
| Throughput | High (managed) | High | Extremely high |
| Ops | Lowest | Medium | Highest |
| Multi-consumer same data | Duplicate publishes / SNS | Fanout bindings | Free via consumer groups |

---

## One business story — three designs

**Feature:** User uploads video → encode → update DB → email user → update search index.

### Design A — SQS (simple, senior for this scope)

```text
  API ──► SQS: video.encode
              │
           Worker encodes
              │
              ├── update DB
              ├── SES email
              └── (optional) second queue: search.index
```

**Why OK:** One pipeline, no multi-team replay need, managed ops.  
**Watch:** Idempotency on `video_id`; DLQ after N receives.

### Design B — RabbitMQ (routing-centric)

```text
  API publish video.uploaded → topic exchange media
       ├── video.uploaded → encode_queue
       └── video.encoded  → email_queue
                        → search_queue
```

**Why OK:** Clear routing topology; different prefetch per queue.  
**Watch:** Persistent msgs + confirms; quorum queues for critical work.

### Design C — Kafka (platform event bus)

```text
  API ──► topic media.events (key=video_id)
              │
              ├─ group encoder
              ├─ group emailer
              └─ group search-indexer
  retention 7d → reprocess search after mapping fix
```

**Why OK:** Shared bus; independent scale/lag; replay.  
**Overkill if:** Only one team and no replay story — SQS is cleaner.

---

## Decision flowchart

```text
  Do multiple systems need the SAME events + replay?
       YES → Kafka (or Pulsar / Kinesis)
       NO
       │
       Need complex routing keys / patterns?
       YES → RabbitMQ
       NO
       │
       Want zero broker ops on AWS?
       YES → SQS (+ SNS if fan-out)
       NO  → RabbitMQ or Redis queue (small scale)
```

---

## Shared rules (all tools)

1. **At-least-once + idempotent consumers**  
2. **DLQ / poison handling**  
3. **Don’t hold DB transactions open across slow broker calls blindly** — outbox pattern for reliable publish  
4. **Observe:** depth (queue) or **lag** (Kafka), error rate, age of oldest message  
5. **Payload:** IDs + thin events; store blobs in S3  

### Transactional outbox (critical senior pattern)

```text
  Same DB transaction:
    1) INSERT order
    2) INSERT outbox(event)
  COMMIT
       │
  Publisher polls outbox → broker
       │
  Mark outbox published
```

Avoids “DB committed but message lost” (dual-write problem).

---

## Deep-dive files in this folder

| File | Focus |
|------|--------|
| [01_message_queue.md](01_message_queue.md) | Queue concept |
| [02_pubsub.md](02_pubsub.md) | Fan-out |
| [03_event_streaming.md](03_event_streaming.md) | Log concept |
| [04_delivery_semantics.md](04_delivery_semantics.md) | At-least / exactly-once |
| [05_dlq_retries.md](05_dlq_retries.md) | Failure handling |
| [08_rabbitmq.md](08_rabbitmq.md) | RabbitMQ in depth |
| [09_kafka.md](09_kafka.md) | Kafka in depth |

---

## Interview trigger phrase

> “For encode-and-email I’d start with **SQS**; if we become an event platform with replay I’d move the domain events to **Kafka**; I’d use **RabbitMQ** when routing topology is the main complexity.”

## Exercise

1. Pick SQS vs Kafka for “send password-reset email” — justify in one sentence.  
2. Where does the **outbox** sit in Design C, and what failure does it prevent?  
3. Name one metric you’d alert on for SQS and one for Kafka.
