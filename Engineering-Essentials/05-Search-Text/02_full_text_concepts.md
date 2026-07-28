# Full-Text Search Concepts

> Turn text into **tokens**, normalize them (**stemming**), then rank docs by **relevance** (TF-IDF / BM25) — not just “contains string.”

## Plain English

Full-text search is a pipeline: analyze text into tokens, index them, then rank matches. Analyzer mismatches at index vs query time are why search “feels broken.”

## Essentials (must-know for this topic)

### Analysis pipeline

| Step | What happens | Example |
|------|--------------|---------|
| **Tokenization** | Split into terms | `Running Shoes!` → `Running`, `Shoes` |
| **Normalization** | Lowercase, strip punct | `running`, `shoes` |
| **Stopwords** | Drop common words | remove `the`, `a` |
| **Stemming / lemmatization** | Reduce to root | `running` → `run` |
| **Index** | Posting lists term → docs | inverted index |

**Golden rule:** same analyzer family at **index time** and **query time**.

### Relevance scoring

| Model | Idea |
|-------|------|
| **TF** | Term frequency in this doc |
| **IDF** | Rarer in corpus → more informative |
| **TF-IDF** | Classic combine |
| **BM25** | Modern Lucene/ES default — TF **saturates** (spam “bike bike bike” doesn’t win forever) |

### Precision vs recall (stemming trade-off)

| Goal | Effect of aggressive stemming |
|------|-------------------------------|
| **Recall** | `run` finds `running` — good |
| **Precision** | Unrelated stems collide — bad |
| SKUs / proper nouns | Often **don’t** stem — use `keyword` or custom analyzer |

### Substring vs token match

| Need | Technique |
|------|-----------|
| Token / stemmed word | Standard analyzer + BM25 |
| Partial substring | N-grams / wildcards (costlier) |
| Exact ID | `keyword` |

## Why seniors get asked

Shows you understand *why* search feels smart — and why analyzer mismatches make search “broken.”

## Simple example

```text
Document: "The runner ran a race"
Tokens (english analyzer): runner, run, race

Query: "running"
After analysis: run  → matches via stemming
```

```json
// Relevance intuition
// Doc A: "bike bike bike" in a corpus full of bikes → TF high but capped (BM25)
// Doc B: rare term "unicycle" matching query → higher IDF boost
```

## When to use / when not / trade-offs

| Invest in analyzers when… | Keep it simple when… |
|---------------------------|----------------------|
| Multilingual product search | Exact SKU / ID lookup |
| User-typed natural language | Structured filters only |

**Trade-offs:** stemming helps recall (“run” finds “running”) but can hurt precision (unrelated stems collide); language-specific analyzers matter.

## Common pitfalls

- Same text analyzed differently at index vs query time  
- Stemming proper nouns / SKUs  
- Ignoring language (English analyzer on German)  
- Expecting substring match without n-grams  

## Interview trigger phrase

> “Full-text means analyze to tokens and rank with BM25 — I’d keep analyzers consistent at index and query time.”

## Exercise

Explain why searching `SHOE-123` fails if the field used an english text analyzer. How do you fix mapping?
