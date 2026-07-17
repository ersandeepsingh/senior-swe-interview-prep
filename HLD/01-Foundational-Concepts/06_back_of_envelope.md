# Back-of-Envelope Estimation

> Rough numbers justify architecture. “1B users” without QPS/storage is storytelling; **X writes/s and Y TB** is how you earn sharding and caching.

## Plain English

In the first 5 minutes of an HLD round, estimate:

1. **Traffic** — QPS (reads/writes), peak vs average  
2. **Storage** — bytes/day → multi-year retention  
3. **Bandwidth** — ingress/egress (especially media)  
4. **Memory** (optional) — working set for cache  

You don’t need exact math — **orders of magnitude** (10³, 10⁶) that drive decisions.

```text
  Requirements → Estimates → Architecture choices
       │              │              │
   "Twitter"     10k write QPS    shard tweets
                 100k read QPS    cache timelines
                 50 TB/year       object store for media
```

## Handy constants (memorize)

| Thing | Rough value |
|-------|-------------|
| Seconds / day | ≈ 10⁵ (86,400) |
| Seconds / month | ≈ 2.5 × 10⁶ |
| Days / year | ≈ 365 ≈ 4 × 10² |
| 1 KB | 10³ bytes |
| 1 MB | 10⁶ |
| 1 GB | 10⁹ |
| 1 TB | 10¹² |
| Peak ≈ | 2–3× daily average (or more for events) |

## Worked example: “1B users, 2 posts/day”

**Writes**

```text
  Posts/day = 1e9 × 2 = 2e9
  Writes/s  ≈ 2e9 / 1e5 = 20,000 posts/s average
  Peak      ≈ 2–3× → ~40k–60k writes/s
```

**Storage** (assume 300 bytes metadata per post, ignore media first)

```text
  Per day  ≈ 2e9 × 300 ≈ 6e11 bytes ≈ 600 GB/day
  Per year ≈ 600 GB × 365 ≈ 220 TB/year (metadata only)
```

**Reads** (assume each user opens feed 5×/day, feed touch = 1 read of timeline)

```text
  Read QPS ≈ (1e9 × 5) / 1e5 = 50,000 QPS average
```

**What this buys you in the interview**

| Number | Decision it justifies |
|--------|------------------------|
| ~20k write QPS | Single Postgres primary may struggle → shard / specialized write path |
| ~50k+ read QPS | Cache + CDN + read replicas |
| Hundreds of TB/year | Object storage for media; cold tiering; not “one disk” |

## Diagram: estimation flow

```text
         ┌──────────────┐
         │ DAU / actions│
         └──────┬───────┘
                ▼
         ┌──────────────┐
         │ ÷ seconds/day│──► avg QPS ──► × peak factor
         └──────┬───────┘
                ▼
         ┌──────────────┐
         │ × size/item  │──► storage / day ──► × retention
         └──────┬───────┘
                ▼
         ┌──────────────┐
         │ media bytes  │──► bandwidth & CDN cost
         └──────────────┘
```

## Why this is preferred over skipping estimates

| Skip estimates | Do back-of-envelope |
|----------------|---------------------|
| “We’ll add Redis and Kafka” (cargo cult) | “Read QPS is 50k → Redis is justified” |
| Over-design a toy scale problem | Keep a college-project design when numbers are small |
| Can’t defend shard count | “Each shard ~2k QPS → ~10 shards + headroom” |

**Prefer rough + stated assumptions** over fake precision (“exactly 18,472 QPS”).

## Trade-offs / pitfalls

| Pitfall | Better habit |
|---------|----------------|
| Using registered users instead of DAU | Ask: daily active? |
| Ignoring peak (Super Bowl / New Year) | State peak multiplier |
| Forgetting fan-out (1 write → N reads/inbox writes) | Estimate *amplified* writes for feeds |
| Media treated like text | Separate blob size and egress |

## Interview trigger phrase

> “Assuming 1B users, 2 posts/day → ~20k write QPS average, ~50k+ read QPS — that already pushes us past a single primary DB, so I’ll plan for sharding and a cache tier.”

## Exercise

**Estimate for a chat app: 50M DAU, each sends 40 messages/day, average message 200 bytes. Media: 5% of messages are 200 KB images.**

1. Average message write QPS (text only).  
2. Storage/day for text + images.  
3. One architecture choice each number forces (DB type, object store, CDN, etc.).  
State your assumptions out loud as you would in an interview.
