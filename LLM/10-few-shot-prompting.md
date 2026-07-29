# 10 · Few-Shot Prompting

**One-line definition:** Few-shot prompting means putting a few worked **input→output examples** in the prompt so the model copies their format and behavior — teaching by demonstration, not by fine-tuning.

---

## Plain English

Instead of only *describing* what you want, you *show* it. You include a handful of example pairs ("here's an input, here's the ideal output") and then the real input. The model pattern-matches on your examples and mimics their style, format, and labeling — no training required.

- **Zero-shot:** just instructions, no examples.
- **One-shot:** one example.
- **Few-shot:** several examples (typically 2–8).

Few-shot is the fastest way to lock in a consistent output format or a nuanced labeling rule that's hard to express in words.

---

## Essentials

### Zero vs one vs few-shot

| Style | Examples | Best for | Trade-off |
|-------|----------|----------|-----------|
| **Zero-shot** | 0 | Simple, well-known tasks; capable models | Cheapest; may miss your exact format |
| **One-shot** | 1 | Show the format once | Cheap; one example may not cover edge cases |
| **Few-shot** | 2–8 | Nuanced formats, tricky edge cases, consistency | More input tokens every call |

### How examples steer format & behavior

The model imitates the **pattern** of your examples:

- **Format:** if examples output JSON, it outputs JSON; if they use a label set, it reuses it.
- **Tone/length:** short examples → short answers.
- **Decision boundary:** examples of tricky cases teach *where* to draw the line (e.g. what counts as "urgent").

### Example (few-shot classification)

```text
Classify the message sentiment as POSITIVE, NEGATIVE, or NEUTRAL.

Message: "This is the best purchase I've made all year!"
Sentiment: POSITIVE

Message: "It arrived broken and support ignored me."
Sentiment: NEGATIVE

Message: "The package was delivered on Tuesday."
Sentiment: NEUTRAL

Message: "{new_message}"
Sentiment:
```

The three examples nail the label set **and** the exact output shape (single word after `Sentiment:`), so the model won't ramble.

### Choosing & ordering examples

| Guideline | Why |
|-----------|-----|
| **Cover the label space / edge cases** | Model learns boundaries, not just the easy case |
| **Balance classes** | Skewed examples bias the output toward the majority label |
| **Use diverse, representative inputs** | Avoid overfitting to one phrasing |
| **Keep them correct** | A wrong example teaches the wrong behavior |
| **Order matters** | Models can be sensitive to example order; recency can bias — test it |
| **Match real distribution** | Examples should look like production inputs |

For hard tasks, **dynamic few-shot** (a.k.a. retrieval-based): pick the most similar examples to the current input at runtime (via embeddings) instead of a fixed static set.

### Token cost trade-off

Every example is **input tokens billed on every call**. 5 examples of 100 tokens = 500 extra prompt tokens per request, forever.

| Situation | Prefer |
|-----------|--------|
| Format learned in 1–2 examples | One/two-shot (cheaper) |
| High volume + fixed examples | Few-shot **+ prompt caching** the example prefix |
| Many examples needed for quality | Consider fine-tuning instead |

Put examples **before** the variable input so a fixed example prefix can be cached (see `07-token-usage-and-billing.md`).

### When fine-tuning beats many-shot

| Signal | Lean toward |
|--------|-------------|
| Need 2–8 examples, occasional task | **Few-shot** (no training, flexible) |
| Need 20+ examples to hit quality | **Fine-tuning** (bake it into weights) |
| Very high volume, examples dominate cost | **Fine-tuning** (shorter prompts → cheaper/faster) |
| Task/labels change often | **Few-shot** (edit prompt instantly) |
| Consistent style/format at scale | **Fine-tuning** |

Rule of thumb: if you're stuffing many examples into every prompt and paying for them millions of times, fine-tune — you move the "teaching" into the model so prompts get short.

---

## When to use / trade-offs

| Approach | Use when | Trade-off |
|----------|----------|-----------|
| Zero-shot | Capable model + clear task | Format may drift |
| Few-shot (static) | Need consistent format/edge cases | +input tokens every call |
| Few-shot (dynamic/retrieval) | Big, varied input space | Retrieval infra + latency |
| Fine-tuning | Many examples / very high volume / fixed behavior | Training cost, data prep, less flexible |

---

## Pitfalls

- **Too many examples** → high per-call cost and longer latency; diminishing returns.
- **Unbalanced examples** → model biases toward the over-represented label.
- **Incorrect/typo'd examples** → model faithfully copies your mistakes.
- **Format drift** → inconsistent example formatting teaches inconsistent output.
- **Examples after the variable input** → breaks prompt caching of the prefix.
- **Using few-shot when fine-tuning is cheaper** → paying for the same 20 examples on every request.
- **Ignoring order sensitivity** → shuffling examples can change results; test it.

---

## Interview trigger phrase

> "Few-shot puts a few input→output examples in the prompt so the model copies the format and decision boundary; I cover edge cases and balance classes, put the fixed examples first so they can be prompt-cached, and switch to fine-tuning once I'd need 20+ examples or the example tokens dominate cost at high volume."

---

## Exercise

You're building an endpoint that labels support tickets as `BILLING`, `TECHNICAL`, or `OTHER` and must return strict JSON `{"label": ...}`.

1. Write a 3-shot prompt (one example per label) that also forces JSON-only output.
2. Add one deliberately **tricky** example that sits near the BILLING/TECHNICAL boundary — explain what it teaches.
3. Estimate the extra input-token cost per call of your examples, and describe how prompt caching reduces it.
4. State the threshold (in # examples or volume) at which you'd stop few-shotting and fine-tune instead, with reasoning.
