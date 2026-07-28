# Redis Beyond Cache

> Redis is often a **multi-tool**: pub/sub, rate limiting, distributed locks, leaderboards, and streams — not only `GET`/`SET`. Seniors name the **primitive** and its **failure mode**.

## Plain English

| Use | Redis feature | Idea |
|-----|---------------|------|
| **Pub/Sub** | `PUBLISH` / `SUBSCRIBE` | Fire-and-forget fan-out (no persistence) |
| **Rate limiting** | Counters + TTL, or sorted sets | Token/leaky/sliding window at the edge of the API |
| **Distributed lock** | `SET key nx px` (+ Redlock debate) | Mutual exclusion across instances |
| **Leaderboards** | Sorted sets (`ZADD` / `ZREVRANGE`) | Rank by score |
| **Streams** | `XADD` / consumer groups | Lightweight append log / work queue |
| **Sessions / carts** | Hashes + TTL | Ephemeral user state |

```text
  Cache is one hat. Same process also:
    INCR ratelimit:ip:1.2.3.4  + EXPIRE 60
    ZADD leaderboard 9001 "alice"
    SET lock:job:42 nx px 30000
    XADD events * type signup user 7
```

## Essentials (must-know for this topic)

### Redis primitives beyond GET/SET

| Use case | Structure / command | Must remember |
|----------|---------------------|---------------|
| **Rate limit** | `INCR` + TTL, or zset sliding window | Always set expiry or keys leak |
| **Distributed lock** | `SET key NX PX` (+ token) | Expiry required; delete only your token (Lua) |
| **Leaderboard** | Sorted set `ZADD` / `ZREVRANGE` | Memory-bound; not a warehouse |
| **Pub/Sub** | `PUBLISH` / `SUBSCRIBE` | **No persistence** — offline = miss |
| **Streams** | `XADD` + consumer groups | Light log/queue; not full Kafka |
| **Session / cart** | Hash + TTL | Ephemeral; lose node → lose state unless replicated |

### When Redis is wrong

| Need | Prefer instead |
|------|----------------|
| Durable multi-team event bus | Kafka / SQS |
| Hard distributed lock correctness across DCs | Consensus store / careful design (Redlock debate) |
| Huge retained history + replay | Kafka / object storage |

**Interview line:** Redis = low-latency coordination; durable cross-service truth still lives in DB/queue/log.

## Simple example

**API rate limit (fixed window):**

```text
  key = ratelimit:{userId}:{minuteBucket}
  count = INCR key
  if count == 1: EXPIRE key 60
  if count > 100: reject 429
```

**Leaderboard:**

```text
  ZADD game:scores 4500 "u1"
  ZREVRANGE game:scores 0 9 WITHSCORES   → top 10
```

**Lock (simplified):**

```text
  SET lock:resource nx px 10000  → "OK" means you hold it
  do work
  DEL lock:resource   (better: Lua check token before delete)
```

## When to use / trade-offs

| Prefer **Redis primitive** when… | Prefer **specialized system** when… |
|----------------------------------|-------------------------------------|
| Soft real-time, app already has Redis | Hard durability / multi-region queue (Kafka, SQS) |
| Simple locks, counters, rankings | Complex workflows, huge retention, strict audit |
| Best-effort pub/sub inside DC | Guaranteed delivery to many teams |

| Primitive | You gain | You give up |
|-----------|----------|-------------|
| Pub/Sub | Simple fan-out | No replay; offline subscribers miss events |
| Streams | Replay, consumer groups | Not full Kafka; ops still on you |
| SET NX lock | Easy mutex | Clock/GC issues; Redlock controversy for correctness |
| Sorted sets | Fast top-K | Memory; not a full analytics warehouse |

## Pitfalls

- Using pub/sub for **critical** billing events (use a durable queue/log).  
- Locks without **expiry** → deadlock forever; without **token** → deleting someone else’s lock.  
- Rate-limit keys without TTL → Redis fills up.  
- Treating Redis Streams as a drop-in Kafka for multi-team event bus at scale.  
- Blocking Redis with heavy Lua / `KEYS *` in production.

## Interview trigger phrase

> “Redis isn’t only a cache — I’d use it for **counters, locks, leaderboards, and light streams**, but for durable cross-service events I’d reach for **Kafka or SQS** and keep Redis for low-latency coordination.”

## Exercise

**Sketch Redis usage for a multiplayer game API.**

1. Top-100 scores, per-user request throttle, and “only one matchmaking worker assigns a room” — which structures?  
2. Why is pub/sub a bad fit for “player purchased skin” that must update inventory?  
3. Your lock TTL is 10s and work sometimes takes 30s — what fails, and how do you fix it?
