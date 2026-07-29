# 07 · Token Usage & Billing

**One-line definition:** You pay per **token** (a chunk of text ≈ ¾ of a word), billed separately for input and output; cost ≈ (input tokens × input price) + (output tokens × output price).

---

## Plain English

LLMs don't see words — they see **tokens** (sub-word pieces). "tokenization" might be 3 tokens: `token` + `iz` + `ation`. Rough rule: **1 token ≈ 4 characters ≈ 0.75 words**, so ~1,000 tokens ≈ 750 words.

Every API response includes a `usage` object with exactly how many tokens you spent. Providers publish prices **per 1 million tokens**, split into **input (prompt)** and **output (completion)**. Output is almost always more expensive.

Your job as the engineer: know these numbers, estimate cost *before* shipping a feature, and put budgets/caps in place so one runaway loop doesn't burn your monthly spend.

---

## Essentials

### The `usage` object

```json
"usage": {
  "prompt_tokens": 1200,      // everything you SENT (system + history + user + tools)
  "completion_tokens": 350,   // what the model GENERATED
  "total_tokens": 1550
}
```

- `prompt_tokens` grows with conversation history, RAG context, few-shot examples, and tool schemas.
- `completion_tokens` is what you control with `max_tokens`.

### Cost formula

```
cost = (prompt_tokens / 1_000_000) * input_price_per_M
     + (completion_tokens / 1_000_000) * output_price_per_M
```

### Worked example (illustrative prices, always check current rates)

Assume a model at **$0.15 / 1M input**, **$0.60 / 1M output**.

| Item | Tokens | Rate ($/1M) | Cost |
|------|--------|-------------|------|
| Prompt | 1,200 | 0.15 | $0.00018 |
| Completion | 350 | 0.60 | $0.00021 |
| **Total** | 1,550 | — | **$0.00039** |

Now multiply by **1,000,000 requests/month** → ~**$390/month**. Small per-call numbers become real money at scale.

### Why output usually costs more

- Output is generated **autoregressively** — one token at a time, each needing a full forward pass — so it's compute-heavier than ingesting input in parallel.
- Practical takeaway: **cap `max_tokens`** and ask for concise answers; trimming output often saves more than trimming input.

### Cost levers

| Lever | Effect | Cost impact |
|-------|--------|-------------|
| `max_tokens` cap | Limits output length | ↓ output cost (the pricey side) |
| Smaller model | Cheaper per token | Big ↓, watch quality |
| Prompt caching | Reuse static prefix (system + few-shot) | ↓ input cost (up to ~50–90% on cached part) |
| Batch API | Async, non-urgent jobs | ~50% ↓ on many providers |
| Trim history | Send only needed turns | ↓ input cost |
| RAG chunk limits | Fewer retrieved tokens | ↓ input cost |

### Prompt caching

Providers can cache a **repeated prefix** (e.g. a big system prompt + few-shot examples that don't change) so you're charged less for those input tokens on subsequent calls.

- Put **stable content first**, variable content (the user's question) last.
- Great for chatbots, agents, and RAG where the instructions are fixed.
- Read the `usage` fields for cached tokens (e.g. `prompt_tokens_details.cached_tokens`) to verify hits.

### Batch discounts

For non-real-time work (nightly summarization, bulk classification, evals), submit a **batch job**. It runs asynchronously within a window (often 24h) at roughly **half price**. Trade latency for cost.

---

## Estimating cost before you ship

1. Take a **realistic sample** request (typical system prompt + history + user input).
2. Count tokens with a tokenizer (e.g. Python `tiktoken`) or read `usage` from a test call.
3. Multiply by expected input/output split and current prices.
4. Multiply by projected volume (per day / per tenant).
5. Add headroom for retries and longer-than-average inputs.

```python
# Quick offline estimate with tiktoken
import tiktoken
enc = tiktoken.get_encoding("o200k_base")
prompt_tokens = len(enc.encode(my_full_prompt))
est_cost = prompt_tokens/1e6 * 0.15 + 350/1e6 * 0.60  # assume ~350 output
```

---

## Budgeting per feature / tenant

| Technique | What it does |
|-----------|--------------|
| Per-request token cap | `max_tokens` + input truncation |
| Per-tenant quota | Track tokens per customer; throttle at limit |
| Per-feature budget | Tag calls (e.g. `feature=summarize`) and sum spend |
| Rate limiting | Cap requests/min per user to stop loops |
| Spend alerts | Alarm at 50/80/100% of monthly budget |
| Model tiering | Cheap model default, expensive only when needed |

Log `feature`, `tenant_id`, `model`, and `usage` on **every** call so you can attribute cost.

---

## When to use / trade-offs

| Optimization | Use when | Trade-off |
|--------------|----------|-----------|
| Prompt caching | Large fixed prefix, high volume | Setup + prefix must be stable |
| Batch API | Latency-tolerant bulk jobs | Not for interactive UX |
| Smaller model | Simple/structured tasks | Possible quality drop — eval first |
| Aggressive `max_tokens` | Cost-sensitive | Risk truncation (`finish_reason: length`) |

---

## Pitfalls

- **Confusing tokens with words** → underestimating cost by ~30%.
- **Forgetting the prompt side** → long system prompts, RAG context, and tool schemas are billed *every* call.
- **Only capping input** → output is the expensive side; cap `max_tokens` too.
- **No per-tenant attribution** → can't tell who's driving the bill.
- **Ignoring cache-friendly ordering** → variable content early kills cache hits.
- **Assuming prices are static** → providers change pricing; keep rates in config, not code.

---

## Interview trigger phrase

> "Cost is (input tokens × input price) + (output tokens × output price) per 1M; output is pricier because it's generated one token at a time, so I cap `max_tokens`, use prompt caching for the fixed prefix, batch non-urgent jobs at ~half price, and log `usage` per tenant/feature for budgets and alerts."

---

## Exercise

Given a feature: system prompt = 800 tokens, average user input = 200 tokens, average output = 400 tokens, 50,000 requests/day, model priced at $0.15/1M input and $0.60/1M output:

1. Compute the per-request and daily cost.
2. Recompute if prompt caching makes 700 of the 800 system-prompt tokens 90% cheaper.
3. Recompute if you move it to the Batch API at 50% off (no caching).
4. Which single change saves the most, and what UX trade-off does it carry?
