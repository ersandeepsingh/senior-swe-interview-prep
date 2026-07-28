# Wide-Column (Cassandra, HBase)

> Tables with a **partition key** (where data lives) and **clustering keys** (how rows sort inside the partition) — optimized for **writes** and known query paths.

## Plain English

Cassandra looks a bit like SQL tables but you **cannot** think in arbitrary JOINs. You design tables **per query**. Partition key placement and avoiding hot/unbounded partitions are the interview core.

## Essentials (must-know for this topic)

### Primary key anatomy

```text
PRIMARY KEY ((partition_key), clustering_1, clustering_2)
```

| Piece | Role |
|-------|------|
| **Partition key** | Hashes to a node — **where** data lives |
| **Clustering columns** | Sort order **inside** the partition |
| **((a, b), c)** | Composite partition key `(a,b)` |

### Query rules (must know)

| Allowed mindset | Forbidden mindset |
|-----------------|-------------------|
| Query by partition key (+ clustering range) | Ad-hoc `WHERE` on non-key columns |
| One table per access pattern | One table for all queries + secondary indexes everywhere |
| Denormalize into multiple tables | JOINs like Postgres |

### Partition health

| Healthy | Unhealthy |
|---------|-----------|
| Even key distribution | Hot partition (`celebrity` user, single global key) |
| Bounded size (time buckets) | Unbounded growth in one partition |
| `LIMIT` on newest clustering | `SELECT *` huge partitions |

**Bucketing:** `PRIMARY KEY ((room_id, day), sent_at, msg_id)` keeps chat rooms from one giant partition.

### Consistency (quick)

| Idea | Meaning |
|------|---------|
| **Tunable consistency** | `ONE` / `QUORUM` / `ALL` for read/write |
| **Eventual** default vibe | Prefer availability + write speed |
| Secondary indexes | Limited — prefer denormalized tables |

## Why seniors get asked

High-write, multi-region systems (timelines, IoT, messaging metadata) often cite Cassandra. Seniors must show partition-key design skill.

## Simple example

```cql
CREATE TABLE user_timeline (
  user_id UUID,
  created_at TIMEUUID,
  activity_id UUID,
  body TEXT,
  PRIMARY KEY ((user_id), created_at, activity_id)
) WITH CLUSTERING ORDER BY (created_at DESC);

-- Good: query by partition key
SELECT * FROM user_timeline WHERE user_id = ? LIMIT 50;

-- Bad: SELECT * WHERE body CONTAINS 'hello';  -- not the access pattern
```

## When to use / when not / trade-offs

| Use wide-column when… | Prefer SQL when… |
|-----------------------|------------------|
| Huge write throughput | Ad-hoc queries / joins |
| Time-ordered per entity feeds | Multi-row ACID common |
| Multi-DC availability | Small data, strong consistency default |

**Trade-offs:** linear scale writes + availability vs denormalization discipline and eventual consistency (tunable).

## Common pitfalls

- Hot partitions (`user_id = celebrity` or single partition key)
- Unbounded partition growth (no clustering/time bucketing)
- Designing one table for all queries
- Treating CQL like full SQL

## Interview trigger phrase

> “In Cassandra I’d model one table per query, choose partition keys for even load, and cluster by time — not run ad-hoc SQL.”

## Exercise

Store “messages in a chat room, latest 50.” Propose primary key and one reason you’d bucket by day/month. What goes wrong with `PRIMARY KEY (room_id)` only?
