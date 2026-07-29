# Monitoring LLM Quality, Latency, Tokens, and Cost

> **One-line definition:** Observability for LLM systems means tracing every call with a trace id, model, tokens, latency, tool calls, and outcome — then watching latency percentiles, tokens/$ per request, and error/refusal rates, backed by offline evals on golden sets and online canaries so quality regressions and spend spikes are caught before users are.

---

## Plain English

A normal service is "healthy" when it's up and fast. An LLM service can be up, fast, cheap — and **quietly wrong**. The output is plausible-looking text, so a broken prompt or a model downgrade doesn't throw a 500; it just gives slightly worse answers that no dashboard catches. Meanwhile the *bill* can 10× overnight from one verbose prompt change.

So LLM monitoring has to cover four axes that don't all show up in ordinary APM:

1. **Latency** — it's slow and variable; you care about p95/p99 and time-to-first-token, not averages.
2. **Tokens** — the unit of both cost and context; the leading indicator of a spend problem.
3. **Cost** — real money per request; must be attributable per feature/tenant.
4. **Quality** — the hard one. Was the answer *good*? You can't compute this from logs alone, so you add **evals**.

The discipline: **log richly per call, aggregate into a few honest metrics, evaluate quality separately (offline + online), and alert on the things that hurt — spend, errors, and regressions.**

---

## Essentials

### What to log on every call (one structured record)

| Field | Why you need it |
|-------|-----------------|
| **trace_id / request_id** | Stitch multi-step agent calls into one story |
| **tenant / user / feature** | Attribute cost and quality; isolate a bad tenant |
| **model + version** | Detect silent provider changes; compare models |
| **prompt_tokens / completion_tokens** | Cost + context usage |
| **latency_ms + time_to_first_token** | UX and streaming health |
| **tool_calls** (name, args-hash, result status) | Agent behavior, loops, failures |
| **outcome** (success / invalid / refusal / fallback / error) | Reliability + quality signal |
| **cost_usd** (derived) | Spend tracking |
| **prompt/response ref** (redacted or hashed) | Debugging — store safely (see security module) |

> Log **outcome as a category**, not just success/fail. "Refusal" and "fell back to model B" are quality signals, not errors.

### Metrics that matter

| Metric | Definition | Watch for |
|--------|------------|-----------|
| **p50 / p95 / p99 latency** | Percentiles, not mean | Long tail from big contexts / slow model |
| **Time to first token** | Streaming responsiveness | Perceived slowness even if total time is fine |
| **Tokens / request** (in & out) | Avg + p95 | Prompt bloat, runaway outputs |
| **$ / request**, **$ / feature**, **$ / tenant** | Cost attribution | One feature/tenant dominating spend |
| **Error rate** | 4xx/5xx, timeouts | Provider issues, retry storms |
| **Refusal rate** | % outputs that are refusals | Over-cautious model, prompt regression |
| **Validation-failure rate** | % outputs failing schema | Prompt/model drift (ties to module 17) |
| **Fallback rate** | % served by fallback path | Primary model/provider degrading |

> **Averages lie.** A 2s mean latency can hide a 15s p99 that's ruining 1% of sessions. Alert on percentiles.

### Quality: offline evals + golden sets

You can't eyeball quality at scale, so you build a **golden set**: a fixed collection of inputs with known-good expected outputs (or graded rubrics).

| Eval type | How it scores | Good for |
|-----------|---------------|----------|
| **Exact / structured match** | Compare to expected field values | Extraction, classification |
| **Assertion / rule** | "Must contain order id", "must not mention competitors" | Guardrail-style checks |
| **Reference similarity** | Embedding/ROUGE vs reference answer | Summaries, paraphrase |
| **LLM-as-judge** | A model grades output against a rubric | Open-ended answers (use with care; validate the judge) |
| **Human review** | Sampled manual grading | Ground truth, spot checks |

Run the golden set **in CI** on every prompt/model change. A prompt edit is a code change — it needs a test.

