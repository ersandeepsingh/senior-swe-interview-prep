# Temperature, Hallucinations, and Limitations

> **One-line definition:** Sampling settings like **temperature** and **top_p** control how random the model's word choices are; **hallucinations** are confident-sounding but false outputs; and knowing the model's built-in limits (no true confidence, knowledge cutoff, non-determinism) is key to using it safely.

---

## Plain English

Remember the model outputs a *probability* for every possible next token. **Sampling** is how it turns those probabilities into an actual choice.

- **Low temperature** → it almost always picks the most likely token → focused, repeatable, "boring."
- **High temperature** → it takes more chances on less likely tokens → creative, varied, riskier.

Because the model always produces *some* plausible continuation, it will sometimes generate a fluent, confident answer that is simply **wrong** — a **hallucination**. It has no internal "I'm not sure" signal you can trust, and no knowledge of events after its **cutoff** date. Your job is to design around these facts.

---

## Essentials

### Sampling controls

| Setting | Range (typical) | Low value | High value |
|---------|-----------------|-----------|------------|
| **temperature** | 0–2 | Deterministic-ish, safe, repetitive | Creative, diverse, more errors |
| **top_p** (nucleus) | 0–1 | Only most-likely tokens considered | Wider pool of tokens allowed |

Both narrow or widen the pool of candidate tokens. **Tune one, not both.** For extraction/classification/code, use **low temperature** (e.g. 0–0.3). For brainstorming/marketing copy, go higher (0.7–1.0).

### Why hallucinations happen

| Cause | Explanation |
|-------|-------------|
| It optimizes plausibility, not truth | Trained to produce likely text, not verified facts |
| Gaps in training data | Fills unknowns with confident guesses |
| No live knowledge | Can't check anything unless you give it tools/data |
| Ambiguous prompt | Vague questions invite invented specifics |
| Pressure to answer | It rarely says "I don't know" unless told it may |

### "Confidence" is not what you think

The model can output token probabilities, but a high probability means "this text is *likely*," **not** "this fact is *true*." A model can be 99% confident in a wrong answer. Don't treat fluency or certainty of tone as accuracy.

### Knowledge cutoff & non-determinism

- **Knowledge cutoff:** the model only "knows" data up to its training date. Anything newer must be supplied by you (RAG/tools).
- **Non-determinism:** with temperature > 0, the same prompt can yield different answers. Even at temperature 0, exact reproducibility isn't guaranteed across time/hardware.

### Limitations at a glance

| Limitation | Consequence | Mitigation |
|------------|-------------|------------|
| Hallucination | Confident false facts | Ground with RAG; cite sources; verify critical claims |
| No true confidence | Can't trust "I'm sure" | Cross-check; use validators/tools |
| Knowledge cutoff | Stale/wrong on recent events | Provide fresh data via retrieval/tools |
| Non-determinism | Flaky, hard to test | Low temperature; seeds if supported; eval sets |
| Weak exact math/counting | Arithmetic errors | Offload to a calculator/code tool |
| Prompt injection | Instructions hijacked | Authorize in code; sanitize untrusted input |

---

## Simple example

```python
# Deterministic-ish extraction: keep it boring and repeatable
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    temperature=0,                      # minimize randomness for structured tasks
    messages=[
        {"role": "system", "content": "Extract the invoice total. If not present, reply 'UNKNOWN'."},
        {"role": "user", "content": invoice_text},
    ],
)
# Telling it that "UNKNOWN" is allowed reduces the urge to hallucinate a number.
```

---

## When to use / trade-offs

- **temperature 0–0.3:** classification, extraction, code, anything you'll parse or must reproduce.
- **temperature 0.7–1.0:** ideation, varied phrasing, creative drafts.
- **Grounding (RAG/tools)** cuts hallucinations for factual tasks — at the cost of extra infrastructure and latency.
- **Explicitly allowing "I don't know"** trades a bit of helpfulness for far fewer fabrications.

---

## Pitfalls

- **High temperature on structured tasks.** Adds noise and parsing failures for no benefit.
- **Trusting confident tone.** Fluency ≠ correctness.
- **Asking about recent events** without supplying data (cutoff!).
- **Expecting reproducible outputs** in tests without pinning temperature (and even then, allow variance).
- **Letting the model do exact math** instead of calling a tool.

---

## Interview trigger phrase

> "Temperature/top_p control randomness — I keep them low for anything parseable. Hallucinations come from optimizing plausibility over truth, and the model has no trustworthy confidence signal, so for factual work I ground it with retrieval, allow 'I don't know', and verify critical outputs rather than trusting a confident tone."

---

## Exercise

Your app answers questions about *this week's* internal sales numbers using an LLM.
1. What temperature would you set and why?
2. Name the two limitations most likely to cause a wrong answer here.
3. Describe one design change that fixes each of those two limitations.
