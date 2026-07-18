# Design a Recommendation System 🔴

> **Crux:** Split **heavy offline candidate generation / training** from **low-latency online serving** — retrieve thousands, rank dozens, all within a tight p99 budget.

## Clarify (say this first)

**Functional**
- Home feed / “for you” recommendations
- Implicit signals: views, clicks, dwell, purchases
- Cold start: new user / new item
- Filters: blocklist, inventory, diversity

**Non-functional**
- Serve p99 ~50–150 ms
- Freshness: hours for models; minutes for features/events
- Huge catalog (millions–billions of items)
- Explainability light; metrics: CTR, dwell, revenue

## Back-of-envelope

```text
100M DAU × 20 feed requests/day → ~25k QPS avg; 100k+ peak
Catalog: 10M items; retrieve 1k candidates → rank top 50
Features: user 2 KB + item 1 KB online; embedding dim 64–256
Offline: daily/hourly train; stream feature updates continuous
```

## API + data model

```text
GET /v1/recommend?user_id=&surface=home&limit=50
POST /v1/events  {user_id, item_id, type, ts}   # click/view
```

| Store | Contents |
|-------|----------|
| Event log | Kafka → warehouse / feature pipe |
| Feature store | user/item features online + offline |
| ANN index | embeddings for candidate gen |
| Model artifacts | ranker weights / graphs |

## High-level architecture

```text
  Client ──► API ──► Retrieval ──► Ranker ──► Blender / filters
                 │         │          │
                 │         │          └─ online features
                 │         └─ ANN / CF / popular / graph
                 └─ event → Kafka → feature jobs + train

  Offline: train two-tower / CF  → publish embeddings + ranker
  Online:  fetch candidates (ms) → score (ms) → return
```

## Deep dive: the crux

**Offline compute + low-latency serving:**
| Stage | Offline | Online |
|-------|---------|--------|
| **Candidates** | Train embeddings / CF / graphs | ANN / inverted / co-vis retrieval (~1k) |
| **Features** | Batch aggregates | Feature store point lookups |
| **Rank** | Train LTR / NN | Lightweight model on candidates |
| **Explore** | Bandit params | ε-greedy / slots reserved |

**Alternatives:** pure popularity (cold start); only collaborative filter (sparse); only online learning (complex). **Pick:** multi-source retrieval → ML ranker → rules (diversity, ads); two-tower embeddings offline, ANN online; stream events for near-real-time features.

**Cold start:** bootstrap with popularity + content embeddings; promote new items via explore slots. Log impressions/skips so offline training sees the full funnel, not only clicks.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Deep ranker | Quality | Latency / cost |
| Larger candidate set | Recall | Rank CPU |
| Hourly retrain | Fresh | Pipeline cost |
| Heavy personalization | Engagement | Filter bubble; cold start |
| Multi-retriever fan-in | Coverage | Merge complexity |

## Failure modes & scale

- **Ranker down:** fall back to popularity / CF-only; degrade gracefully
- **ANN stale:** new items missing — sidepath “new item” retriever
- **Feature skew:** train/serve mismatch — shared feature definitions
- **Feedback loop:** popular gets more popular — exploration slots
- **Hot user/item keys:** cache embeddings; shard feature store

## Interview trigger phrase

> “I’d **retrieve candidates from multiple cheap sources** (ANN, popular, graph), then **score with a ranker using online features** — heavy training stays **offline**, serving stays a tight multi-stage cascade.”

## Exercise

1. Budget 80 ms — allocate time across retrieval, features, rank, blend.  
2. Brand-new item with no interactions — how does it enter feeds?  
3. Ranker model file is corrupt after deploy — what’s your fallback path?
