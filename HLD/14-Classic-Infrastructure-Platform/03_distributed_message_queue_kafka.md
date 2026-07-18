# Design a Distributed Message Queue (Kafka-style) 🔴

> **Crux:** A **durable, partitioned, ordered append log** plus clear **delivery semantics** (at-least-once + idempotent consumers) — not a transient in-memory queue.

## Clarify (say this first)

**Functional**
- Topics; produce / consume; consumer groups
- Order within partition (not global)
- Retention by time/size; replay from offset
- Delivery: at-least-once default; exactly-once optional

**Non-functional**
- High throughput (MB–GB/s); durable to disk
- Survive broker loss (RF≥2 or 3)
- Lag visibility; backpressure via consumer pace
- Multi-AZ; controlled rebalance

## Back-of-envelope

```text
100k msg/s × 1 KB ≈ 100 MB/s ingest
RF=3 → ~300 MB/s disk write cluster-wide
Retention 7d → 100 MB/s × 86400 × 7 ≈ 60 TB raw (÷compress)
Partitions: enough so max(producer, consumer parallelism) scales
  e.g. 100 partitions → ~1k msg/s/partition average
```

## API + data model

```text
Produce(topic, key?, records[]) → offsets
Fetch(topic, partition, offset, max_bytes)
CommitOffset(group, topic, partition, offset)
```

| Entity | Role |
|--------|------|
| Topic | named stream |
| Partition | ordered log segment(s); 1 leader |
| Offset | monotonic position in partition |
| Consumer group | competing consumers; 1 owner / partition |

## High-level architecture

```text
  Producers ──► Brokers (partition leaders + followers)
                    │
                    │  append to log (page cache + disk)
                    ▼
              [P0][P1][P2]... topic partitions
                    │
                    ▼
              Consumer group
           C1 owns P0,P1 | C2 owns P2
           commit offsets → __consumer_offsets
```

## Deep dive: the crux

**Ordered durable log:** each partition is an append-only sequence. Key → hash → partition → **order preserved for that key**. Replication: leader + followers; acks=`all` / ISR for durability.

**Delivery:**
| Mode | How | When |
|------|-----|------|
| At-most-once | commit before process | Loss OK |
| At-least-once | process then commit | Default; need idempotency |
| Exactly-once | idempotent producer + txn / EOS | Ledger-like; higher cost |

**Consumer groups:** each partition assigned to one member; rebalance on join/leave. **Pick:** partitions for parallelism + key affinity; at-least-once + idempotent handlers unless payment-grade EOS required.

**Offsets:** consumers track position; commit after successful side effects. Compaction keeps latest value per key (changelog topics). Mirror/replication across DCs is async — expect lag, not sync dual-write.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Partitioned log | Scale + per-key order | No global order |
| More partitions | Throughput / parallelism | More files; longer rebalances |
| acks=all | Durability | Produce latency |
| Compacted topic | Latest value per key | Not full history |
| Shared consumer group | Competing consumers | Stop-the-world rebalance risk |

## Failure modes & scale

- **Leader fail:** ISR elects new leader; producers refresh metadata
- **Consumer crash:** uncommitted work redelivered → **idempotent** processing
- **Hot partition:** bad key cardinality — redesign key or split
- **Lag spike:** scale consumers (≤ partition count) or add partitions (careful)
- **Disk full:** retention/compaction; alert before ISR shrinks

## Interview trigger phrase

> “I’d model it as a **partitioned append log**: order and scale per partition, **consumer groups** for parallelism, and **at-least-once with idempotent consumers** unless we truly need transactional exactly-once.”

## Exercise

1. Why can’t one consumer group member process the same partition as another at once?  
2. User-id as key — what ordering guarantee do you have for that user’s events?  
3. After a rebalance, a message is processed twice — where do you put dedup state?
