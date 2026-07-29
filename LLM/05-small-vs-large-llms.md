# Small vs Large LLMs

> **One-line definition:** Small LLMs are cheaper, faster, and can run close to (or on) the device but are less capable; large LLMs are more accurate and versatile but cost more and are slower — good systems **match the model to the task** and often mix both.

---

## Plain English

Bigger models generally reason better and handle harder, more open-ended tasks — but every request costs more and takes longer. Smaller models are cheap and fast, and often *good enough* for narrow, well-defined jobs like classification, extraction, or routing.

The senior-engineer instinct is not "always use the biggest model." It's: **use the smallest model that reliably passes your evals for this task**, and combine models when it helps (route easy work to small, escalate hard work to large).

---

## Essentials

### The core trade-off

| Dimension | Small LLM | Large LLM |
|-----------|-----------|-----------|
| **Cost per token** | Low | High |
| **Latency** | Fast | Slower |
| **Quality on hard tasks** | Lower | Higher |
| **Quality on narrow tasks** | Often equal | Overkill |
| **Deployment** | Can run on-device / self-host | Usually hosted API |
| **Context window** | Often smaller | Often larger |
| **Fine-tuning cost** | Cheap | Expensive |

### When small models win

- Well-defined, repetitive tasks: **classification, tagging, routing, extraction, simple rewriting**.
- **High volume** where cost multiplies fast.
- **Latency-sensitive** paths (autocomplete, real-time UX).
- **Privacy / offline** needs (on-device, no data leaves the machine).
- A **fine-tuned small model** on your narrow task can beat a general large one.

### When large models win

- Complex reasoning, multi-step planning, ambiguous instructions.
- Long-context synthesis across many documents.
- Broad general knowledge with fewer examples (better zero/few-shot).
- Tasks where a mistake is expensive and quality matters most.

### Routing and cascading

Instead of one model for everything, combine them:

| Pattern | How it works | Benefit |
|---------|--------------|---------|
| **Routing** | A classifier (often a small model) sends each request to the right-sized model | Pay for big only when needed |
| **Cascading** | Try small model first; if low quality/confidence, escalate to large | Cheap by default, accurate when required |
| **Fallback** | On error/timeout, drop to an alternate model | Reliability |

```text
request → [small model / classifier]
             ├─ easy?  → small model answers        (cheap, fast)
             └─ hard?  → escalate to large model     (accurate)
```

### On-device vs hosted

| | On-device / self-hosted small model | Hosted large model (API) |
|--|-------------------------------------|--------------------------|
| Data privacy | Data stays local | Data sent to provider |
| Latency | No network hop | Network + queue |
| Cost model | Upfront hardware / ops | Per-token, scales with use |
| Capability | Limited by device | State-of-the-art |
| Offline | Works offline | Needs connectivity |
| Ops burden | You manage it | Provider manages it |

---

## Simple example

```python
def answer(query):
    # Cascade: cheap first, escalate only if needed
    small = call_model("small-fast-model", query, temperature=0)
    if is_confident_and_complete(small):      # your own quality/eval check
        return small
    return call_model("large-strong-model", query, temperature=0)
```

---

## When to use / trade-offs

- **Start small, measure, then escalate.** Prove a small model *fails* your evals before paying for a large one.
- **Routing/cascading** cuts cost dramatically at scale but adds complexity and a routing-error risk.
- **On-device** wins on privacy/latency/offline but caps capability and adds ops.
- Don't optimize prematurely — for low volume, one good hosted model is simplest.

---

## Pitfalls

- **Defaulting to the biggest model** "to be safe" — burns money and latency for tasks a small model nails.
- **No evals.** Without a task-specific test set you can't tell if the small model is actually good enough.
- **Ignoring the routing model's own cost/errors.** A bad router can send everything to the expensive model anyway.
- **Underestimating on-device ops** (updates, hardware limits, memory).
- **Comparing models on vibes** instead of your real workload.

---

## Interview trigger phrase

> "I match the model to the task: smallest model that passes my evals, then route or cascade so easy requests go to a cheap/fast model and only hard ones escalate to a large one — and I reach for on-device small models when privacy, latency, or offline matter more than peak capability."

---

## Exercise

You run a support system: 90% of tickets are simple FAQs, 10% are complex multi-account billing disputes.
1. Which model size fits each bucket?
2. Sketch a routing or cascading design for this traffic in 2–3 lines.
3. Give one metric you'd track to decide whether the small model is "good enough."
