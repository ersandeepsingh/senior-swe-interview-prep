# Design a News Feed / Ranking 🔴

> **Crux:** Candidate generation + ML (or heuristic) ranking under tight latency — with heavy caching and graceful degradation when the ranker is slow/down.

## Clarify (say this first)

**Functional**
- Personalized home feed: not pure chrono — rank by relevance/engagement
- Mix friends’ posts, groups/pages, ads/recommendations (scope ads if asked)
- Infinite scroll with cursors; mark seen / not-interested signals
- Near-real-time: new posts appear within seconds–minutes after rank refresh

**Non-functional**
- p99 feed < 200–300 ms at edge of ranking service
- Availability: never blank feed if ML is down (fallback chrono/cached)
- Eventual consistency OK; read-your-writes for own posts preferred
- Feature freshness vs latency trade-off

## Back-of-envelope

```text
Assumptions: 100M DAU, 30 feed opens/day → ~35K feed req/s avg (peak 3–5×)
Candidates per request: ~500–2000 → rank top 50
Features: user + post + edge; feature store QPS ≈ feed QPS × candidates (must prune early)
Cache: ranked feed per user TTL 30–120s cuts origin ranking heavily
Model: two-stage retrieval → light ranker → heavy ranker on top-K
```

## API + data model

```text
GET  /api/v1/feed/home     ?cursor&limit
POST /api/v1/feed/seen     { post_ids[] }
POST /api/v1/feed/feedback { post_id, action }
```

| Entity / store | Role |
|----------------|------|
| Candidate sources | Friend inbox, pages, recommended pool |
| `features` | User/post/edge features (online + offline store) |
| `ranked_feed_cache` | `user_id` → ordered `post_id[]` + scores + TTL |
| Impression log | Training / diversity / dedup |

## High-level architecture

```text
Client → Feed API
           │
           ├─► Cache hit? return ranked list (hydrate post meta)
           │
           └─► Candidate gen (fan-in sources)
                    │
                    ▼
              Ranker (L1 cheap → L2 ML)
                    │
                    ▼
              Diversity / filters → cache → client
                    │
         Feature store + model serving
```

## Deep dive: the crux

**Pipeline:** retrieval (many) → ranking (score) → re-ranking (diversity, freshness, business rules).

| Piece | Alternatives | Pick when |
|-------|--------------|-----------|
| Candidates | Fan-out inbox only vs multi-source retrieval | Social-only vs FB/IG-style |
| Ranking | Heuristic (likes×decay) vs ML model | Warm-up vs senior bar |
| Caching | Cache final ranked IDs vs cache features | Ranked IDs = simplest win |
| Invalidation | TTL + soft refresh vs write-through on new post | TTL default; bump on publish for active users |

**Latency budget:** precompute features offline; online features only for hot signals. Retrieve ≤ O(hundreds), not all friends’ history. **Never block the feed on model RPC timeout** — serve cached or chronological fallback.

**Caching strategy:** cache `user_id → [post_ids]` for 1–2 min; async refresh. Hydrate post bodies from post service/cache. Dedup seen posts via bloom/bitsets.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Heavy ML ranker | Relevance / engagement | Latency, cost, failure surface |
| Long cache TTL | Cheap, stable p99 | Stale / less “live” feed |
| Multi-source candidates | Rich feed | Complexity, spam, calibration |
| Chrono fallback | Availability | Worse engagement metrics |

## Failure modes & scale

- **Ranker timeout:** circuit breaker → cached feed → chrono merge of inbox
- **Feature store lag:** degrade features; don’t fail request
- **Hot key user:** local cache + sticky routing optional
- **Filter bubbles / spam:** diversity constraints + integrity signals in re-rank
- **Shard** candidate/timeline by user; scale model replicas horizontally

## Interview trigger phrase

> “I’d treat feed as retrieve → rank → re-rank, cache the ranked post-ID list per user with a short TTL, and always have a chronological fallback when the ranker or feature store is unhealthy.”

## Exercise

1. Budget **100 ms** for ranking — what do you precompute vs compute online?
2. How do you ensure a user **sees their own new post** immediately despite a cached ranked feed?
3. What metrics would you watch to know ranking is wrong vs infrastructure is slow?
