# 15. Classic HLD — Location & Misc

Geo, ranking, sandboxed execution, and ML serving — problems that mix **specialized indexes / graphs** with familiar scale patterns (sharding, caches, async pipelines).

| # | Problem | Crux | Diff |
|---|---------|------|------|
| 01 | [Proximity / Nearby (Yelp)](01_proximity_nearby_yelp.md) | Geo-indexing | 🔴 |
| 02 | [Google Maps / Routing](02_google_maps_routing.md) | Graph partitioning + precomputation | 🔴 |
| 03 | [Leaderboard / Ranking](03_leaderboard_ranking.md) | Real-time ranking + sharding | 🟡 |
| 04 | [Online Code Judge](04_online_code_judge.md) | Async execution + isolation | 🟡 |
| 05 | [Recommendation System](05_recommendation_system.md) | Offline compute + low-latency serving | 🔴 |

**How to use:** Clarify → estimate → API/model → boxes → **deep-dive the crux** → failures. Say the trigger phrase out loud; do the Exercise without peeking.

**Building blocks to refresh first:** geospatial indexes, graphs/shortest path, sorted sets / ranking, queues + isolation, feature stores / candidate generation.
