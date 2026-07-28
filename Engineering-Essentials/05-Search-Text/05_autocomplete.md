# Autocomplete / Typeahead

> Suggest completions as the user types — usually via **edge n-grams**, **prefix queries**, or a **completion suggester**, not full BM25 search.

## Plain English

User types `run` → show `running shoes`, `runner jacket`. Needs to be **fast** and prefix-oriented — a different index design from the main results page.

## Essentials (must-know for this topic)

### Techniques compared

| Technique | Idea | Pros | Cons |
|-----------|------|------|------|
| **Edge n-grams** | Index `r`, `ru`, `run`, … | Filterable with bool/docs | Index size grows |
| **`prefix` / `match_phrase_prefix`** | Query-time prefix | Simple | Can be slower at scale |
| **Completion suggester** | In-memory FST | Ultra-fast suggests | Less flexible filters (design constraint) |
| **Redis / trie / edge service** | Custom typeahead | Full control | Extra system |

### Autocomplete vs full search

| | Typeahead | Results page |
|--|-----------|--------------|
| Goal | Fast prefix suggestions | Relevance ranking |
| Query | Every keystroke (debounced) | Submit / refined search |
| Index | N-grams / completion | Standard analyzers + BM25 |
| Size | Top 5–10 | Pages of hits |

### UX / product knobs

| Knob | Guidance |
|------|----------|
| **Debounce** | ~150–300ms client-side |
| **`size`** | Small (5–10) |
| **Popularity** | Rank by sales/searches, not obscure matches first |
| **SKU vs title** | Often **two fields/analyzers** (keyword-ish vs edge-ngram text) |

### Multi-word prefixes

`run sho` needs phrase/prefix strategy — plain single-term edge n-grams may be insufficient; plan for it.

## Why seniors get asked

Search UX interviews dig into autocomplete separately from “search results page” — different index design.

## Simple example

```json
// Edge n-gram analyzer sketch (index-time)
{
  "settings": {
    "analysis": {
      "tokenizer": {
        "edge_ngram_tokenizer": {
          "type": "edge_ngram",
          "min_gram": 2,
          "max_gram": 15,
          "token_chars": ["letter", "digit"]
        }
      }
    }
  }
}
```

```json
GET /products/_search
{
  "query": {
    "bool": {
      "must": [{ "match": { "title_autocomplete": "run" } }],
      "filter": [{ "term": { "active": true } }]
    }
  },
  "size": 8
}
```

## When to use / when not / trade-offs

| Use edge n-grams when… | Use completion suggester when… |
|------------------------|--------------------------------|
| Need filterable autocomplete | Pure suggest strings, max speed |
| Moderate corpus | Fixed dictionary of phrases |

**Trade-offs:** n-grams inflate index size; completion suggester is fast but less flexible with per-doc filters (improved over time, still a design constraint).

## Common pitfalls

- Running full `_search` BM25 on every keystroke without debounce  
- N-grams on huge text bodies (index explosion)  
- No popularity ranking → obscure suggestions first  
- Ignoring multi-word prefixes (`run sho`)  

## Interview trigger phrase

> “For typeahead I’d edge-ngram or a completion suggester, debounce client-side, and rank by popularity — separate from the main results query.”

## Exercise

Design autocomplete for SKUs (`SHOE-123`) and product titles. Why might you use two fields/analyzers? What’s your max `size` and debounce?
