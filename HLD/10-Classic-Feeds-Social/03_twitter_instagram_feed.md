# Design Twitter / Instagram Feed 🔴

> **Crux:** Fan-out on write vs fan-out on read — and how you special-case celebrities so one post doesn’t melt the write path.

## Clarify (say this first)

**Functional**
- Post tweet/photo; follow users; home timeline = posts from people I follow
- User timeline (my posts); like/comment optional park
- Near-real-time: seconds OK, not ms-trading
- Media via separate CDN/object store; feed returns URLs + meta

**Non-functional**
- Extremely read-heavy home timeline; write fan-out can explode
- High availability; eventual consistency OK (see post within a few seconds)
- p99 home feed load under a few hundred ms
- Hot users (celebrities) with 10M+ followers

## Back-of-envelope

```text
Assumptions: 200M DAU, 2 posts/user/day → ~5K posts/s avg (peak ~25K)
Home timeline reads: 200M × 20 opens/day ≈ 50K reads/s avg (peak much higher)
Fan-out-on-write: avg 200 followers → 25K posts/s × 200 = 5M timeline writes/s
Celebrity 50M followers → one post = 50M writes — cannot fan-out naively
Storage: timeline entries denormalized; tweet store separate
```

## API + data model

```text
POST /api/v1/posts              { text, media_ids[] }
GET  /api/v1/timeline/home      ?cursor&limit
GET  /api/v1/users/:id/timeline ?cursor&limit
POST /api/v1/users/:id/follow
```

| Entity | Fields |
|--------|--------|
| `post` | `post_id`, `author_id`, `text`, `media`, `created_at` |
| `follow` | `follower_id`, `followee_id`, `created_at` |
| `home_timeline` | `user_id`, `post_id`, `author_id`, `ts` — denormalized feed inbox |
| `user_timeline` | `author_id`, `post_id`, `ts` |

## High-level architecture

```text
Client → API → Post Service ──► Post DB
                    │
                    ▼
              Fan-out workers (queue)
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
  Home timeline cache/DB    Skip / mark celebrity
  (per follower inbox)      (pull on read)
        │
Client ◄── Timeline service merges inbox + celebrity pull + rank
```

## Deep dive: the crux

| Strategy | Write path | Read path | Best for |
|----------|------------|-----------|----------|
| **Fan-out on write** | Push post ID into each follower’s inbox | Read precomputed timeline | Normal users, low follower count |
| **Fan-out on read** | Write post once | Pull N followees’ recent posts, merge | Sparse follows / celebs |
| **Hybrid** | Fan-out to “normal” followers; celebs pulled on read | Merge inbox + live pulls | Production Twitter-style |

**Celebrity problem:** if followers > threshold (e.g. 10K–100K), **do not** fan-out on write. On home timeline read: load user’s inbox + fetch latest posts from celebrity followees + merge by time (then optional rank).

**Ordering:** `post_id` Snowflake ≈ time-ordered; cursor pagination by `(ts, post_id)`. Duplicates possible under hybrid — dedupe by `post_id`.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Fan-out write | Fast home reads | Write amplification; celeb meltdown |
| Fan-out read | Cheap writes | Slow/expensive reads; merge complexity |
| Hybrid | Scales both sides | Two code paths; tuning threshold |
| Denormalized inbox | p99 read latency | Storage + invalidation on unfollow/delete |

## Failure modes & scale

- **Fan-out lag:** queue backlog → users see delay; prioritize online users’ inboxes
- **Unfollow:** lazy filter on read or async remove from inbox
- **Delete post:** tombstone + async purge from inboxes; cache invalidate
- **Shard** timeline by `user_id`; posts by `post_id`/`author_id`
- **Cache** hot home timelines in Redis (list/ZSET); warm on login

## Interview trigger phrase

> “I’d fan-out on write into per-user timeline inboxes for normal accounts, and for celebrities I’d fan-out on read and merge — that hybrid is how you avoid a single celebrity post writing tens of millions of inbox rows.”

## Exercise

1. Where do you set the **celebrity threshold**, and how do you move a user across it safely?
2. How does **unfollow** interact with an already-fanned-out inbox?
3. Design cursor pagination when merging inbox + celebrity pulls without duplicates/skips.
