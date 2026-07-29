# Output Validation, Retries, Fallbacks, and Guardrails

> **One-line definition:** Because the model is an untrusted probabilistic planner, you wrap every call in a validate → retry → fallback pipeline and gate both inputs and outputs with guardrails, so bad, unsafe, or malformed generations never reach your APIs or users.

---

## Plain English

The model will *usually* return what you asked for. "Usually" is not a contract. Sometimes it returns invalid JSON, an extra apology paragraph, a made-up enum value, a refusal, or something toxic. If your code assumes the happy path, it breaks in production the first busy afternoon.

The fix is to treat model output the way you'd treat **input from an untrusted client**: never trust it, always validate it. Around that core validation you build three concentric safety layers:

1. **Retries** — the same request failed transiently (network blip, `429`, or invalid output); try again, smartly.
2. **Fallbacks** — this approach keeps failing; switch to a different model, a simpler prompt, or a canned answer.
3. **Guardrails** — screen what goes *in* (moderation, allowlists) and what comes *out* (schema, safety, PII), and handle refusals as first-class outcomes.

The golden rule: **the model proposes, your validator disposes.** Nothing hits your trusted executor (APIs, DB, tools) until it has passed validation.

---

## Essentials

### The pipeline, in order

```text
input ─► input guardrails ─► LLM call ─► output validation ─► output guardrails ─► use it
                 │                │              │                    │
                 │ block          │ retry/       │ re-ask / retry     │ block / redact
                 ▼                ▼ fallback      ▼                    ▼
             reject request   backoff+retry   re-ask (N times)    safe fallback answer
```

### Output validation: what "valid" means

| Check | Example | If it fails |
|-------|---------|-------------|
| **Parseable** | Is it actually JSON? | Re-ask with the parse error |
| **Schema** | Right fields, types, enums | Re-ask, showing the schema |
| **Semantic** | `refund_amount <= order_total` | Re-ask or reject |
| **Grounded** | Cited doc actually exists | Drop the claim / re-ask |
| **Safe** | No PII leak, no toxic text | Redact or refuse |

> Prefer **structured outputs / JSON mode / function-calling schemas** if the provider offers them — the model is constrained at decode time, so you get far fewer parse failures. Still validate; constrained ≠ correct.

### Re-ask (self-correction) loop

When output is malformed, don't just retry blindly — tell the model *what was wrong* and ask again. This fixes far more cases than a plain retry.

```python
def call_validated(prompt, schema, max_tries=3):
    messages = [{"role": "user", "content": prompt}]
    for attempt in range(max_tries):
        raw = llm(messages)                    # the call
        ok, obj, err = validate(raw, schema)   # parse + schema + semantic
        if ok:
            return obj
        # feed the error back so the model can fix itself
        messages += [
            {"role": "assistant", "content": raw},
            {"role": "user", "content": f"Invalid: {err}. Return ONLY JSON matching the schema."},
        ]
    raise ValidationFailed()   # -> triggers fallback
```

### Retry vs re-ask vs fallback — don't confuse them

| Mechanism | Trigger | Same prompt? | Goal |
|-----------|---------|--------------|------|
| **Retry (backoff)** | `429`, 5xx, timeout, network | Yes | Survive a *transient* failure |
| **Re-ask** | Output invalid/refusal | No (adds the error) | Get a *correct* output |
| **Fallback** | Retries/re-asks exhausted | Different model/prompt/canned | Degrade gracefully, stay up |

### Retries done right

| Rule | Why |
|------|-----|
| **Exponential backoff + jitter** | Avoid synchronized retry storms |
| **Honor `retry-after`** | Provider tells you the wait |
| **Cap attempts** (2–3) | Bound cost and latency |
| **Only retry retryable errors** | Don't retry a `400 bad request` or content-policy block |
| **Idempotency key** | So a retried action isn't executed twice |

> **Idempotency is the subtle one.** If the model already called `create_refund` and the *response* timed out, a naive retry issues a **second refund**. Attach an idempotency key to every side-effecting tool call so the executor dedupes.

### Fallback ladder (cheapest degradation first)

