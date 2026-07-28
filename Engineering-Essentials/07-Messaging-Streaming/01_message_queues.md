# Message Queues (RabbitMQ / SQS)

> A **message queue** buffers work between producers and consumers. Producers enqueue; workers pull and process. Classic for **decoupling**, **spike absorption**, and **async jobs** (emails, image processing, webhooks).

## Plain English

| | **RabbitMQ** | **SQS** (AWS) |
|---|--------------|---------------|
| Model | Broker with exchanges/queues/bindings | Fully managed queue |
| Routing | Direct, topic, fanout exchanges | Usually one queue (+ SNS for fan-out) |
| Ops | You (or managed) run/cluster it | AWS operates it |
| Delivery | ACKs; configurable | At-least-once; visibility timeout |
| Ordering | Per-queue FIFO optional; not global | Standard = best effort; FIFO queues available |

```text
  Producer ──publish──► Queue ──consume──► Worker
                           │
                      buffer spikes
                      retry / DLQ on failure
```

**Visibility timeout (SQS):** after receive, message is hidden; if you don’t delete it in time, it reappears (retry).

## Essentials (must-know for this topic)

### Queue vocabulary

| Term | Meaning |
|------|---------|
| **Producer / consumer** | Enqueues work / pulls and processes |
| **Competing consumers** | N workers share one queue — each message → one worker |
| **ACK / delete** | Confirm success so message won’t redeliver |
| **Visibility timeout** (SQS) | Hide after receive; reappear if not deleted in time |
| **DLQ** | Dead-letter queue after N failed receives |
| **Exchange / binding** (Rabbit) | Routing rules from publish → queue(s) |

### RabbitMQ vs SQS (flashcard)

| | **RabbitMQ** | **SQS** |
|---|--------------|---------|
| Ops | You (or managed broker) | Fully managed AWS |
| Routing | Exchanges (direct/topic/fanout) | Usually one queue; SNS for fan-out |
| Delivery | ACK/NACK; flexible | At-least-once; visibility timeout |
| Ordering | Per-queue; not global | Standard ≈ best-effort; FIFO queues available |

### Queue vs Kafka log

| | **Queue (SQS/Rabbit)** | **Kafka** |
|---|------------------------|-----------|
| After success | Message typically **gone** | Offset advances; data **retained** |
| Best for | Job workers, task fan-in | Replay, many consumer groups, event bus |

## Simple example

**Image upload pipeline:**

```text
  API: save metadata → enqueue {imageId, s3Key}
  Workers: download → thumbnail → upload → update DB → ACK/delete
  Failures: after N receives → DLQ for humans/ops
```

**RabbitMQ topic exchange:** `orders.created`, `orders.shipped` → different queues bound by pattern.

## When to use / trade-offs

| Prefer **queue (Rabbit/SQS)** when… | Prefer **Kafka log** when… |
|-------------------------------------|----------------------------|
| Task distribution, job workers | Many consumers need replay / history |
| Delete-after-consume is fine | Event bus, audit, stream processing |
| Simple competing consumers | High-throughput partitioned log |

| Prefer **SQS** when… | Prefer **RabbitMQ** when… |
|----------------------|---------------------------|
| AWS-native, minimal ops | Complex routing, protocols (AMQP), on-prem |
| Standard serverless workers | Fine-grained ack/nack, priority queues |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Async queue | Resilience to spikes; decoupling | End-to-end latency; eventual processing |
| FIFO queue | Ordering per group | Lower throughput; stricter limits |
| Long visibility timeout | Time for slow jobs | Delayed retries on crash |

## Pitfalls

- Processing but forgetting **ACK/delete** → infinite redelivery.  
- ACK **before** side effect completes → silent loss on crash.  
- No **idempotency** under at-least-once.  
- Using a queue as a **database** (huge backlog with no drain plan).  
- SQS: visibility timeout shorter than work duration → duplicate workers.

## Interview trigger phrase

> “I’d put **async work on a queue** — SQS or Rabbit — so the API returns fast, workers scale independently, and failures go to a **DLQ** after bounded retries with idempotent handlers.”

## Exercise

**Design “send order confirmation email.”**

1. Sync in API vs enqueue — when each is OK.  
2. Worker crashes after SMTP send but before delete — what happens, how do you prevent double email?  
3. Compare SQS standard vs FIFO for this use case in one sentence each.
