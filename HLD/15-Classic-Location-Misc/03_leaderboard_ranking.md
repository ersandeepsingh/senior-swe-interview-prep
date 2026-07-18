# Design a Leaderboard / Ranking 🟡

> **Crux:** Maintain **top-K / rank-by-score** under high write QPS — **sorted sets** (Redis ZSET) plus a **sharding** story when one board doesn’t fit.

## Clarify (say this first)

**Functional**
- Update score; get top-K; get rank for user
- Global vs per-game / per-region / per-season boards
- Ties; score only increases vs arbitrary updates
- Historical seasons (archive)

**Non-functional**
- Real-time feel (sub-second visibility)
- High write rate (game events)
- Read skew: top-100 extremely hot
- Durability: lose board vs rebuild from log

## Back-of-envelope

```text
10M players; 1k score updates/s avg; 10k peak
Top-100 reads: 50k QPS (cacheable)
Redis ZSET: 10M members × ~50–100 B ≈ few GB — often 1 shard OK
100M players or many boards → shard by board_id or score range
```

## API + data model

```text
POST /boards/{id}/scores  {user_id, score}   # or delta
GET  /boards/{id}/top?k=100
GET  /boards/{id}/rank/{user_id}
```

| Entity | Fields |
|--------|--------|
| Entry | `board_id`, `user_id`, `score`, `updated_at` |
| Board | `id`, `season`, `shard_key` |

## High-level architecture

```text
  Game servers
       │  score events
       ▼
  Ingest / API ──► Redis ZSET (per board)
       │                 │
       │                 ├─ ZADD / ZINCRBY
       │                 ├─ ZREVRANGE 0 K-1
       │                 └─ ZREVRANK
       ▼
  Optional: Kafka ──► warehouse / rebuild
       │
       ▼
  Cache CDN/edge for top-K snapshot (100–500 ms TTL)
```

## Deep dive: the crux

**Real-time ranking + sharding:**
| Approach | When |
|----------|------|
| **Single Redis ZSET** | One board fits memory; simplest |
| **Shard by board/season** | Many independent boards |
| **Score-range shards** | One huge global board; top-K mostly high shard |
| **Approx / sample** | Mega-scale; exact rank optional |
| **SQL `ORDER BY` only** | Small N; not high QPS |

**Top-K hot path:** cache serialized top-100; invalidate on timer or version bump — exact personal rank still hits ZSET. **Pick:** ZSET per board; shard by `board_id`; async persist for durability; short TTL cache on top-K.

**Celebrity / dense scores:** include `timestamp` in score bits for stable ordering.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Redis ZSET | Fast rank/top-K | Memory cost; persistence care |
| Top-K cache | Protect Redis | Slightly stale podium |
| Exact global rank | Product honesty | Harder at 100M+ |
| Score-range shards | Scale one board | Cross-shard rank math |
| Rebuild from log | Durability | Recovery time |

## Failure modes & scale

- **Redis flush:** rebuild from DB/Kafka; show stale cached top-K meanwhile
- **Hot board:** replica reads for top-K; separate write primary
- **Cheat / spikes:** server-authoritative scores; rate-limit updates
- **Season rollover:** freeze ZSET → archive; new empty board
- **Multi-region:** regional boards or single-region primary for fairness

## Interview trigger phrase

> “I’d keep each board in a **Redis sorted set** for O(log N) updates and top-K, **shard by board**, and **cache the podium** so top-100 reads don’t melt the primary.”

## Exercise

1. Need exact rank for user #5,000,000 — can you answer from top-K cache? Where do you go?  
2. Global board grows past one Redis instance — design score-range sharding for top-100.  
3. Two players tie on score — how do you define a deterministic order?
