# Kafka Event Streaming

> Kafka is a **durable, partitioned, append-only log**. Consumers track **offsets**; data is retained by time/size, so you can **replay**. That’s the core difference from classic delete-on-consume queues.

## Plain English

| Concept | Meaning |
|---------|---------|
| **Topic** | Named stream of events |
| **Partition** | Ordered append log; unit of parallelism |
| **Offset** | Position in a partition |
| **Producer** | Appends records (often keyed → partition) |
| **Consumer group** | Set of consumers; each partition → at most one member |
| **Retention** | Keep data even after consume (hours → forever) |

```text
  Topic "orders" — 3 partitions:

  P0: [e0][e1][e2]...     consumer A
  P1: [e0][e1]...         consumer B
  P2: [e0][e1][e2][e3]   consumer C

  Same group → parallel consume, no two members share a partition
  New group → can read from beginning (replay)
```

## Essentials (must-know for this topic)

### Topic / partition / offset / consumer group

| Concept | One-liner |
|---------|-----------|
| **Topic** | Named stream of related events |
| **Partition** | Ordered append-only log; unit of parallelism |
| **Offset** | Consumer’s position in a partition |
| **Key** | Routes records to a partition (same key → same partition → order) |
| **Producer** | Appends to partitions |
| **Consumer group** | Team of consumers; each partition assigned to **≤1** member in the group |
| **Retention** | Keep data by time/size even after consume → **replay** |
| **Lag** | How far consumer offset is behind log end |
| **Compacted topic** | Keep latest value per key (not full history) |

### Scaling rule

| Fact | Implication |
|------|-------------|
| Consumers in a group ≤ partitions that are active | Extra members sit idle |
| More partitions | More parallelism; cost/rebalance overhead |
| Order | **Inside a partition only** — not topic-wide |

## Simple example

**Order events:**

```text
  key = orderId  → all events for one order land in same partition → ordered
  value = {type: "OrderCreated", ...}

  Fraud service consumer group: processes in near-real-time
  Analytics group: replays last 7 days after a bugfix
```

**vs SQS:** SQS message typically disappears after success. Kafka keeps the log; lag is “how far behind is my offset.”

## When to use / trade-offs

| Prefer **Kafka** when… | Prefer **queue** when… |
|------------------------|------------------------|
| Multiple independent consumers need the same events | One worker pool drains tasks |
| Replay, audit, stream join/aggregate | Simple job buffer |
| High throughput, partitioned scale | Lower volume; simpler ops |

| Decision | You gain | You give up |
|----------|----------|-------------|
| More partitions | Parallelism | Harder total ordering; rebalance cost |
| Long retention | Replay, new consumers catch up | Storage cost |
| Compacted topic | Latest value per key | Not a full history |

## Pitfalls

- Treating Kafka like a queue and expecting **poison messages** to vanish (they don’t — you must skip/DLQ pattern).  
- Too few partitions → can’t scale consumers. Too many → overhead.  
- Changing partition count breaks key→partition affinity for old data.  
- Forgetting **idempotent producers / transactions** when claiming exactly-once.  
- Huge messages; use external blob + pointer.

## Interview trigger phrase

> “Kafka is a **partitioned commit log**: consumers advance **offsets**, retention enables **replay**, and **keys** give per-key order inside a partition — I’d use it as an event backbone, not as a simple task queue.”

## Exercise

**Clickstream + billing.**

1. Why put page views on Kafka but password-reset emails on SQS?  
2. Consumer group has 6 members and topic has 3 partitions — what happens?  
3. You deploy a buggy consumer; fix ships — how do you reprocess yesterday’s events safely?
