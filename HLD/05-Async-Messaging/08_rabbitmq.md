# RabbitMQ Deep Dive

> **RabbitMQ** is a general-purpose **message broker** (AMQP). Producers publish to an **exchange**; the exchange **routes** to **queues**; consumers **ack** when done. Best for flexible routing, work queues, and classic request/async job patterns.

## Plain English

| Piece | Role |
|-------|------|
| **Producer** | Publishes a message to an exchange (not usually straight to a queue) |
| **Exchange** | Routing brain — decides which queue(s) get the message |
| **Binding** | Rule linking exchange → queue (routing key / headers) |
| **Queue** | Buffer of messages waiting for consumers |
| **Consumer** | Pulls/pushes messages; **acks** (or nacks) after processing |
| **Virtual host** | Namespace/isolation inside one broker |

```text
  Producer
      │  publish(routing_key, body)
      ▼
  ┌─────────────┐
  │  Exchange   │──── binding rules ────┐
  └─────────────┘                       │
         │                              ▼
         ├──────────────────────► ┌──────────┐
         │                        │  Queue A │──► Consumer 1
         └──────────────────────► │  Queue B │──► Consumer 2
                                  └──────────┘
```

**Mental model:** Post office. Exchange = sorting facility; queues = mailboxes; routing key = address label.

---

## Exchange types (the routing toolkit)

| Type | Behavior | Use when |
|------|----------|----------|
| **Direct** | Exact match on routing key | `payment.success` → payments queue |
| **Topic** | Pattern match (`*`, `#`) | `order.*.created`, `log.eu.#` |
| **Fanout** | Broadcast to all bound queues | “Notify everyone” — cache bust, websockets |
| **Headers** | Match on header attributes | Rare; complex attribute routing |

```text
  Topic example:
    routing key:  order.eu.created
    binding:      order.*.created     ✓
    binding:      order.#             ✓
    binding:      order.us.*          ✗
```

---

## Simple end-to-end example — order pipeline

**Goal:** Checkout API stays fast; payment, email, and inventory run async.

```text
  Checkout API
       │ publish routing_key="order.created"
       ▼
  exchange: orders (topic)
       │
       ├── binding order.created → queue: payments
       ├── binding order.created → queue: inventory
       └── binding order.#       → queue: audit_log

  payments consumer  → charge card → publish order.paid
  inventory consumer → reserve SKU
  email consumer     ← bound to order.paid
```

### Pseudocode (producer)

```python
# After writing order row as "pending"
channel.basic_publish(
    exchange="orders",
    routing_key="order.created",
    body=json.dumps({"order_id": "ord_123", "amount": 49900}),
    properties=pika.BasicProperties(
        delivery_mode=2,          # persistent
        content_type="application/json",
        message_id="ord_123",     # idempotency hint
        headers={"tenant": "acme"},
    ),
)
return {"order_id": "ord_123", "status": "pending"}
```

### Pseudocode (consumer)

```python
def on_message(ch, method, properties, body):
    order = json.loads(body)
    try:
        charge(order["order_id"], order["amount"])  # idempotent by order_id
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except TransientError:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    except PermanentError:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        # send to DLQ via dead-letter exchange
```

---

## Common patterns

### 1) Competing consumers (work queue)

```text
  Queue: image_resize
     │
     ├── Worker-1
     ├── Worker-2
     └── Worker-3
  Each message goes to ONE idle worker (load shared).
```

Use **prefetch (QoS)** so one fast worker doesn’t grab everything while others sit idle:

```python
channel.basic_qos(prefetch_count=10)  # unacked messages per consumer
```

### 2) Pub/Sub (fanout)

```text
  exchange: cache_bust (fanout)
      ├── queue: api_a_local
      ├── queue: api_b_local
      └── queue: edge_invalidator
  One publish → all queues get a copy.
```

### 3) RPC over RabbitMQ (request/reply)

```text
  Client publishes to rpc_queue with reply_to=callback_queue + correlation_id
  Server processes, publishes result to reply_to
  Client matches correlation_id
```

Useful for internal sync-looking calls with timeout — don’t use for public HTTP if a queue isn’t needed.

### 4) Delayed / retry with TTL + DLX

```text
  Main queue ──nack/expire──► retry_queue (TTL 30s)
                                  │ dead-letter
                                  ▼
                              Main queue again
  After N attempts → parking_lot / DLQ for humans
```

---

## Reliability checklist

| Knob | Meaning | Prefer |
|------|---------|--------|
| **Persistent messages** | Survive broker restart if queue durable | `delivery_mode=2` + durable queue |
| **Publisher confirms** | Broker ACKs it accepted the message | On for money/orders |
| **Consumer ack** | Manual ack after side effects succeed | Manual, not auto-ack |
| **Prefetch** | Limit in-flight per consumer | Tune to avoid overload |
| **DLX / DLQ** | Poison messages don’t block the queue | Always for prod workers |
| **Idempotent handler** | Duplicates won’t double-charge | Mandatory with at-least-once |

**Delivery reality:** RabbitMQ gives **at-least-once** in the common reliable setup. Design consumers as idempotent.

---

## Clustering / HA (interview level)

```text
  Classic mirrored queues (older) / quorum queues (modern)
  Clients connect via load balancer to any node
  Quorum queues: Raft-based, better for durability under partition
```

**Senior note:** Prefer **quorum queues** for critical work in modern RabbitMQ; classic mirroring has known footguns.

---

## Why RabbitMQ vs Kafka / SQS

| Prefer **RabbitMQ** when… | Prefer something else when… |
|---------------------------|-----------------------------|
| Complex routing (topic/headers) | Need huge retained log + replay (→ Kafka) |
| Per-message ack / flexible patterns | Want fully managed, dumb queue (→ SQS) |
| Low-latency task dispatch | Multi-team event bus with independent offsets (→ Kafka) |
| Protocol flexibility (AMQP, MQTT plugins) | Extreme throughput append-only streams |

---

## Trade-offs

| Decision | Gain | Cost |
|----------|------|------|
| Smart broker (exchanges) | Routing in infra, dumb producers | Broker is critical path; ops matter |
| Many small queues | Isolation per workload | Management overhead |
| Persistent + confirms | Durability | Slightly higher latency |
| Auto-ack | Simpler code | Message loss on crash mid-process |

---

## Worked example — notification system

```text
  event: user.signup
       │
       ▼
  exchange: notifications (topic)
       │
       ├── user.signup → queue: email_welcome
       ├── user.signup → queue: sms_otp          (if phone present — filter in consumer)
       └── user.#      → queue: analytics_ingest

  email_welcome:
    prefetch=5
    idempotency key = user_id + "welcome"
    on 5xx from SES → nack requeue with backoff via TTL retry queue
    on invalid email → nack no-requeue → DLQ
```

**API path:** `POST /signup` writes user + publishes event → returns 201. Email is eventually consistent.

---

## Interview trigger phrase

> “I’d use **RabbitMQ** when I need flexible AMQP routing and classic work queues — publish to a topic exchange, bind payments/inventory/email queues, manual ack + DLX, and idempotent consumers for at-least-once delivery.”

## Exercise

1. Design routing for `order.created`, `order.paid`, `order.shipped` so shipping only runs after paid — exchange type + keys?  
2. Why is `prefetch_count=0` (unlimited) dangerous under load?  
3. Consumer crashes after charging but before ack — what must your payment table enforce?
