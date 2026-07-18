# Ranking & Relevance

> Retrieval finds **candidates**; **ranking** decides order. Classical **BM25/TF-IDF** scores text match; **ML re-rankers** blend engagement, quality, and business goals in a second stage.

## Plain English

Two-stage is the interview default:

1. **Retrieve** cheap top-K (inverted index, ANN, filters) — hundreds/thousands.
2. **Rank / re-rank** with richer features or a model — top 10–50.

Scoring layers people mix up: **text relevance** (BM25) ≠ **personalization** ≠ **business rules** (boosts, demotions).

```text
  Query ──► Retrieve (BM25 / ANN) ──► candidates (~200)
                    │
                    ▼
            Feature join (CTR, price, freshness)
                    │
                    ▼
            Ranker (LM/GBT / neural) ──► top 20
                    │
                    ▼
            Business rules (boost paid, demote spam)
```

## Simple example

Search “wireless headphones”: BM25 returns text-similar SKUs. Re-ranker uses historical CTR, rating, stock, margin. Sponsored items may get a controlled boost — disclosed per policy.

```text
  Feed ranking (same pattern):
    candidate gen (follow graph / topic)
         → ranker (engagement probability)
         → diversity (author / topic caps)
```

**Offline vs online:** train on logged features; serve with **point-in-time** correct features to avoid leakage. Evaluate with NDCG / offline + online A/B.

## Why prefer one over the other

| Prefer **classic BM25 only** when… | Prefer **ML re-rank** when… |
|------------------------------------|-----------------------------|
| Small corpus, simple needs | Engagement/$$ depends on order |
| Explainability & ops simplicity | You have labels / click logs |
| Latency ultra-tight | Can afford 10–30ms re-rank |

**Learning-to-rank** needs feedback loops and careful evaluation. Don’t claim neural ranker without data/infra story (feature store, training pipeline, A/B).

**ANN (HNSW etc.):** vector retrieval for semantic search — still usually followed by re-rank.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Deep re-rank | Better relevance / revenue | Latency, complexity, feature cost |
| Heavy business boosts | Short-term $$ | Trust / long-term relevance |
| Pure engagement optimize | Clicks | Clickbait, filter bubbles |
| One-stage score-all-docs | Simple mentally | Impossible at corpus scale |

**Trap:** One giant model scoring 10M docs online. Seniors: **cheap retrieve → expensive re-rank on small K**.

**Position bias:** clicks on rank #1 aren’t pure relevance — train with debiasing / randomization when you claim LTR sophistication.

**Freshness:** news and social need a time-decay feature or candidates die in the index while BM25 still loves old exact matches.

## Interview trigger phrase

> “I’d **retrieve with BM25/ANN**, then **ML re-rank** a few hundred candidates with CTR and quality features — keep the heavy model off the full corpus.”

## Exercise

**Rank results for a news search product.**

1. List 5 features for the re-ranker (besides text score).
2. How do you avoid training-serving skew on “hours since publish”?
3. One sentence on diversity vs pure relevance.