### Online quality signals (in production)

| Signal | Meaning |
|--------|---------|
| Thumbs up/down, ratings | Direct user quality feedback |
| Re-ask / regenerate rate | Users unhappy with first answer |
| Escalation-to-human rate | Assistant failing at the task |
| Task completion / conversion | Did the flow actually work |
| Refusal / fallback / validation-failure trend | Creeping regression |

### Canaries, drift, and A/B

- **Online canary:** route a small % of traffic to a new model/prompt, compare metrics + evals before full rollout. Auto-rollback on regression.
- **Drift:** the model didn't change but the **inputs** did (new user phrasing, new doc types) → quality slips. Watch input distribution + quality metrics over time.
- **Model version drift:** providers update models silently. Pin versions where possible; alert when `model.version` changes.

### Alerting on spend (the one people forget)

| Alert | Trigger |
|-------|---------|
| **Spend rate** | $/hour exceeds budget slope (catches loops, prompt bloat) |
| **Token spike** | p95 tokens/request jumps |
| **Cost per tenant/feature** | One tenant runs away (abuse or bug) |
| **Fallback/error surge** | Provider degradation |
| **Refusal/validation-failure surge** | Quality regression |

> A cost alert on **rate of spend** catches an infinite agent loop in minutes; a monthly invoice catches it after you've lost thousands.

---

## Concrete example: one structured log line + derived metrics

```json
{
  "trace_id": "req_8f2c",
  "tenant": "acme",
  "feature": "support_assistant",
  "model": "gpt-4o-mini-2025-XX",
  "prompt_tokens": 1450,
  "completion_tokens": 220,
  "cost_usd": 0.00042,
  "latency_ms": 3120,
  "time_to_first_token_ms": 240,
  "tool_calls": [{"name": "get_order", "status": "ok"}],
  "outcome": "success"
}
```

From a stream of these you compute p95 latency, tokens/request, $/feature, refusal rate, and fallback rate — and you can replay any `trace_id` end to end when something looks wrong.

---

## When to use / trade-offs

- **Always** log the structured record and track cost — cheap insurance against silent spend/quality drift.
- **Golden-set evals in CI** the moment prompts/models are load-bearing.
- **Canaries** when you ship model/prompt changes to real users at scale.
- **LLM-as-judge** when you need scalable quality scoring but can tolerate some noise; validate the judge against human labels.
- Trade-offs: logging prompts/responses risks PII (redact — see module 18); evals cost tokens and maintenance; canaries add routing complexity. Match investment to blast radius.

---

## Pitfalls

- **Only watching uptime/latency.** You'll miss silent quality regressions entirely.
- **Averages instead of percentiles.** Hides the painful tail.
- **No cost attribution.** You see a big bill but not *which feature/tenant*.
- **No golden set.** Every prompt tweak is a blind gamble.
- **Trusting LLM-as-judge blindly.** The judge can be wrong/biased; calibrate it.
- **Logging raw PII.** Your observability stack becomes a compliance liability.
- **Ignoring model version pins.** A silent provider update quietly changes behavior.
- **Alerting on monthly cost only.** Alert on spend *rate* to catch loops fast.

---

## Interview trigger phrase

> "I emit one structured record per call — trace id, model+version, tokens, latency, tool calls, outcome, cost — then track latency percentiles, tokens and $ per request/feature/tenant, and error/refusal/fallback rates. Quality gets its own layer: golden-set evals in CI plus online canaries with auto-rollback, and I alert on spend *rate*, not the monthly invoice."

---

## Exercise

Your support assistant's user satisfaction quietly drops over two weeks, but latency, error rate, and uptime all look normal.

1. Which logged fields and metrics would you inspect first, and what would "silent quality regression" look like in them?
2. You suspect a provider silently updated the model. What single logged field confirms it, and what should have prevented the surprise?
3. Design a spend alert that would have caught a runaway agent loop within 10 minutes. What do you alert on, and why not just watch total monthly cost?
