# Feature Store & Model Serving

> Training is batch; **serving** needs **low-latency features + model inference**. A **feature store** shares definitions online/offline; **model serving** hosts the model behind a tight p99 budget.

## Plain English

ML in HLD interviews is rarely “train GPT.” It’s: **candidates → features → score → act**, under a latency budget, without training-serving skew.

| Piece | Job |
|-------|-----|
| **Offline features** | Point-in-time correct rows for training (warehouse/Spark) |
| **Online features** | Low-latency KV lookups at request time (Redis, Dynamo, Feast online) |
| **Model serving** | REST/gRPC / embedded model; batch vs real-time |
| **Model registry** | Versioned artifacts + rollout / rollback |

```text
  Training:  historical events → offline FS → train model → registry
  Serving:   request → online features (user/item) → model → score
                    │
                    └── log features + prediction for monitoring
```

## Simple example

“Recommend next video”: online features = user recent watches embedding, time-of-day, candidate video stats. Model (GBT or small neural net) scores 100 candidates in <20ms. Heavy ANN retrieval happens earlier; model only re-ranks.

```text
  Fraud @ checkout (<50ms):
    precomputed risk features (batch) + a few real-time signals
         → lightweight model
         → allow / challenge / block
```

**Training-serving skew:** if training used “clicks next hour” but serving can’t see the future, metrics lie. Feature store + point-in-time joins are the fix you name in interviews.

## Why prefer one over the other

| Prefer **online model service** when… | Prefer **batch scores** when… |
|---------------------------------------|-------------------------------|
| Personalization per request | Daily email / precompute top-N |
| Features change quickly | Stable catalog rankings |
| Latency budget allows | Huge candidate sets cheaper offline |

**Embedded vs remote model:** embed in process for lowest latency; remote for independent deploy / GPU. Trade ops vs p99.

**Shadow / canary** new models before full traffic; monitor prediction drift and business KPIs.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Shared feature store | Consistency train/serve | Platform investment |
| Real-time features | Fresh personalization | Infra cost, complexity |
| Huge deep model online | Quality ceiling | p99 / cost; need distillation |
| Batch-only scores | Simple & cheap | Stale personalization |

**Trap:** “We’ll call the Python notebook in the request path.” Seniors: **registry, versioned model, online FS, shadow/A/B, drift monitors**.

**Latency budget split (example 50ms):** 10ms feature fetch, 25ms inference, 15ms network/overhead — say the numbers so the design feels real.

**Fallback:** if model or FS is down, use heuristic score / last batch ranking rather than failing checkout or feed entirely.

## Interview trigger phrase

> “I’d retrieve candidates cheaply, join **online features from a feature store**, score with a **versioned model service**, and log features to catch training-serving skew.”

## Exercise

**Real-time fraud score on checkout (<50ms).**

1. Which features are online vs precomputed batch?
2. What happens when the feature Redis is down — degrade how?
3. One sentence on model rollback after a bad deploy.
