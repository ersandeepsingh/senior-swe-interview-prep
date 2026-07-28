# Vector Search / Embeddings

> Represent text (or images) as **vectors** in high-dimensional space — “similar meaning” ≈ **nearby vectors**, found with **ANN** indexes.

## Plain English

An embedding model turns text into a float vector. Nearest neighbors ≈ semantic similarity (“athlete footwear” ↔ “running shoes”) without shared keywords. Usually combined with keyword filters — **hybrid search**.

## Essentials (must-know for this topic)

### Pipeline

| Step | What |
|------|------|
| 1 | **Embed** documents offline (title/description → vector) |
| 2 | Store vectors + metadata (ES kNN, pgvector, Pinecone, …) |
| 3 | Embed the **query** at request time |
| 4 | **ANN** find top-k neighbors (+ filters) |

### Vocab

| Term | Meaning |
|------|---------|
| **Embedding** | Dense vector (e.g. 384–1536 dims) |
| **Similarity** | Cosine / dot / L2 — “nearby = similar meaning” |
| **ANN** | Approximate Nearest Neighbor — fast, slightly lossy |
| **HNSW / IVF** | Common ANN index structures |
| **Hybrid search** | Vector recall + BM25/keyword + business boosts |
| **RAG** | Retrieve chunks via vectors → feed LLM |

### Vector vs BM25

| Prefer vectors when… | Prefer keyword/BM25 when… |
|----------------------|---------------------------|
| Synonyms / intent / NL queries | Exact SKU, names, legal terms |
| Multimodal (image→image) | Users type precise codes |
| Semantic catalog browse | Tiny corpus; FTS enough |

### Ops must-knows

| Topic | Line |
|-------|------|
| Model change | **Re-embed** the corpus |
| Filters | Always constrain (in_stock, locale) — pure kNN is noisy |
| Cost | Embedding compute + ANN memory |

## Why seniors get asked

Modern must-know. RAG, recommendations, and semantic product search all use vectors. Seniors discuss hybrid retrieval and operational cost.

## Simple example

```python
# Pseudocode
q_vec = embed("comfortable shoes for marathon")
results = vector_index.search(q_vec, k=10, filter={"in_stock": True})
```

```json
// OpenSearch/ES kNN sketch
{
  "query": {
    "knn": {
      "title_vector": {
        "vector": [0.01, -0.2, "..."],
        "k": 10
      }
    }
  }
}
```

## When to use / when not / trade-offs

| Use vectors when… | Prefer keyword/BM25 when… |
|-------------------|---------------------------|
| Synonyms / intent / natural language | Exact SKU, names, legal terms |
| Multimodal (image→image) | Users type precise product codes |
| Hybrid ranking needed | Tiny corpus; LIKE/FTS enough |

**Trade-offs:** better semantic recall vs cost (GPU/embeddings), index memory, approximate results, and stale embeddings when models change (re-embed).

## Common pitfalls

- Embedding only, no keyword filter → irrelevant semantic neighbors  
- Changing models without reindexing vectors  
- Huge kNN without filters → slow/noisy  
- Ignoring privacy of embedded user text  

## Interview trigger phrase

> “I’d embed documents and queries for semantic recall, use ANN for speed, and hybridize with BM25 filters for precision.”

## Exercise

Product search: user types “gift for dad who hikes.” Outline hybrid retrieval (vector + keyword + business boosts) in 4 steps. When do you re-embed the catalog?
