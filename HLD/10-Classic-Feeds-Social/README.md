# 10. Classic HLD — Read-Heavy / Feeds & Social

Read-heavy designs where the interviewer probes **key generation, caching, fan-out, ranking, and graph scale**. Drill these after foundational concepts — they reuse CAP, caching, sharding, and denormalization constantly.

| # | Problem | Crux | Difficulty |
|---|---------|------|------------|
| 01 | [URL Shortener (TinyURL)](01_url_shortener.md) | Key generation + read caching | 🟡 |
| 02 | [Pastebin](02_pastebin.md) | Object storage + expiry | 🟡 |
| 03 | [Twitter/Instagram Feed](03_twitter_instagram_feed.md) | Fan-out strategy + celebrity problem | 🔴 |
| 04 | [News Feed / Ranking](04_news_feed_ranking.md) | Ranking + caching | 🔴 |
| 05 | [Social Graph (follow/friend)](05_social_graph.md) | Graph modeling + sharding | 🔴 |
| 06 | [Search Autocomplete / Typeahead](06_search_autocomplete.md) | Trie + ranking at edge | 🟡 |

**How to use:** Clarify → estimate → API/data model → happy-path diagram → deep-dive the crux → trade-offs → failure modes. Say the interview trigger phrase out loud, then answer the Exercise without peeking.
