# RAG, Embeddings, and Vector Databases

> **One-line definition:** RAG (Retrieval-Augmented Generation) fetches relevant private or fresh documents at query time, stuffs them into the prompt, and only then asks the LLM to answer — so the model reasons over *your* evidence, not just training memory.

---

## Plain English

LLMs don’t know your wiki, tickets, or yesterday’s policy PDF. Fine-tuning won’t keep up with daily changes either. **RAG** solves “private + fresh knowledge” by:

1. Turning documents into **embeddings** (vectors that capture meaning).
2. Storing them in a **vector database**.
3. At ask-time: embed the question → **similarity search** → top chunks → prompt the LLM with those chunks → generate an answer (often with citations).

The LLM still only proposes text. Your retrieval pipeline and APIs decide *what* it may see; authz still gates which docs a user can retrieve.

```text
Docs → chunk → embed → vector DB
                ▲
User question → embed → similarity search → top-k chunks
                                              │
                                              ▼
                         Prompt: system + chunks + question → LLM → answer (+ citations)
```

---

## Essentials

### Why RAG

| Need | Why the base model fails | What RAG adds |
|------|--------------------------|---------------|
| Private data | Never in training | Your corpus at query time |
| Fresh facts | Knowledge cutoff / drift | Re-index new docs |
| Grounding | Hallucinates confidently | Answer from retrieved evidence |

### Embeddings intuition

An embedding is a list of numbers representing semantic meaning. Similar text → vectors that point in a similar direction. “cancel my subscription” and “how do I end my plan?” land near each other even if the words differ.

You don’t interpret each dimension; you care about **distance / similarity** between vectors.

### Chunking

| Choice | Guidance |
|--------|----------|
| **Size** | Enough context to stand alone (often ~200–800 tokens), not whole books |
| **Overlap** | Small overlap so sentences split across boundaries aren’t lost |
| **Unit** | Prefer semantic units (section, paragraph) over blind fixed splits when possible |
| **Metadata** | Store source, title, updated_at, acl tags with each chunk |

Bad chunking = retrieval returns fragments that confuse the model.

### Vector DB + similarity search

| Concept | Meaning |
|---------|---------|
| **Vector DB** | Stores embeddings + metadata; supports nearest-neighbor queries |
| **Cosine similarity** | Angle between vectors — common relevance score |
| **ANN** | Approximate Nearest Neighbor — fast top-k at scale (HNSW, IVF, etc.) |
| **Filter** | Always filter by tenant/ACL *before or with* the vector search |

### Retrieve-then-generate flow

| Step | Owner | Action |
|------|-------|--------|
| 1 | App | Authenticate user; scope corpus by permission |
| 2 | App | Embed query; ANN search + metadata filters |
| 3 | App | Rerank / trim to token budget |
| 4 | LLM | Generate answer from provided chunks only |
| 5 | App | Attach citations (chunk → source URL/doc id) |

### Hybrid search

| Method | Strength |
|--------|----------|
| **Dense (embeddings)** | Paraphrase / semantic match |
| **Sparse (BM25 / keyword)** | Exact IDs, error codes, rare terms |
| **Hybrid** | Combine both scores — often best in production |

### Citations

Return `source_id`, title, and snippet for each used chunk. Citations don’t prove truth, but they make answers auditable and help users verify.

### Common failure modes

| Failure | Cause | Fix |
|---------|-------|-----|
| **Bad chunking** | Too big/small/split mid-thought | Retune size; semantic splits; overlap |
| **Stale index** | Docs updated, vectors not | Incremental re-embed; TTL; sync jobs |
| **Wrong neighbor** | Ambiguous query / weak embeddings | Hybrid search; reranker; query rewrite |
| **Permission leak** | Search without ACL filter | Filter by tenant/user on every query |
| **Context stuffing** | Too many chunks | Top-k + token budget; summarization |

---

## Simple example

```python
# Pseudocode: retrieve-then-generate (authz on retrieve)
def answer(user, question: str) -> str:
    qvec = embed(question)
    chunks = vector_db.search(
        qvec,
        k=5,
        filter={"tenant_id": user.tenant_id},  # never skip
    )
    context = "\n\n".join(c.text for c in chunks)
    return llm.chat([
        {"role": "system", "content": "Answer only from CONTEXT. Cite sources."},
        {"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION: {question}"},
    ])
```

---

## When to use / trade-offs

- **Use RAG** for internal knowledge, policies, product docs, support macros — anything private or changing.
- **Don’t use RAG** for pure style/format tasks or when a single SQL lookup is the real answer.
- **Trade-offs:** indexing/ops cost and retrieval quality vs freshness and grounding. RAG quality is mostly retrieval quality.

---

## Pitfalls

- Embedding without ACL filters (cross-tenant leaks).
- Never refreshing the index after doc updates.
- Dumping 50 chunks into the prompt “to be safe.”
- Expecting citations to appear magically without prompting + returning source metadata.
- Treating vector search alone as enough for SKUs, ticket IDs, and error codes — add keyword/hybrid.

---

## Interview trigger phrase

> “RAG retrieves authorized chunks via embeddings and similarity search, then the LLM generates from that evidence — I treat retrieval + ACL filters as the source of truth path, not the model’s memory.”

---

## Exercise

You have a 40-page employee handbook that updates monthly.
1. Sketch chunk → embed → index → query → generate with one ACL filter.
2. Give one case where hybrid search beats pure vectors.
3. List two symptoms of a stale index and how you’d detect them.
