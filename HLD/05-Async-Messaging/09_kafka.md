# Kafka Deep Dive

> **Kafka** is a distributed **append-only event log**, not a traditional “delete after ack” queue. Producers write to **topics** (split into **partitions**); **consumer groups** read at their own **offsets**. Built for high throughput, replay, and many independent consumers.

## Plain English

| Term | Meaning |
|------|---------|
| **Broker** | A Kafka server node |
| **Cluster** | Several brokers + controller (KRaft or ZooKeeper legacy) |
| **Topic** | Named stream of events (`orders`, `pageviews`) |
| **Partition** | Ordered shard of a topic — **ordering is per partition** |
| **Offset** | Position in a partition (`0, 1, 2, …`) |
| **Producer** | Appends records (optional key) |
| **Consumer group** | Team of consumers sharing partitions; each partition → one consumer in the group |
| **Retention** | Keep data for time/size even after read (hours → days → forever) |
| **Consumer lag** | How far behind “log end” a group is |

```text
  Producers                    Topic: orders
  (key=orderId)                ┌─ partition 0: [o1][o4][o7]...
       │                       ├─ partition 1: [o2][o5]...
       └── hash(key) % N ─────►└─ partition 2: [o3][o6]...
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
              Group "billing"   Group "search"    Group "warehouse"
              offsets own        offsets own       can replay old data
```

**Mental model:** A commit log (like a distributed `tail -f` with rewind). Queues hand out tasks; Kafka **stores history** for anyone who wants to catch up.

---

## Core guarantees (memorize)

1. **Order within a partition** — not global across the topic  
2. **Same key → same partition** (if you set a key) → per-entity ordering  
3. **At-least-once** by default; exactly-once needs idempotent producer + transactions (careful design)  
4. **Fan-out cheap** — N consumer groups each read the same data independently  
5. **Replay** — reset offsets and reprocess after a bug fix  

---

## Simple example — e-commerce events

```text
  Checkout service ──produce──► topic orders.events
       key = order_id
       value = { "type": "OrderCreated", "order_id": "...", "items": [...] }

  Partition count = 12
  order_id "ord_9f2a" always lands on the same partition → status updates stay ordered
```

### Producer (conceptual)

```python
producer.send(
    topic="orders.events",
    key=order_id.encode(),
    value=json.dumps({
        "type": "OrderCreated",
        "order_id": order_id,
        "user_id": user_id,
        "total": 49900,
    }).encode(),
    headers=[("ce-type", b"OrderCreated")],
)
# linger.ms + batch.size → higher throughput
# acks=all + idempotence → safer writes
```

### Consumer group (conceptual)

```python
# group_id="billing-service"
consumer.subscribe(["orders.events"])
for record in consumer:
    event = json.loads(record.value)
    if event["type"] == "OrderCreated":
        create_invoice(event["order_id"])  # idempotent upsert
    # commit offset after success (auto or manual)
    consumer.commit()
```

Search indexer can be **another** `group_id="search-indexer"` on the same topic — no second publish.

---

## Partitions & scaling

```text
  Throughput ≈ partitions (parallelism) × per-partition rate

  Consumers in one group:
    - Ideal: consumers ≤ partitions
    - Extra consumers sit idle
    - Too few consumers → lag grows
```

| Choice | Effect |
|--------|--------|
| Partition by `userId` | Ordered timeline per user; watch hot celebrities |
| Partition by `orderId` | Ordered lifecycle per order |
| Partition by `null` (round-robin) | Max spread; **no** per-entity order |
| Too few partitions | Can’t scale consumers later easily (adding partitions doesn’t rebalance old keys) |

**Hot key problem:** one viral `userId` hammers one partition → skewed lag. Mitigate with sub-sharding keys or separate paths for celebrities.

---

## Consumer groups vs Rabbit competing consumers

| | Kafka consumer group | Rabbit work queue |
|--|----------------------|-------------------|
| Message after read | Still on log (until retention) | Typically removed after ack |
| Second team needs same events | New group, same topic | Extra publish or fanout exchange |
| Replay | Reset offsets | Usually gone |
| Ordering | Per partition | Per queue (weaker model) |

---

## Delivery & exactly-once (practical)

