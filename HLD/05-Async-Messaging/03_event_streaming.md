# Event Streaming

> **Event streaming** (Kafka-style) is a **durable, ordered log**. Producers append; many consumer groups read at their own pace. You keep history for replay, not just “delete after ack” like a classic queue.

## Plain English

| Idea | Meaning |
|------|---------|
| **Log / topic** | Append-only sequence of events |
| **Partition** | Shard of the log — order guaranteed *within* a partition |
| **Offset** | Consumer’s cursor (“I’ve read up to 1042”) |
| **Consumer group** | Team of workers sharing partitions; each event processed once *per group* |

```text
  Producers                  Topic (partitions)
  P1, P2 ──append──►  ┌─ p0: e1 e2 e5 e8 ...
                      ├─ p1: e3 e4 e6 ...
                      └─ p2: e7 e9 ...
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
         Group A         Group B       Group C
        (billing)       (search)      (warehouse)
         own offsets     own offsets   can replay
```

Queues: message often gone after successful consume. Streams: retained for hours/days — **replay** after a bug fix.

## Simple example

Clickstream: every page view appended to `pageviews` keyed by `userId` (same user → same partition → order preserved).

```text
  user-42 views ──► partition hash(user-42) ──► ordered events
  Analytics group at offset 1_000_000
  Fraud group still at offset 900_000   ← slower, independent
```

Bug in analytics? Fix code, **reset offset**, reprocess. Classic queue already dropped those messages.

## Why prefer one over the other

| Prefer **event streaming** when… | Prefer **classic queue** when… |
|----------------------------------|--------------------------------|
| Multiple teams need the same history | Simple job handoff, delete-after-done |
| Replay / reprocessing matters | Short-lived tasks (resize image) |
| Ordered per key (user, order) | Order across all messages doesn’t matter |
| High throughput append log | Smaller scale ops simplicity wins |

**Not “Kafka for everything.”** Operating partitions, retention, and consumer lag is real cost. For “send 1 email,” SQS/Rabbit is enough.

**Compaction / retention:** time-based (e.g. 7 days) or size-based; compacted topics keep latest value per key (handy for changelogs).

### Real systems (interview name-drops)

- **Kafka, Pulsar, Kinesis, Redpanda** — durable logs.
- **Interview phrase:** “partition by entity id for ordering; consumer groups for fan-out.”

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Durable log + retention | Replay, audit, many independent consumers | Storage cost; more ops complexity |
| Partition by key | Per-key ordering + parallel scale | Hot keys can skew one partition |
| Many consumer groups | True fan-out without extra publishes | Lag monitoring per group |
| Classic queue only | Simple mental model | No easy historical replay |

**Common interview trap:** Promising global ordering across all events — in Kafka, order is **per partition**.

## Interview trigger phrase

> “I’d use a **Kafka-style log** partitioned by `orderId` so we keep order per order, let billing and search consume independently, and **replay** if a consumer bugs out.”

## Exercise

**Design “activity feed ingestion” for a social app.**

1. What do you partition by (user, post, shard) — and what ordering do you guarantee?  
2. Search indexer falls 2 hours behind — how do you describe that in streaming terms (lag / offset)?  
3. After a bad deploy corrupted derived data, how does retention + replay save you vs a pure queue?
