# Elasticsearch / OpenSearch

> A distributed **search and analytics** engine built on an **inverted index** — documents are analyzed, sharded, and queried by relevance (or filters/aggs).

## Plain English

You index JSON documents into an **index** (like a table). Text is analyzed into tokens; an **inverted index** maps terms → documents. OpenSearch is the AWS-friendly fork; concepts transfer. ES is a **derived search view**, not your system of record.

## Essentials (must-know for this topic)

### Core concepts

| Concept | Meaning |
|---------|---------|
| **Inverted index** | For each term (`bike`), list of docs containing it — opposite of doc→words |
| **Analyzer** | Char filter → tokenizer → token filters (`Running Shoes` → `run`, `shoe`) |
| **Mapping** | Field types + analyzers (`text` vs `keyword`) |
| **Index** | Collection of docs (≈ table) |
| **Shard** | Slice of an index (primary + replicas) |
| **Near-realtime** | Refresh interval — not same instant as DB commit |

### `text` vs `keyword` (must get right)

| Type | Analyzed? | Use for |
|------|-----------|---------|
| **`text`** | Yes | Full-text search (`title`, `description`) |
| **`keyword`** | No (exact) | IDs, SKUs, enums, sort, aggs, filters |

Wrong type → exact match fails or aggs explode.

### Cluster vocab

| Term | Meaning |
|------|---------|
| **Primary shard** | Owns a partition of docs |
| **Replica** | Copy for HA/read scale |
| Shard count | Set at index creation (changing = reindex); don’t over-shard |

### ES vs primary DB

| ES/OS | Postgres/etc. |
|-------|----------------|
| Relevance, facets, log search | Transactions, source of truth |
| Async sync lag OK | Strong write consistency |

## Why seniors get asked

Product search, logs, and “find stuff fast” designs expect ES literacy: mappings, shards, and why it’s not your primary DB.

## Simple example

```json
PUT /products
{
  "mappings": {
    "properties": {
      "title": { "type": "text", "analyzer": "english" },
      "sku":   { "type": "keyword" },
      "price_cents": { "type": "integer" }
    }
  }
}
```

```bash
curl -X POST "localhost:9200/products/_doc" -H 'Content-Type: application/json' -d '
{"title":"Red running shoes","sku":"SHOE-1","price_cents":4999}'

curl "localhost:9200/products/_search?q=running"
```

## When to use / when not / trade-offs

| Use ES/OS when… | Prefer DB when… |
|-----------------|-----------------|
| Full-text relevance, facets, log search | Primary transactional source of truth |
| Near-realtime search at scale | Tiny datasets; simple equality lookups |
| Aggregations over text corpora | Strong multi-doc ACID |

**Trade-offs:** powerful search + scale vs operational complexity, eventual sync with source DB, mapping mistakes that require reindex.

## Common pitfalls

- Using `text` for IDs you need exact match (`keyword` instead)  
- Too many shards (overhead) or one giant shard  
- Treating ES as the system of record  
- Dynamic mapping surprises (`"yes"` becoming boolean)  

## Interview trigger phrase

> “I’d index denormalized search docs in Elasticsearch with explicit mappings and shards — Postgres remains source of truth.”

## Exercise

Index a product with title, brand, and tags. Which fields are `text` vs `keyword`? How many primary shards would you start with for 2M products and why?