```text
  Default path: at-least-once
    produce → crash → retry → duplicate event possible
    consume → process → crash before commit → reprocess

  Mitigations:
    1) Idempotent consumer (UPSERT / idempotency key)
    2) Idempotent producer (broker dedupes retries for same PID/seq)
    3) Transactions (consume-process-produce atomically) — EOS pipelines
```

**Interview honesty:**  
> “Exactly-once *effect* comes from idempotent business logic; Kafka EOS helps pipeline handoffs, not magic for every side effect (e.g. sending email twice).”

---

## Retention, compaction, replay

| Mode | Behavior | Use |
|------|----------|-----|
| **Time retention** (e.g. 7d) | Drop older than 7 days | Clickstream, logs |
| **Size retention** | Cap disk per partition | Cost control |
| **Log compaction** | Keep **latest value per key** | Changelog / KTable / config |

```text
  Compacted topic user.profile
    key=user42  value={name:Ada}     (older versions garbage-collected)
    Downstream always can rebuild state from compacted log
```

**Replay example:** Billing bug undercharged for 2 hours → fix code → reset group offsets to timestamp → reprocess → idempotent invoices correct totals.

---

## Ecosystem pieces (name-drop correctly)

| Piece | Role |
|-------|------|
| **Kafka Connect** | Source/sink connectors (DB CDC → Kafka → ES/S3) |
| **Kafka Streams / Flink / Spark** | Stream processing |
| **Schema Registry** | Avro/Protobuf contracts; evolve safely |
| **MirrorMaker 2** | Cross-cluster replication |
| **KRaft** | Consensus without ZooKeeper (modern) |

---

## Worked example — activity feed + search + fraud

```text
  API ──► topic: user.activity   (key=user_id)
              │
              ├─ group feed-writer   → Cassandra timelines
              ├─ group search-index  → Elasticsearch
              └─ group fraud-score   → feature store / alerts

  retention = 3 days
  partitions = 64
  feed-writer lag alert if > 30s
  fraud can be slower (lag OK) but must not reset carelessly
```

**Failure drill:** Bad search mapping deploy → fix mapping → reset **only** `search-index` offsets → rebuild index from retained log. Billing group untouched.

---

## Ops & failure modes seniors mention

| Issue | What you do |
|-------|-------------|
| Consumer lag climbing | Scale consumers (≤ partitions), speed handler, fix slow dependency |
| Rebalance storms | Cooperative rebalancing; avoid long processing without pause/commit strategy |
| Disk full | Retention, tiered storage, more brokers |
| Poison message | Dead-letter topic + skip/seek; don’t block partition forever |
| Schema break | Compatibility checks in CI via Schema Registry |

---

## Why Kafka vs RabbitMQ / SQS

| Prefer **Kafka** when… | Prefer **Rabbit/SQS** when… |
|------------------------|-----------------------------|
| Multiple consumers need the same history | Simple task handoff (send email, resize image) |
| Replay / audit / stream processing | Complex per-message routing topology |
| High throughput event bus | Low ops / fully managed small workloads |
| Per-key ordering at scale | RPC-ish or short-lived jobs |

**Not Kafka for everything:** operating partitions, lag, and schemas is real cost. A single SQS queue may be the senior choice for one worker pool.

---

## Trade-offs

| Decision | Gain | Cost |
|----------|------|------|
| Many partitions | Parallelism | More files, longer recovery, rebalances |
| Long retention | Replay power | Storage $$$ |
| `acks=all` | Durability | Higher produce latency |
| Manual offset commit | Control | Easy to bug (lost or dup work) |
| Compacted topics | Rebuildable state | Not a full history of every change |

---

## Config cheat-sheet (interview talking points)

```text
  Producer: acks=all, enable.idempotence=true, linger.ms for batching
  Consumer: enable.auto.commit=false (often), commit after side effects
  Topic:   replication.factor >= 3 in prod, min.insync.replicas=2
  Key:     always set when order matters
```

---

## Interview trigger phrase

> “I’d put domain events on **Kafka** partitioned by `orderId` — billing and search as separate consumer groups, retention for replay, idempotent handlers for at-least-once, and lag alerts per group.”

## Exercise

1. You need global “exactly once email.” Why is Kafka alone not enough, and what do you add?  
2. Topic has 6 partitions and 10 consumers in one group — what happens?  
3. After fixing a bug, how do you reprocess only yesterday’s `orders.events` without touching other groups?
