# Fine-Tuning vs Prompting vs RAG

> **One-line definition:** Prompting steers behavior with instructions in the request; RAG injects external facts at query time; fine-tuning changes model weights so a style or task pattern becomes the default — pick by *what* you need to change.

---

## Plain English

Three levers, three jobs:

- **Prompting** — tell the model *how* to behave *this call* (system prompt, few-shot examples, output schema). Fastest to iterate.
- **RAG** — give the model *which facts* to use *this call* by retrieving documents. Best for private/fresh knowledge.
- **Fine-tuning** — train on examples so the model *internalizes* a format, tone, or specialized behavior. Slowest and costliest; doesn’t magically add reliable new facts.

None of these replace your APIs. If an action must happen, the model still proposes; your services authorize and execute.

```text
Need fresh/private facts?     → RAG
Need format/tone/task habit?  → fine-tune (or strong prompting first)
Need quick iteration / rules? → prompting
Often: prompt + RAG (+ tools); fine-tune only when prompting plateaus
```

---

## Essentials

### What each changes

| Approach | What changes | What stays the same |
|----------|--------------|---------------------|
| **Prompting** | Instructions & examples in context | Model weights |
| **RAG** | Context window contents (retrieved docs) | Model weights |
| **Fine-tuning** | Model weights (adapter or full) | Your docs still need a retrieval story if they change |

### Decision table

| Goal | Prefer | Why |
|------|--------|-----|
| **Facts** (policies, product data, tickets) | **RAG** | Knowledge moves; don’t bake it into weights |
| **Format / behavior** (always JSON shape, brand voice, domain jargon) | **Fine-tune** (after prompting fails) | Consistency without huge prompts |
| **Quick iteration** (new rules weekly) | **Prompting** | Change text, redeploy prompt, done |
| **Live actions** (cancel order, refund) | **Tools / APIs** | Authz + execution outside the model |
| **Exact lookups** (balance, inventory) | **API / DB**, not RAG or fine-tune | Deterministic source of truth |

### Cost / effort

| | Prompting | RAG | Fine-tuning |
|--|-----------|-----|-------------|
| **Time to first version** | Hours | Days (ingest + eval) | Days–weeks (data + train + eval) |
| **Ongoing cost** | Tokens per call | Embed + store + retrieve + tokens | Training runs + hosting specialized model |
| **Update story** | Edit prompt | Re-index docs | Collect new data, retrain |
| **Ops burden** | Low | Medium (index freshness, ACL) | High (datasets, evals, drift) |

### Combining them

| Stack | Role of each |
|-------|----------------|
| Prompt + RAG | Prompt = behavior; RAG = facts |
| Prompt + tools | Prompt = when to call; tools = real I/O |
| Fine-tune + RAG | Fine-tune = style/schema; RAG = current knowledge |
| Fine-tune + tools | Fine-tune = reliable tool-calling patterns; APIs still enforce authz |

Anti-pattern: fine-tune on yesterday’s FAQ and skip RAG — answers go stale.

### When fine-tuning is justified

| Signal | Meaning |
|--------|---------|
| Prompting + few-shot is long, brittle, or inconsistent at scale | Behavior belongs in weights |
| You have **thousands** of high-quality input/output examples | Enough signal to learn |
| Latency/cost of giant prompts hurts | Shorter prompts after tune |
| Domain format is strict (medical note structure, internal DSL) | Consistency matters more than factual novelty |
| Facts change often | **Not** a fine-tune justification — use RAG |

Always eval before/after. Fine-tuning without a gold set is hope, not engineering.

---

## Simple example

```text
Task: "Answer employee handbook questions in our HR tone, cite the policy."

1. Prompting: system = "Be concise, HR tone, refuse legal advice."
2. RAG: retrieve handbook chunks with ACL; put in CONTEXT.
3. Fine-tune?: only if tone/format still drifts after good prompts + few-shots.
4. Tools: "file_leave_request" → your HR API (authz), not the handbook text.
```

```python
# Prefer compose, don't jump to fine-tune
answer = llm.chat(
    system=HR_STYLE_PROMPT,           # prompting
    user=f"CONTEXT:\n{rag(user, q)}\n\nQ: {q}",  # RAG
)
# later, if needed: model="ft:hr-style-v3"  # fine-tune for style only
```

---

## When to use / trade-offs

- **Start with prompting.** Add RAG when answers need your documents. Add tools when answers need real actions. Fine-tune last.
- **Trade-off:** fine-tuning can improve consistency but freezes behavior, costs data/ops, and is a poor store of changing facts.
- **Senior default:** RAG for knowledge, prompts for policy, fine-tune for stubborn style/format, APIs for side effects.

---

## Pitfalls

- Fine-tuning to “teach facts” that will change next sprint.
- Skipping evals — you can’t tell if the tune helped.
- Huge prompts that should have been RAG or a tool call.
- Assuming fine-tuning replaces authorization or business rules.
- Combining all three without measuring — complexity without gain.

---

## Interview trigger phrase

> “Facts go to RAG, quick behavior changes go to prompting, fine-tuning is for durable format/style when prompting plateaus — and side effects still go through APIs that enforce authz.”

---

## Exercise

Pick one product task: (A) answer from a changing policy PDF, (B) always emit a fixed JSON ticket schema, (C) refund an order.
1. Map A/B/C to RAG, prompting/fine-tune, and tools.
2. For B, write the condition under which you’d fine-tune instead of few-shot prompting.
3. In one sentence, explain why fine-tuning does not remove the need for authz on C.
