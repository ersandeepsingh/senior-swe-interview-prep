# Search Engine vs DB `LIKE`

> `LIKE '%term%'` scans text the hard way; a **search engine** uses inverted indexes and relevance — different tool for different jobs.

## Plain English

`LIKE` is fine for small/admin tools. User-facing product search at scale needs inverted indexes, analyzers, and ranking — accepting sync lag with the source DB.

## Essentials (must-know for this topic)

### Head-to-head

| | **SQL `LIKE` / `ILIKE`** | **Elasticsearch / dedicated search** |
|--|--------------------------|--------------------------------------|
| Mechanism | Often seq scan / trigram | Inverted index + analyzers |
| Ranking | None (unless you add it) | BM25 / custom relevance |
| Scale | Hurts on large text corpora | Built for it |
| Features | Basic pattern match | Fuzzy, facets, highlighting, synonyms |
| Freshness | Same as DB transaction | Usually async near-realtime |
| Ops | None extra | Cluster + sync pipeline |

### Middle ground in Postgres

| Feature | When it helps |
|---------|----------------|
| **`pg_trgm`** | Fuzzy/`ILIKE` with GIN/GIST — medium data |
| **`tsvector` / FTS** | Real token+rank search without ES |
| Still not | Full search platform (synonyms UX, heavy facets at huge scale) |

### Decision cheat sheet

| Stick with DB when… | Add search engine when… |
|---------------------|-------------------------|
| Small data, rare text search | Catalog search UX at scale |
| Exact/prefix on indexed columns | Typo tolerance, facets, synonyms |
| Must be transactionally fresh | Relevance is a product feature |
| 500 rows admin UI | 10M products typeahead |

### Cost you must name

| Choice | #1 operational cost |
|--------|---------------------|
| ES/OS | Sync lag + cluster ops + reindex |
| Postgres FTS | Tuning dictionaries; still on primary DB load |
| `LIKE '%x%'` hot path | CPU/IO melt |

## Why seniors get asked

Classic trade-off question. Seniors say when `LIKE` is fine and when to introduce ES — with sync cost.

## Simple example

```sql
-- Works for admin tools / small tables; painful at scale
SELECT id, title FROM products WHERE title ILIKE '%run%';
```

```bash
# Search engine: token match + score
curl "localhost:9200/products/_search?q=title:run"
```

## When to use / when not / trade-offs

| Stick with DB when… | Add a search engine when… |
|---------------------|---------------------------|
| Small data, rare text search | Product catalog search UX |
| Exact/prefix on indexed columns | Typo tolerance, facets, synonyms |
| Strong consistency with writes | Relevance tuning is a product need |

**Trade-offs:** `LIKE` is simple and consistent; search engines add infra + sync lag + richer UX.

## Common pitfalls

- Leading-wildcard `LIKE '%foo'` on huge tables in the hot path  
- Expecting `LIKE` to rank well  
- Jumping to ES for 500 rows  
- Forgetting search lag after DB writes  

## Interview trigger phrase

> “LIKE is fine for small/admin search; user-facing relevance at scale needs an inverted index — Postgres FTS or Elasticsearch — accepting sync complexity.”

## Exercise

10M products, typeahead + filters + typo tolerance. Argue against `ILIKE`, pick Postgres FTS vs Elasticsearch, and name the #1 operational cost of your choice.
