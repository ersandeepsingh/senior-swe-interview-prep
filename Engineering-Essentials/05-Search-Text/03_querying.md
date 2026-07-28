# Querying (Bool, Filters, Aggregations)

> Compose search with **bool** clauses: some clauses **score** (queries), some only **include/exclude** (filters), plus **aggregations** for facets/counts.

## Plain English

Real search UIs are text + filters + facets. Structure bool queries so hard constraints don’t mess up relevance scoring — and so filters stay cacheable.

## Essentials (must-know for this topic)

### Query context vs filter context

| Context | Affects `_score`? | Cached? | Use for |
|---------|-------------------|---------|---------|
| **Query** | Yes | Less | Text relevance (`match` “red shoes”) |
| **Filter** | No (yes/no) | Yes | Price, stock, category, authz |

**Rule:** hard constraints → `filter`; “how well text matches” → `must`/`should`.

### Bool clauses

| Clause | Meaning |
|--------|---------|
| **`must`** | Must match; contributes score |
| **`filter`** | Must match; **no** score |
| **`should`** | Nice-to-have / soft boost (or required if no must) |
| **`must_not`** | Exclude |

### Aggregations (facets)

| Agg type | Use |
|----------|-----|
| **`terms`** | Brand/size facet counts |
| **`range` / histogram** | Price buckets |
| **stats/avg** | Metrics over hits |

Use **`keyword`** (or `.keyword` multi-field) for `terms` aggs — not analyzed `text`.

### Pagination

| Approach | Note |
|----------|------|
| `from` / `size` | Fine for shallow pages |
| **`search_after`** | Deep pagination / continuous scroll |

## Why seniors get asked

Real search UIs are filters + text + facets. Seniors structure bool queries instead of one giant scored `AND`.

## Simple example

```json
POST /products/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "title": "running shoes" } }
      ],
      "filter": [
        { "term": { "in_stock": true } },
        { "range": { "price_cents": { "lte": 8000 } } }
      ],
      "must_not": [
        { "term": { "brand.keyword": "BlockedBrand" } }
      ]
    }
  },
  "aggs": {
    "brands": { "terms": { "field": "brand.keyword", "size": 10 } }
  }
}
```

## When to use / when not / trade-offs

| Use | When |
|-----|------|
| `filter` | Facets, authz, price, status — cache-friendly |
| `must` match | Full-text relevance |
| `should` | Soft boosts (“prefer featured”) |
| `aggs` | Sidebar facet counts |

**Trade-offs:** complex bools are powerful but hard to tune; scoring everything prevents filter cache efficiency.

## Common pitfalls

- Using `match` on `keyword` fields (or vice versa)  
- Putting filters in `must` and wondering about weird scores  
- High-cardinality `terms` aggregations blowing memory  
- Deep pagination with `from/size` — prefer `search_after`  

## Interview trigger phrase

> “I’d put text in must for BM25 scoring and structured constraints in filter — aggregations for facets.”

## Exercise

Write a bool query sketch: text “blue jacket”, category=men, price 20–100, boost featured items, facet by size. Mark which clauses are filter vs score.
