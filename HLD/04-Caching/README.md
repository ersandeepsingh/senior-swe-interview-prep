# 4. Caching

Speed and origin protection by serving hot data from memory or edge. Interviewers expect you to **name the placement layer, read/write strategy, eviction, and invalidation** — and how you’ll survive a **hot key** stampede.

| # | Concept | One-line intent |
|---|---------|-----------------|
| 01 | [Cache placement](01_cache_placement.md) | Client / CDN / app / distributed / DB layers |
| 02 | [Caching strategies](02_caching_strategies.md) | Cache-aside / read-through / write-through / write-back |
| 03 | [Eviction policies](03_eviction_policies.md) | LRU / LFU / TTL — what leaves when full |
| 04 | [Cache invalidation](04_cache_invalidation.md) | Keep cache and source of truth in sync |
| 05 | [Hot key & thundering herd](05_hot_key_thundering_herd.md) | Stampede control, coalescing, jittered TTLs |

**How to use:** For each file — read Plain English → diagram → trade-offs → say the interview trigger phrase out loud → do the Exercise without peeking at notes.
