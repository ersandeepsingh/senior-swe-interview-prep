# Design a Social Graph (Follow / Friend) 🔴

> **Crux:** Model follow/friend edges for fast adjacency queries, then shard a skewed graph so celebrities don’t create hot partitions.

## Clarify (say this first)

**Functional**
- Follow / unfollow (directed); or friend request + accept (undirected)
- List followers, following; check “does A follow B?”; mutual friends optional
- Counts (follower/following); privacy (private accounts) if asked
- Feed fan-out and recommendations consume this graph

**Non-functional**
- Extremely skewed degree distribution (power law)
- Low-latency point lookups and “list first page of followers”
- High write rate on follow/unfollow bursts (viral users)
- Eventual consistency on counts OK; edge existence should be reliable

## Back-of-envelope

```text
Assumptions: 500M users, avg 200 following → ~100B edges
Edge ~50 B → ~5 TB raw edges (plus indexes/replication)
Follow QPS: peaks around celebs / events — tens of K writes/s
Read: “home feed fan-out” and “follower list” dominate
Celebrity: 100M followers → cannot store/serve from one node naively
```

## API + data model

```text
POST   /api/v1/users/:id/follow
DELETE /api/v1/users/:id/follow
GET    /api/v1/users/:id/followers ?cursor
GET    /api/v1/users/:id/following ?cursor
GET    /api/v1/users/:a/follows/:b  → boolean
```

| Model | Storage idea |
|-------|----------------|
| Directed edge | `(follower_id, followee_id, ts)` + reverse index |
| Counts | `user_id → {followers, following}` (cached / approx OK) |
| Friend (undirected) | Canonical `min(a,b), max(a,b)` + state `pending/accepted` |

## High-level architecture

```text
Client → Graph API → Graph service
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
   Edge store      Reverse index   Count cache
   (shard by       (followers of   (Redis)
    followee or     X)
    follower)
          │
   Feed / fan-out / recommend consume edges
```

## Deep dive: the crux

**Modeling**
- **Follow:** two adjacency lists — outbound (following) and inbound (followers), or one edge table + secondary index.
- **Friend:** state machine + undirected edge; authorize both sides.

**Sharding alternatives**

| Shard key | Good for | Pain |
|-----------|----------|------|
| By `follower_id` | “Who do I follow?” / fan-out-on-write source | Hot celebs’ follower lists scattered — hard to list followers |
| By `followee_id` | “Who follows X?” | Hot celeb shard; following-list queries scatter |
| Dual-write both directions | Both query patterns fast | 2× writes; sync issues |
| Celebrity special case | Isolate mega-nodes | Extra code path |

**Senior approach:** dual indexes (or dual tables); **hash shard** normal users; **dedicated celebrity graph partitions** or leave celebrity followers in a separate store optimized for append + cursor scan. Cache follower counts; don’t `COUNT(*)` live.

**Check edge:** bloom filter / cache + KV `follower:followee` key for O(1) exists.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Dual adjacency | Fast both directions | Write amp + consistency |
| Graph DB (Neo4j-style) | Traversals (mutual, FoF) | Ops/scale vs KV at pure follow |
| Exact counts | Accuracy | Hot-row updates |
| Approx counts (Redis) | Speed | Drift; reconcile async |

## Failure modes & scale

- **Hot partition (celeb):** isolate node; cache top pages of followers; rate-limit scrapers
- **Dual-write failure:** reconcile job from source-of-truth edge log
- **Unfollow storms:** async propagate to feed inboxes
- **Privacy:** private account — follow = request; authorize list endpoints
- **FoF / mutual:** precompute or sampled online — don’t DFS entire graph in request path

## Interview trigger phrase

> “I’d store directed edges with dual adjacency indexes, shard by user for normal traffic, and special-case celebrities so one inbound list doesn’t hot-spot a single shard — counts live in cache, not as live COUNT queries.”

## Exercise

1. Compare **SQL edge table**, **wide-column**, and **graph DB** for follow-only vs “people you may know.”
2. How do you page **100M followers** without deep `OFFSET`?
3. Design a consistent **unfollow** that also stops feed fan-out within seconds.
