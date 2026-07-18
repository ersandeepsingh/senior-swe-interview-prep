# Pub/Sub

> **Publish/subscribe** sends one event to **many** interested consumers. The publisher doesn’t know (or care) how many subscribers exist — you get **fan-out** without hard-coding N downstream calls.

## Plain English

| | Message queue (typical) | Pub/Sub |
|---|-------------------------|---------|
| Consumers | Competing — each message usually handled once | Fan-out — each subscriber gets a copy |
| Coupling | Work pipeline | Broadcast / notify many systems |
| Mental model | Job to do | Fact that happened |

```text
                    order_placed event
                           │
                           ▼
                    ┌─────────────┐
                    │  Pub/Sub    │
                    │   topic     │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
      Inventory         Analytics        Email
      service           pipeline         service
```

Publisher publishes once. New subscriber (e.g. fraud) plugs in later — no change to checkout code.

## Simple example

E-commerce **OrderPlaced**:

```text
  Checkout ──publish──► topic: orders
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
     Reserve stock    Update CRM     Send receipt
```

With sync fan-out you’d call three APIs in the request path — timeouts multiply, and adding a fourth system means editing checkout again.

## Why prefer one over the other

| Prefer **pub/sub** when… | Prefer a **single queue** when… |
|--------------------------|----------------------------------|
| Many independent reactions to one fact | Exactly one worker should do the job |
| You want loose coupling / plug-in consumers | Competing consumers for throughput on one task |
| Notifications, search index updates, metrics | “Encode this video” once |
| Adding a consumer shouldn’t touch the producer | Pipeline stages are a known linear workflow |

**Hybrid you’ll hear:** pub/sub topic → each subscription has its own queue (SNS→SQS). Fan-out *and* per-consumer buffering.

### Real systems (interview name-drops)

- **SNS, Google Pub/Sub, Redis Pub/Sub, NATS** — fan-out messaging.
- **Kafka/Pulsar “topics + consumer groups”** — can do both fan-out (groups) and competing consumers (within a group).

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Pub/sub fan-out | Easy to add consumers; producer stays dumb | Harder to reason about “all side effects done” |
| Sync multi-call from API | Clear success/fail in one place | Fragile latency; tight coupling |
| Shared topic, many subs | One event schema | Schema evolution / poison one consumer carefully |
| Fire-and-forget publish | Fast path | Need delivery guarantees + idempotent handlers |

**Common interview trap:** Calling everything “Kafka” when you only need a simple fan-out notification bus.

## Interview trigger phrase

> “For **OrderPlaced** I’d use **pub/sub** so inventory, email, and analytics each get a copy — checkout doesn’t call them one-by-one.”

## Exercise

**Design “user updated profile photo.”**

1. List 3 subscribers that should react (e.g. CDN invalidate, search, feed avatar cache) — argue pub/sub vs one queue.  
2. A new “moderation” service wants the same event next quarter — what changes in the producer?  
3. One sentence on failure: email subscriber is down — do photo upload / inventory-style paths still succeed?
