# Message Queue

> A **message queue** lets a producer fire work and walk away. The consumer pulls (or is pushed) later. You **decouple** services and **buffer** spikes so the DB or workers aren’t crushed by peak traffic.

## Plain English

| Piece | Role |
|-------|------|
| **Producer** | Puts a message on the queue (“order placed”) |
| **Queue** | Holds messages until consumed; absorbs bursts |
| **Consumer** | Processes one message at a time (or small batches) |

Sync call: caller waits for the callee. Queue: caller gets ACK from the broker; heavy work happens offline.

```text
  Checkout API                    Workers
       │                             │
       │  enqueue "charge+ship"      │
       ▼                             │
  ┌─────────────┐    poll/push       ▼
  │   Queue     │ ────────────────► Worker-1
  │ (buffer)    │ ────────────────► Worker-2
  └─────────────┘
       ▲
       │ spike of 10k orders
       │ queue grows; APIs stay fast
```

## Simple example

User clicks **Place Order**. You must not hold the HTTP request open while payment + inventory + email finish.

```text
  Client ──► Order API ──► enqueue order_created
                 │
                 └──► 202 Accepted / orderId
                          │
                          ▼
                    Payment worker → Inventory → Email
```

If payment is slow for 30s, the user still got a fast response. Retries and failures live with the workers, not the browser tab.

## Why prefer one over the other

| Prefer a **queue** when… | Prefer **sync RPC** when… |
|--------------------------|---------------------------|
| Work can finish after the response | Caller needs the result *now* to continue |
| Spikes would melt downstream | Downstream is fast and always required |
| You want independent scale of producers vs consumers | Transaction must complete in one request path |
| Email, thumbnails, fraud checks, webhooks | Login, read-your-write profile fetch |

**Not “async is always better.”** If the UI must show “payment succeeded” before the next screen, that step may stay sync (or sync + async for side effects).

### Real systems (interview name-drops)

- **SQS, RabbitMQ, Azure Queue, Celery/Redis queues** — classic work queues.
- **Often paired with:** DB write of “pending,” then queue, then worker marks “done.”

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Queue between services | Decoupling, spike absorption, independent scale | Operational complexity; eventual consistency of side effects |
| Fire-and-forget enqueue | Fast API latency | Harder end-to-end tracing; need retries/DLQ story |
| Many consumers on one queue | Throughput | Competing consumers — design for idempotency |
| Oversized sync chain | Simple mental model | Timeouts, cascading failures under load |

**Common interview trap:** Drawing a queue but never saying who retries, what’s idempotent, or how the user sees “still processing.”

## Interview trigger phrase

> “I’d put heavy or spike-y work on a **queue** so checkout stays fast — producers and consumers scale independently, and the queue buffers peaks.”

## Exercise

**Design “upload video → encode → notify.”**

1. Which steps stay on the request path vs go on a queue — and why?  
2. Upload traffic spikes 20× for one hour — what absorbs the spike, and what scales out?  
3. One sentence: what does the client poll (or get via webhook) to know encoding finished?
