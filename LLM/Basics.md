# LLM Integration Learning Module

A practical path for **wiring LLMs into your application APIs** — from how models work, through prompting and tool calling, to MCP, RAG, scale, security, and production design.

---

## Learning path

| # | Topic | File |
|---|--------|------|
| 1 | What an LLM is and how it works | [01-what-is-an-llm.md](01-what-is-an-llm.md) |
| 2 | Tokens, context windows, input & output tokens | [02-tokens-and-context-windows.md](02-tokens-and-context-windows.md) |
| 3 | Prompts, system/user prompts, structured outputs | [03-prompts-and-structured-outputs.md](03-prompts-and-structured-outputs.md) |
| 4 | Temperature, hallucinations, confidence & limitations | [04-temperature-hallucinations-limitations.md](04-temperature-hallucinations-limitations.md) |
| 5 | Small LLMs versus large LLMs | [05-small-vs-large-llms.md](05-small-vs-large-llms.md) |
| 6 | Calling LLMs from Python and Go | [06-calling-llms-python-go.md](06-calling-llms-python-go.md) |
| 7 | Token usage and billing | [07-token-usage-and-billing.md](07-token-usage-and-billing.md) |
| 8 | Selecting the right model for a task | [08-selecting-the-right-model.md](08-selecting-the-right-model.md) |
| 9 | Prompt engineering techniques | [09-prompt-engineering-techniques.md](09-prompt-engineering-techniques.md) |
| 10 | Few-shot prompting and examples | [10-few-shot-prompting.md](10-few-shot-prompting.md) |
| 11 | Function calling and tool calling | [11-function-and-tool-calling.md](11-function-and-tool-calling.md) |
| 12 | MCP servers and how LLMs use MCP tools | [12-mcp-servers.md](12-mcp-servers.md) |
| 13 | RAG, embeddings, and vector databases | [13-rag-embeddings-vector-databases.md](13-rag-embeddings-vector-databases.md) |
| 14 | Fine-tuning vs prompting vs RAG | [14-fine-tuning-vs-prompting-vs-rag.md](14-fine-tuning-vs-prompting-vs-rag.md) |
| 15 | Caching, batching, and reducing token costs | [15-caching-batching-cost-reduction.md](15-caching-batching-cost-reduction.md) |
| 16 | Handling millions of requests efficiently | [16-handling-millions-of-requests.md](16-handling-millions-of-requests.md) |
| 17 | Output validation, retries, fallbacks & guardrails | [17-validation-retries-fallbacks-guardrails.md](17-validation-retries-fallbacks-guardrails.md) |
| 18 | Security, privacy, prompt injection & data leakage | [18-security-privacy-prompt-injection.md](18-security-privacy-prompt-injection.md) |
| 19 | Monitoring quality, latency, tokens & cost | [19-monitoring-quality-latency-cost.md](19-monitoring-quality-latency-cost.md) |
| 20 | Designing a production-ready LLM system | [20-designing-production-llm-system.md](20-designing-production-llm-system.md) |

**Suggested order:** 1 → 20 in sequence. Don’t jump to MCP (12) before tool calling (11), or to production (20) before security (18) and monitoring (19).

---

## What you will be able to explain after this

1. What an LLM actually does (next-token prediction) and what it does *not* do  
2. How tokens, context windows, and billing connect — and how to control spend  
3. How to call models from Python and Go, pick a model, and engineer prompts  
4. How tool calling and MCP map to *your* APIs (model proposes; you execute)  
5. When to use prompting vs RAG vs fine-tuning  
6. How to run LLM features at scale with validation, security, and observability  

---

## Big picture (one diagram)

```text
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  Your App   │────►│  LLM Provider    │◄────│  Tools / MCP / RAG  │
│  (API/UI)   │     │  (Chat / Agents) │     │  (your APIs, DBs,   │
│             │◄────│                  │────►│   docs, Slack…)     │
└─────────────┘     └──────────────────┘     └─────────────────────┘
   prompts in            tokens in/out              side effects
   answers out           = $ cost                   = real actions
```

- **LLM** reasons and generates text (and tool-call decisions).  
- **Your APIs** remain the source of truth for business actions.  
- **MCP / tools / RAG** feed context and capabilities — never replace authz.

---

## Interview / design one-liners

> “An LLM is next-token prediction at scale — useful as a planner, never as a trusted source of truth or authz.”

> “Tokens are the billing and context unit. Cost ≈ (input + output tokens) × price; context window caps what you can send.”

> “I never let the model hit production DBs directly — it proposes tool calls; my service validates auth and executes.”

> “Facts → RAG. Format/behavior → fine-tune (rarely). Quick iteration → prompting.”

> “Production LLM system = normal distributed system + an untrusted probabilistic component: gateway, validate, least privilege, evals, cost budgets.”

---

## How to study

1. Read one module; rewrite its diagram or decision table from memory.  
2. For modules 11–12: sketch an “order status” tool as REST vs MCP.  
3. For modules 13–14: pick one product feature and choose prompt / RAG / fine-tune.  
4. End with modules 17–20 checklists before any real integration.