| Level | Fallback | Result quality |
|-------|----------|----------------|
| 1 | Re-ask same model | Full |
| 2 | Simpler / stricter prompt (or JSON mode) | Full |
| 3 | Different model (other provider) | Usually full |
| 4 | Smaller/cheaper model | Slightly worse |
| 5 | Static template / cached answer / "human will follow up" | Degraded but real |

### Guardrails: input vs output

| | Input guardrails | Output guardrails |
|--|------------------|-------------------|
| Goal | Stop bad/unsafe/abusive requests early | Stop bad/unsafe/leaky responses |
| Techniques | Moderation API, allowlists, length/format checks, injection detection, per-tenant quotas | Schema validation, moderation, PII redaction, grounding check, allowlisted actions |
| Fail action | Reject with a clear message | Redact, re-ask, or fall back |

### Refusal handling

A refusal ("I can't help with that") is a **valid, expected output**, not an error. Detect it and route it:

- Legit safety refusal → show a helpful boundary message, don't retry into a loop.
- Spurious refusal (over-cautious) → re-ask with clarification once, then fall back.
- Never parse a refusal string as if it were your JSON.

---

## Concrete example: full pipeline for a "categorize ticket" endpoint

```python
def categorize_ticket(text):
    # 1. input guardrail
    if moderation(text).flagged:
        return safe_reject("This request can't be processed.")

    # 2. call + validate + re-ask (with backoff on transient errors)
    try:
        result = with_backoff(lambda: call_validated(
            prompt=build_prompt(text),
            schema=TICKET_SCHEMA,        # {category: enum, priority: enum, pii: bool}
            max_tries=3,
        ))
    except (ValidationFailed, ProviderError):
        # 3. fallback ladder
        result = call_validated(prompt=build_prompt(text), schema=TICKET_SCHEMA,
                                model=SECONDARY_MODEL, max_tries=1) \
                 if secondary_available() else {"category": "other", "priority": "normal"}

    # 4. output guardrail
    result = redact_pii(result)
    return result
```

The endpoint *always* returns a valid, safe object — even in the worst case it degrades to `{"category": "other"}` rather than throwing.

---

## When to use / trade-offs

- **Always validate** any output your code will parse or act on. Non-negotiable.
- **Add re-ask** when you need structured output and see occasional malformed responses.
- **Add fallbacks** when uptime matters more than always using the best model.
- **Full guardrails** when handling untrusted user input, regulated data, or public-facing surfaces.
- Trade-off: each layer adds latency and cost (extra calls). Cap attempts; don't build a 6-model fallback chain for an internal tool.

---

## Pitfalls

- **Trusting valid-looking JSON.** Schema-valid ≠ semantically correct. `refund_amount: 999999` parses fine.
- **Retrying non-idempotent side effects.** Double refunds, double emails. Use idempotency keys.
- **Retrying non-retryable errors.** Retrying a content-policy `400` just wastes money.
- **Infinite re-ask loops.** Always cap attempts and have a terminal fallback.
- **Treating refusals as crashes.** They're expected outputs; handle them.
- **Guardrails only on output.** Injection and abuse are cheaper to stop on input.
- **Regex-parsing free text.** Fragile. Use structured outputs and a real validator.

---

## Interview trigger phrase

> "I treat model output like untrusted client input: parse and schema-validate everything, re-ask with the error on invalid output, retry transient failures with backoff and idempotency keys, and fall back down a ladder to a cheaper model or a canned answer. Input and output both pass guardrails, and a refusal is a valid outcome I route — not an exception I crash on."

---

## Exercise

You have an endpoint that asks the model to extract `{amount, currency, account_id}` from an invoice and then calls `POST /transfers`.

1. The model returns `{"amount": "one thousand", "currency": "USD"}` (missing `account_id`, amount as words). List the validation checks that catch this and what your re-ask message says.
2. The transfer API call times out *after* the model requested it. Why is a blind retry dangerous, and what one field fixes it?
3. The primary model starts refusing every third request due to a content-policy false positive. Sketch your fallback ladder and where you cap attempts.
