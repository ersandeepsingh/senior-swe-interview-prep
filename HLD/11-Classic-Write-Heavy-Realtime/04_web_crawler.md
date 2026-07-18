# Design a Web Crawler 🔴

> **Crux:** Distribute fetch work fairly (frontier), **dedup** URLs at massive scale, and obey **politeness** (per-host rate limits) without starving the crawl.

## Clarify (say this first)

**Functional**
- Start from seed URLs; fetch HTML; extract links; enqueue new URLs
- Respect `robots.txt`; cap depth / domain allowlist
- Store raw pages + extracted metadata; continuous vs one-shot crawl
- Recrawl policy by change frequency (optional)

**Non-functional**
- Extremely high URL cardinality; writes to frontier dominate
- Politeness: max N concurrent requests per host
- Throughput: thousands of pages/s across workers
- Exactly-once fetch not required — avoid repeat waste

## Back-of-envelope

```text
Assumptions: 10B URL frontier; 1K pages/s sustained
Page ~100 KB → 100 MB/s raw ≈ 8 TB/day
Dedup set: 10B URLs × 16 B hash ≈ 160 GB (or bloom ≪)
DNS + robots cache critical or they become bottlenecks
Workers: hundreds; need work stealing without dogpiling one host
```

## API + data model

```text
Admin: POST /seeds  { urls[] }
       GET  /stats  { fetched, queued, errors }
Internal: frontier claim / complete RPCs
```

| Component | Data |
|-----------|------|
| Frontier | Priority queue of URLs (by score / domain) |
| Seen / dedup | Bloom + durable URL key store |
| Document store | `url`, `fetch_ts`, `content_ref`, `status` |
| Host state | `host → next_fetch_at`, robots rules |

## High-level architecture

```text
Seeds → Frontier (sharded queues)
            │
            ▼
      Scheduler (politeness)
            │
            ▼
      Fetcher workers ──► DNS / robots cache
            │
            ├─► content → object store
            ├─► parse links → dedup → frontier
            └─► metadata DB
```

## Deep dive: the crux

**Work distribution**
- Shard frontier by **host hash** so one host’s politeness state lives with its queue
- Alternative: global priority queue + per-host locks (harder at scale)
- Workers pull from local shard; dynamic rebalance if skew

**Dedup**
- Canonicalize URL (scheme, host, trailing slash, query normalize)
- Bloom filter (false positives skip — OK if rare miss) + exact KV for “seen”
- Content fingerprint optional to skip unchanged recrawls

**Politeness**
- Per-host token bucket / next-available timestamp
- Shared robots.txt cache with TTL
- Never stampede a small host from 1K workers

| Priority scoring | Purpose |
|------------------|---------|
| Seed / PageRank-like | Important pages first |
| Freshness | Recrawl stale |
| Political / allowlist | Stay in scope |

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Shard by host | Natural politeness | Uneven shard load (huge sites) |
| Bloom-only dedup | Memory | Rare duplicate fetches |
| Exact URL store | No duplicates | Cost / latency |
| Aggressive crawl rate | Coverage speed | Ban risk / legal |

## Failure modes & scale

- **Frontier explosion:** priority caps, domain budgets, drop low-score URLs
- **Giant host (wikipedia):** split by path prefix; multiple politeness keys
- **Fetcher crash mid-write:** lease URLs with timeout; retry → at-least-once
- **Parser poison / infinite spaces:** max depth, same-host caps, nofollow
- **DNS storms:** cache resolvers; bulk lookup

## Interview trigger phrase

> “I’d shard the frontier by host so politeness is local, use URL canonicalization plus a bloom+KV seen-set for dedup, and have fetchers lease work with timeouts — throughput comes from parallelism, correctness from per-host rate limits.”

## Exercise

1. How do you prevent **crawler traps** (calendar links, infinite query params)?
2. Design **recrawl** so changed pages are refreshed without refetching the whole web weekly.
3. What breaks if you shard the frontier by **URL hash** instead of host?
