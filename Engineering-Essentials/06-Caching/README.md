# 6. Caching ⭐

Speed and origin protection by serving hot data from memory or the edge. Interviewers expect you to **name the store, read/write strategy, eviction, and invalidation** — and how you’ll survive a **hot key** stampede.

| # | Topic | One-line intent |
|---|-------|-----------------|
| 01 | [Redis / Memcached](01_redis_memcached.md) | In-memory stores, data structures, when each fits |
| 02 | [Caching strategies](02_caching_strategies.md) | Cache-aside, read/write-through, write-back |
| 03 | [Eviction & TTL](03_eviction_ttl.md) | LRU/LFU, expiry, memory bounds |
| 04 | [Cache invalidation](04_cache_invalidation.md) | Staleness vs freshness — the hard problem |
| 05 | [Distributed caching](05_distributed_caching.md) | Consistent hashing, hot keys, stampede |
| 06 | [CDN caching](06_cdn_caching.md) | Edge caching for static/media, cache headers |
| 07 | [Redis beyond cache](07_redis_beyond_cache.md) | Pub/sub, rate limits, locks, leaderboards, streams |

**How to use:** For each file — read Plain English → example → trade-offs → say the interview trigger phrase out loud → do the Exercise without peeking.
