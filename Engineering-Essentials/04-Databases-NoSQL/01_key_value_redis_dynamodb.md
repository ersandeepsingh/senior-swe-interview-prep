# Key-Value (Redis, DynamoDB)

> Store data as **key → value** with blazing simple access patterns: get, put, delete (and a few extras).

## Plain English

You design around keys you will look up: `user:42:session`, `order:43`. KV wins when you know the key and don’t need ad-hoc SQL joins. Redis and DynamoDB are the two interview defaults — very different personalities.

## Essentials (must-know for this topic)

### Redis vs DynamoDB — access patterns

| | **Redis** | **DynamoDB** |
|--|-----------|--------------|
| Latency | Microseconds (memory) | Single-digit ms (managed) |
| Model | Structures: string, hash, list, set, **sorted set**, streams | Table items with **PK** (+ optional **SK**) |
| Persistence | Optional (AOF/RDB); often cache | Durable system of record |
| Scale story | Cluster / shards; memory-bound | Partitions by key; near-infinite with right design |
| Query shape | `GET`/`SET`, `HGET`, `ZRANGE`, … | `GetItem`, `Query` on PK/SK, GSIs |
| Classic uses | Cache, sessions, rate limit, leaderboard, locks | Serverless backends, user→orders, session store at scale |

### DynamoDB key design vocab

| Term | Meaning |
|------|---------|
| **PK (partition key)** | Determines partition — must be in every access |
| **SK (sort key)** | Orders/ranges within partition (`ORDER#43`) |
| **Query** | PK equal + SK condition — efficient |
| **Scan** | Whole table — avoid in hot path |
| **GSI** | Alternate PK/SK for a second access pattern |

### Redis structures cheat sheet

| Structure | Use |
|-----------|-----|
| String | Cache blob, counter (`INCR`) |
| Hash | Object fields (`user:7`) |
| List | Queue / recent N |
| Set | Unique membership |
| Sorted set | Leaderboard / time-ordered |

### Shared footguns

| Footgun | Why |
|---------|-----|
| **Hot key** | One key hammered → partition/node melt |
| Huge values | Latency + memory |
| Redis as only SoR | Need HA + persistence story |
| Dynamo without access-pattern design | Forces scans |

## Why seniors get asked

Caching, sessions, rate limits, shopping carts, and serverless backends all lean KV. Seniors must design keys and know hot-partition risks.

## Simple example

```bash
# Redis
SET session:abc123 '{"user_id":7}' EX 3600
GET session:abc123
ZINCRBY leaderboard 10 "player:7"
```

```text
DynamoDB item:
PK = USER#7
SK = ORDER#43
attrs: status, total_cents
Query: PK=USER#7, SK begins_with ORDER#
```

## When to use / when not / trade-offs

| Use KV when… | Prefer SQL when… |
|--------------|------------------|
| Lookup by primary key / known pattern | Complex joins, ad-hoc analytics |
| Ultra-low latency (Redis) | Strong multi-row ACID is central |
| Massive scale with simple access (Dynamo) | Rich secondary querying without GSIs |

**Trade-offs:** speed and scale vs query flexibility; Redis memory cost; DynamoDB forces upfront access-pattern design.

## Common pitfalls

- Using Redis as the only system of record without persistence/HA story
- Hot keys (one key hit by everyone)
- DynamoDB table design that requires scans
- Huge values that blow latency/memory

## Interview trigger phrase

> “If access is get-by-key at low latency, I’d use Redis or DynamoDB — I’d design keys around queries, not pretend it’s SQL.”

## Exercise

Model “user’s last 20 notifications” in Redis and in DynamoDB (PK/SK). Name one query each model makes awkward.
