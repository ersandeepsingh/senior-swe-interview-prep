# Prompts and Structured Outputs

> **One-line definition:** A **prompt** is the text you send an LLM; **message roles** (system / user / assistant) organize that text; and **structured outputs** force the model to reply in a machine-readable shape like JSON so your code can consume it reliably.

---

## Plain English

Talking to a chat model isn't one blob of text — it's a **list of messages**, each with a **role**. The `system` message sets the rules and persona, `user` messages are what the human says, and `assistant` messages are what the model said before. You resend this list every call (the model is stateless).

By default the model replies in free-form prose. That's fine for a chatbot, but terrible for code that needs to parse the answer. **Structured output** (JSON mode / schema-constrained decoding) makes the model return data that matches a shape you define — so you can `parse()` it instead of writing brittle regex.

---

## Essentials

### Message roles

| Role | Who | Purpose | Example |
|------|-----|---------|---------|
| `system` | You (developer) | Set behavior, rules, format, persona | "You are a support agent. Be concise. Never invent order IDs." |
| `user` | End user / your app | The actual request | "Where's my order #1234?" |
| `assistant` | The model | Its previous replies (kept for context) | "Your order shipped yesterday." |
| `tool` / `function` | Your code | Results returned from a tool call | `{"status": "shipped"}` |

Key idea: the **system** prompt is your control panel — instructions there carry more weight and persist across the conversation.

### Prompt = system + history + new user message

```text
[system]    rules, format, persona        (set once, high priority)
[user]      earlier question
[assistant] earlier answer
...
[user]      the new question               ← what you want answered now
```

### Structured outputs: the options

| Approach | How it works | Reliability | Notes |
|----------|--------------|-------------|-------|
| **Prompt-only** ("reply in JSON") | You just ask nicely | Low–medium | Model may add prose, markdown fences, or malformed JSON |
| **JSON mode** | Provider guarantees *valid* JSON | Medium–high | Valid JSON, but not necessarily *your* shape |
| **Schema-constrained** (JSON Schema / structured outputs) | Model output is constrained to match a schema you supply | High | Fields, types, and required keys enforced |
| **Tool/function calling** | Model fills arguments for a function signature | High | Great when the output *is* an action (see file 03 in Basics module) |

Prefer **schema-constrained** output whenever your code will parse the result.

### When to use structured output

- Your code needs to read specific fields (extraction, classification, routing).
- You're building an API where the response feeds another system.
- You want to avoid parsing free text with regex.

Use **free text** for human-facing chat, explanations, and creative writing.

---

## Simple example

```python
# Schema-constrained output: force the shape your code expects
schema = {
    "type": "object",
    "properties": {
        "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
        "urgent": {"type": "boolean"},
    },
    "required": ["sentiment", "urgent"],
}

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Classify the review. Return only the requested fields."},
        {"role": "user", "content": "This is broken and support ignored me for a week!"},
    ],
    response_format={"type": "json_schema", "json_schema": {"name": "review", "schema": schema}},
)

data = json.loads(resp.choices[0].message.content)
# data == {"sentiment": "negative", "urgent": True}  -> safe to use directly
```

---

## When to use / trade-offs

- **Structured output** = predictable, parseable, integrates cleanly — but slightly constrains the model and adds schema maintenance.
- **Free text** = flexible and natural — but fragile to parse and easy to break.
- **A strong system prompt** reduces surprises, but don't rely on it for security (users can try to override it; enforce rules in code too).

---

## Pitfalls

- **Parsing prose with regex.** Use JSON/schema mode instead.
- **Trusting "reply in JSON" alone.** Without a schema you may get markdown fences (```json …```) or extra commentary.
- **Overstuffing the system prompt.** Long, contradictory rules degrade following; keep it tight.
- **Assuming the system prompt is a security boundary.** Validate and authorize in your own code — prompt injection can override instructions.
- **Forgetting to resend history.** Roles/context must be passed every call.

---

## Interview trigger phrase

> "I structure calls as system/user/assistant messages, put behavior and format rules in the system prompt, and use schema-constrained JSON output whenever my code parses the result — never regex on free text, and never the system prompt as a security boundary."

---

## Exercise

You're building an endpoint that extracts `{name, email, company}` from a pasted email signature.
1. Which message role holds "always return these three fields, empty string if missing"?
2. Would you use free text, JSON mode, or schema-constrained output? Why?
3. Name one reason you'd still validate the model's JSON in your own code.
