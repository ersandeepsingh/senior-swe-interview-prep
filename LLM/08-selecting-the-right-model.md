# 08 · Selecting the Right Model

**One-line definition:** Model selection is choosing the cheapest, fastest model that reliably clears your task's **quality bar** — proven by evals, not vibes.

---

## Plain English

There's no single "best" model — there's the best model *for this task at this budget and latency*. A tiny model is perfect for classifying support tickets; a frontier model is worth it for complex multi-step reasoning or code generation.

The trap is defaulting to the biggest model "to be safe." That's often 10–50× more expensive and slower than needed. The professional approach: define what "good enough" means, run a quick **eval** on real examples, and pick the smallest model that passes. Route hard cases up only when needed.

---

## Essentials

### Decision factors

| Factor | Question | Why it matters |
|--------|----------|----------------|
| **Quality** | Does it pass my eval on real data? | The whole point — everything else is a constraint |
| **Latency** | p95 response time acceptable? | Interactive UX needs speed; batch doesn't |
| **Cost** | $/1M in & out at my volume? | Dominates at scale |
| **Context length** | Does my input (docs/history) fit? | Long RAG/agents need big windows |
| **Tool/function calling** | Reliable structured tool use? | Required for agents |
| **Structured output** | JSON/schema mode support? | Needed for APIs downstream |
| **Privacy / hosting** | Can data leave my boundary? | Regulated data may need self-hosted/on-prem |
| **Multimodal** | Images/audio needed? | Not all models support it |
| **Availability** | Rate limits, region, SLA | Production reliability |

### Task → model mapping (illustrative)

| Task | Good fit | Why |
|------|----------|-----|
| Classification / routing / tagging | Small/cheap model | Simple, high volume, cost-sensitive |
| Extraction to JSON | Small–mid + structured output | Cheap, needs schema support |
| Summarization | Mid model, larger context | Balance quality/cost |
| RAG Q&A | Mid model + big context window | Fit retrieved chunks |
| Complex reasoning / planning | Frontier / reasoning model | Multi-step correctness matters |
| Code generation / refactor | Strong code model | Quality pays for itself |
| Agentic tool use | Model with reliable tool calling | Correct tool selection critical |
| Sensitive/regulated data | Self-hosted / on-prem model | Data can't leave boundary |

### Eval-before-commit

Never pick a model from a leaderboard alone — benchmarks ≠ your task. Build a small eval:

1. Collect **20–100 real examples** with expected outputs (or a grading rubric).
2. Run each candidate model.
3. Score with exact-match, JSON-schema validation, or an **LLM-as-judge** for open-ended tasks.
4. Compare **quality vs cost vs latency** in a table; pick the cheapest that clears the bar.
5. Re-run the eval when you change prompts or providers upgrade models (prevents silent regressions).

### Cascading / routing

Serve most traffic cheaply, escalate only hard cases.

```text
           ┌─────────────┐   pass (confident)
 request ─►│ small model │ ─────────────────► return
           └──────┬──────┘
                  │ low confidence / needs reasoning
                  ▼
           ┌─────────────┐
           │ big model   │ ──► return
           └─────────────┘
```

| Strategy | How it decides | Best for |
|----------|----------------|----------|
| **Cascade** | Try cheap first; escalate on low confidence/failed validation | Save cost on easy majority |
| **Router** | A classifier picks the model up front by task type/difficulty | Mixed workloads |
| **Fixed tier** | Hard-code model per feature | Simple, predictable |

Cascading works because most real traffic is easy — you pay frontier prices only on the hard tail.

---

## Example: choosing for "extract invoice fields to JSON"

- Needs: structured JSON output, low cost (high volume), moderate quality, small context.
- Candidates: a small model with JSON mode vs a mid model.
- Eval: run 50 real invoices, validate against schema, measure field accuracy.
- Result: small model hits 98% field accuracy at 1/10th the cost → **ship the small one**, route only schema-validation failures to the mid model.

---

## When to use / trade-offs

| Approach | Use when | Trade-off |
|----------|----------|-----------|
| Single small model | Simple, uniform task | May miss hard edge cases |
| Single frontier model | Low volume, high stakes | Expensive, slower |
| Cascade | High volume, mixed difficulty | Extra complexity + double cost on escalated calls |
| Router | Many distinct task types | Router itself can misroute |
| Self-hosted | Privacy/compliance, steady high volume | Ops burden, infra cost |

---

## Pitfalls

- **Defaulting to the biggest model** → paying 10–50× for no measurable quality gain.
- **Trusting leaderboards over your eval** → benchmark leader can lose on *your* data.
- **Ignoring context limits** → silent truncation of RAG context → wrong answers.
- **No re-eval after upgrades** → provider "improves" a model and your outputs quietly regress.
- **Cascade with a bad confidence signal** → escalates everything (no savings) or nothing (quality drop).
- **Forgetting tool-calling reliability** → an agent with a weak-tool model loops or picks wrong tools.

---

## Interview trigger phrase

> "I don't pick the 'best' model, I pick the cheapest/fastest one that clears the task's quality bar on a small real-data eval; for mixed traffic I cascade — a cheap model handles the easy majority and escalates only low-confidence cases to a frontier model — and I re-run evals on every model/prompt change."

---

## Exercise

You must build three features: (a) tag incoming support emails by topic, (b) answer questions over a 200-page policy PDF, (c) generate and run multi-step data-cleanup with tools.

1. For each, list the top 2 decision factors and pick a model *tier* (small / mid / frontier) with justification.
2. Design a 30-example eval for feature (a): what inputs, expected outputs, and scoring method?
3. Sketch a cascade for feature (b): what's the escalation signal, and how do you prevent it from escalating everything?
