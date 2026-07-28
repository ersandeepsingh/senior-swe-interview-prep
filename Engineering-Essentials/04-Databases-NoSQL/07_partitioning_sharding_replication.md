# Partitioning / Sharding & Replication

> **Replication** copies data for HA/reads; **partitioning/sharding** splits data across machines for scale.

## Plain English

Replicas help you survive primary failure and scale reads. Shards split data when one machine can’t hold write QPS or storage. Interviewers listen for: don’t shard early, pick the right key, and know cross-shard pain.

## Essentials (must-know for this topic)

### Replication vs sharding

| | **Replication** | **Sharding / partitioning** |
|--|-----------------|-----------------------------|
| What | Copies of the **same** data | **Subsets** of data per node |
| Buys | HA, read scale | Write/storage scale |
| Pain | Lag / stale reads | Cross-shard joins & txns; resharding |
| When | Almost always before sharding | After vertical scale + cache + replicas aren’t enough |

### Replication vocab

| Term | Meaning |
|------|---------|
| **Primary / replica** | Writes to primary; replicas serve reads (typical) |
| **Sync vs async** | Durability vs lag trade-off |
| **Failover** | Promote replica when primary dies |
| **Read-your-writes** | Read primary (or session sticky) after write |

### Partitioning types

| Style | How | Example |
|-------|-----|---------|
| **Range** | Key ranges per shard | Time months, id 1–1M |
| **Hash** | `hash(key) % N` | Even user distribution |
| **Geo** | By region | Compliance / latency |
| **Directory** | Lookup service maps key→shard | Flexible; extra hop |

**Postgres note:** declarative **partitioning** can be same-instance (manageability); **sharding** usually means separate servers.

### Shard key rules

| Good key | Bad key |
|----------|---------|
| Present in almost every query | Forces scatter-gather always |
| Even distribution | Hot shard (one celebrity / one tenant) |
| Stable | Constant resharding |

## Why seniors get asked

“How does this scale past one DB?” is core system design. Seniors distinguish read replicas from shards and know resharding pain.

## Simple example

```sql
-- Postgres declarative partitioning (same instance)
CREATE TABLE events (
  id bigserial,
  user_id bigint,
  ts timestamptz
) PARTITION BY RANGE (ts);

CREATE TABLE events_2026_07 PARTITION OF events
  FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');
```

App-level shard sketch:

```python
def shard_for(user_id: int) -> str:
    return f"db-{user_id % 4}"
```

## When to use / when not / trade-offs

| Use replicas when… | Use sharding when… |
|--------------------|--------------------|
| Read scale / HA | Single primary can’t hold data or write QPS |
| Reporting off primary | Clear shard key in almost all queries |

**Avoid sharding** until vertical scale + caching + replicas aren’t enough — operational cost is high.

**Trade-offs:** replicas → lag & stale reads; shards → cross-shard joins/transactions hurt; resharding is hard.

## Common pitfalls

- Sharding on the wrong key (hot shard)  
- Assuming replicas are always up to date  
- Cross-shard transactions without a plan  
- Auto-increment IDs that don’t work across shards  

## Interview trigger phrase

> “Replicas buy read scale and HA; sharding buys write/storage scale — I’d pick a shard key that matches queries and delay sharding until necessary.”

## Exercise

A social app’s `posts` table is 20TB. Propose a shard key, one query that stays single-shard, and one that becomes hard. How do replicas help the timeline read path?
