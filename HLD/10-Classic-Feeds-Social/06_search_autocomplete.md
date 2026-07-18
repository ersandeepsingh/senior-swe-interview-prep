# Design Search Autocomplete / Typeahead 🟡

> **Crux:** Prefix lookup at very low latency (trie / prefix index) plus ranking of suggestions — ideally served from the edge or a hot in-memory tier.

## Clarify (say this first)

**Functional**
- As user types, show top-K completions for the prefix
- Personalization optional (recents, history); global trending default
- Multilingual / typos optional park; empty query → trending
- Click-through updates popularity (async)

**Non-functional**
- Ultra-low latency: p99 < 50–100 ms end-to-end; often < 20 ms in-region
- Extremely high QPS (every keystroke); mostly read
- Stale ranking for minutes OK; availability over perfect freshness
- Prefix index must fit memory or edge cache for hot prefixes

## Back-of-envelope

```text
Assumptions: 50M DAU, 20 searches/day, ~5 keystrokes each with debounce
→ ~50–100K autocomplete QPS avg (peak several×)
Dictionary: 10M queries; top suggestions per prefix limited to K=8–10
Hot prefixes ("a", "how") tiny set → cache everything at edge
Update popularity: batch every few min from click/stream logs
```

## API + data model

```text
GET /api/v1/suggest?q=pre&limit=10 → [{ text, score, type }]
POST /api/v1/suggest/impression  (optional analytics)
```

| Store | Role |
|-------|------|
| Trie / prefix index | In-memory: prefix → top-K terms |
| Popularity table | `term → score` (frequency, CTR, time decay) |
| Edge / CDN cache | Cache responses for popular `q=` |
| Personalization | Per-user recent queries (Redis) |

## High-level architecture

```text
Client (debounce) → Edge/CDN → Suggest API
                                  │
                     ┌────────────┴────────────┐
                     ▼                         ▼
              In-memory trie             Personal recents
              (top-K per node)           (optional merge)
                     ▲
              Offline/stream job
              rebuilds scores + trie snapshot
```

## Deep dive: the crux

**Prefix data structure**

| Approach | Pros | Cons | Pick when |
|----------|------|------|-----------|
| Trie + top-K at each node | O(prefix) + instant top-K | Memory; rebuild | Classic interview answer |
| Sorted list / binary search | Simple | Slower range + rank | Small corpus |
| ES completion suggester | Managed | Ops + latency | Already on ES |
| Segment trees / n-gram | Fuzzy | Heavier | Typo tolerance asked |

**Ranking:** frequency × time decay × CTR; boost exact prefix match; optional personalization (merge global top-K with user history). Limit K small.

**Serving at edge:** most traffic is repeated short prefixes — cache `q → suggestions` at CDN/API with short TTL. Debounce client 30–50 ms. Shard tries by language or first character if memory-bound; broadcast hot root nodes.

**Updates:** don’t mutate trie on every click — aggregate in stream, periodically rebuild snapshot, atomic swap.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Top-K cached on trie nodes | Fast reads | Stale until rebuild; memory |
| Per-request full re-rank | Fresher | Miss p99 budget |
| Edge cache | Absorbs QPS | Personalization harder (vary by cookie carefully) |
| Fuzzy / typo | UX | Latency + index size |

## Failure modes & scale

- **Hot prefix stampede:** edge cache + request coalescing
- **Rebuild failure:** keep previous snapshot; never empty the service
- **Abuse / poison queries:** rate-limit, denylist, authenticity of popularity signals
- **Memory blowup:** store top-K only (not full postings) on deep nodes; prune rare terms
- **Multi-DC:** replicate snapshots; accept brief rank divergence

## Interview trigger phrase

> “I’d keep an in-memory trie with top-K suggestions precomputed on each node, rank from aggregated popularity offline, and serve hot prefixes from edge cache — keystrokes never hit a cold DB.”

## Exercise

1. How do you update popularity for a **breaking-news** query within a minute without rebuilding the whole trie?
2. Design **personalized** autocomplete without defeating CDN caching.
3. What changes if the corpus is **product catalog SKUs** instead of search queries?
