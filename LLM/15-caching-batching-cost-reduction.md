# Caching, Batching, and Reducing Token Costs

> **One-line definition:** Most LLM spend is tokens × price × volume — you cut cost by reusing work (cache), grouping work (batch), shrinking what you send/receive, and routing easy tasks to smaller/cheaper models.

---

## Plain English

Every character you stuff into a prompt and every token the model writes costs money (and latency). Seniors don’t only pick a cheaper model — they **measure** where tokens go, then:

- **Cache** repeated prompts or semantically similar answers.
- **Batch** offline jobs so you pay bulk rates / lower priority.
- **Trim** history, tool payloads, and RAG chunks.
- **Route** simple classifications to small models; reserve large models for hard reasoning.

Caching never bypasses authz: a cached “order status” answer for user A must not be served to user B.

```text
Cost ≈ (input_tokens + output_tokens) × $/token × requests
     ↓ reduce inputs (trim, cache prefixes, smaller tools)
     ↓ reduce outputs (max_tokens, concise prompts)
     ↓ reduce requests (semantic cache, batch offline)
     ↓ reduce $/token (smaller model, batch tier)
```

---

## Essentials

### Prompt / response caching

| Type | Idea | Good for |
|------|------|----------|
| **Exact response cache** | Same request key → return stored answer | Deterministic FAQs, identical prompts |
| **Prompt-prefix caching** | Provider reuses KV for a long shared system/RAG prefix | Large stable system prompts, repeated tool schemas |
| **Semantic cache** | Embed query; if near a past query, reuse answer | Support bots with paraphrase-heavy traffic |

Always key caches by **tenant / user / ACL scope** where answers are user-specific.

### Prompt-prefix caching (provider feature)

| Do | Don’t |
|----|-------|
| Put **stable** content first (system, tool defs, big static policy) | Put user-specific text first (breaks prefix reuse) |
| Keep the shared prefix byte-identical across calls | Tweak whitespace/order every request |
| Measure cache hit rate from provider metrics | Assume caching with no observability |

### Batching requests

| Mode | When | Benefit |
|------|------|---------|
| **Async batch APIs** | Offline evals, embeddings, nightly summaries | Lower $/token, higher latency OK |
| **App-level batching** | Embed many chunks in one call | Fewer HTTP round-trips |
| **Not for** | Interactive user chat | Users won’t wait for a batch window |

### Trimming history / summarization

| Technique | Effect |
|-----------|--------|
| **Sliding window** | Keep last N turns only |
| **Summarize older turns** | Compress long chats into a short memory blob |
| **Drop tool traces** | Keep final tool results, not every intermediate blob |
| **Hard token budget** | Truncate before calling the API |

### Smaller models for easy tasks

| Task | Typical model tier |
|------|-------------------|
| Classification, routing, short extract | Small / mini |
| Tool-orchestrated multi-step agent | Mid / large |
| Hard reasoning, subtle writing | Large |

Use a **router**: cheap model decides “easy vs hard,” then escalate.

### Cap max_tokens & tool payloads

| Knob | Why |
|------|-----|
| **`max_tokens`** | Stops runaway essays; bounds worst-case output cost |
| **Tool result size** | Truncate lists; return IDs + summaries, not full tables |
| **RAG top-k / chunk size** | Retrieval quality plateaus; extra chunks mostly burn money |
| **Response format** | “3 bullets max” beats hoping the model stays brief |

### Measuring savings

| Metric | What it tells you |
|--------|-------------------|
| Tokens in / out per request | Where the mass is |
| $/successful task | Real unit economics |
| Cache hit rate | Whether caching works |
| Model mix (% mini vs large) | Routing effectiveness |
| p95 latency | Cost tricks that hurt UX |

Log `request_id`, model, token counts, cache hit, user/tenant. Optimize from data, not vibes.

---

## Simple example

```python
# Pseudocode: prefix-friendly prompt + caps + semantic cache (scoped)
def ask(user, question: str) -> str:
    cache_key = semantic_key(user.tenant_id, question)  # ACL in the key
    if hit := cache.get(cache_key):
        return hit

    # Stable prefix first → better provider prefix-cache hits
    messages = [
        {"role": "system", "content": BIG_STABLE_SYSTEM},  # tools + policy
        {"role": "user", "content": f"{trim_history(user)}\n\nQ: {question}"},
    ]
    resp = client.chat.completions.create(
        model=route_model(question),   # mini vs large
        messages=messages,
        max_tokens=300,
    )
    answer = resp.choices[0].message.content
    cache.set(cache_key, answer, ttl=3600)
    return answer
```

---

## When to use / trade-offs

- **Cache** when traffic repeats (FAQ, similar tickets) and answers aren’t ultra-personalized — or key carefully when they are.
- **Batch** for offline embedding/eval/summary jobs, not user-facing chat.
- **Trade-offs:** stale cache vs savings; small models miss edge cases; aggressive truncation can drop needed context. Measure quality alongside cost.

---

## Pitfalls

- Semantic cache without tenant/user scope → data leak.
- Putting volatile user text before a huge static prefix → prefix cache never hits.
- Unlimited `max_tokens` and fat tool dumps “just in case.”
- Batching interactive UX and wondering why p95 latency exploded.
- Celebrating lower token counts while task success rate tanks — track both.

---

## Interview trigger phrase

> “I treat cost as tokens × price × volume: cache safe repeats (scoped by auth), batch offline work, trim history and tool payloads, cap max_tokens, and route easy tasks to smaller models — measured by $/successful task and cache hit rate.”

---

## Exercise

Your support bot averages 4k input tokens (2k static system + 1.5k history + 0.5k question) and 400 output tokens.
1. Name three concrete cuts you’d try first and what each targets.
2. Would you use exact cache, semantic cache, or prefix cache for “How do I reset my password?” — why?
3. Write the cache key fields you’d include so user A never gets user B’s order answer.
