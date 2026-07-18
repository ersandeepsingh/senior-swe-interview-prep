# Inverted Index & Full-Text Search

> SQL `LIKE '%shoe%'` doesn’t scale. An **inverted index** maps terms → document IDs so Elasticsearch-style engines can retrieve and score matches in milliseconds.

## Plain English

**Forward index:** doc → words. **Inverted index:** word → list of docs (postings), often with positions for phrase search.

Pipeline: analyze text (tokenize, lowercase, stem) → index → query → retrieve candidates → score → return page.

| Building block | Role |
|----------------|------|
| **Analyzer** | How text becomes tokens |
| **Postings list** | Doc IDs (+ positions, freqs) |
| **Shard** | Horizontal split of the index |
| **Replica** | Copy for HA / read scale |

```text
  Docs:  D1 "red running shoes"
         D2 "blue shoes sale"

  Inverted index:
    red      → D1
    running  → D1
    shoes    → D1, D2
    blue     → D2
    sale     → D2

  Query "shoes" → postings {D1,D2} → rank → results
```

## Simple example

E-commerce search “nike air”. Tokens `nike`, `air` → intersect/union postings → BM25 score → top 20. Filters (size=10, in_stock) applied as bitsets / doc values. Autocomplete may use edge n-grams or a separate completion suggester.

```text
  Write path:
  OLTP product update → CDC/queue → indexer → ES shard refresh
  (near-real-time ≠ instantly searchable)
```

**Indexing path:** product CDC / queue → indexer workers → shards. Near-real-time refresh (ES) ≠ instantly searchable on write.

## Why prefer one over the other

| Prefer **search engine (ES/OpenSearch/Solr)** when… | Prefer **DB / KV** when… |
|----------------------------------------------------|--------------------------|
| Full-text, fuzzy, facets, relevance | Exact ID / key lookup |
| Typo tolerance, highlighting | Strong transactional source of truth |
| Relevance tuning matters | Simple equality filters |

**Source of truth** stays in OLTP; search is a **derived index**. Rebuild/reindex plans matter (mapping changes, analyzer updates).

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Inverted index | Fast text retrieval | Index size; eventual sync lag |
| More analyzers / n-grams | Better recall / autocomplete | Bigger index, noisier matches |
| Many shards | Scale | Overhead; wrong shard count hurts |
| Sync index on write | Fresher search | Write latency / availability coupling |

**Trap:** Treating Elasticsearch as the system of record for orders. Seniors: **OLTP writes → async index**; handle delete/update consistency.

**Deletes & updates:** soft-delete flags or delete-by-query; version conflicts on concurrent updates — use external versioning from OLTP when needed.

**Relevance vs filters:** filters (stock, price range) are often cheaper than scored queries; apply filters early to shrink the candidate set.

## Interview trigger phrase

> “I’d keep products in OLTP, **CDC into an inverted index** for search, and tune analyzers + BM25 — accepting seconds of index lag for query speed.”

## Exercise

**Design product search for 50M SKUs.**

1. How do updates (price/stock) reach the index without blocking writes?
2. Why shard by product_id hash vs by category?
3. One sentence on what the user sees if index lag is 10s after a price cut.
