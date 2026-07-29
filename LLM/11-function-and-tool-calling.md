# Function Calling / Tool Calling

> **One-line definition:** Tool calling is when the model outputs a structured “I want to call tool X with these args” proposal — your code validates auth, executes the real API, and feeds the result back into the next model turn.

---

## Plain English

The LLM cannot safely hit your database or charge a card. Instead you give it a **tool schema** (name, description, JSON parameters). When it needs real data or a side effect, it **proposes** a tool call. Your service is the gatekeeper: it checks who the user is, whether they’re allowed, runs the call, and returns a tool result. The model then continues with that evidence.

**Core rule:** the model proposes; your APIs enforce authz and execute.

```text
User → App → LLM (with tools)
              │
              ▼ proposes: get_order(order_id="123")
         Your code: authz + validate + call OrderService
              │
              ▼ tool result: {"status":"shipped",...}
         LLM → final answer to user
```

---

## Essentials

### Tool schema

| Field | Purpose | Example |
|-------|---------|---------|
| **name** | Stable identifier the model selects | `get_order` |
| **description** | When to use it (the model reads this) | “Fetch order status by ID for the current user” |
| **parameters** | JSON Schema for args | `{ "type":"object", "properties":{ "order_id":{"type":"string"} }, "required":["order_id"] }` |

Keep descriptions precise. Vague tools → wrong calls.

### The tool loop

| Step | Who | What |
|------|-----|------|
| 1 | You | Send messages + tool definitions to the model |
| 2 | Model | Either answers in text **or** returns `tool_calls` |
| 3 | You | Validate args, enforce authz, execute, append `role=tool` results |
| 4 | Model | Continues with results; may call more tools or finish |
| 5 | You | Cap iterations (e.g. max 5 loops) so it can’t spin forever |

### Read vs write tools

| Kind | Examples | Extra care |
|------|----------|------------|
| **Read** | get_order, search_docs, list_invoices | Still authz; prefer small payloads |
| **Write** | cancel_order, refund, create_ticket | Idempotency keys, confirmations, dry-run for high risk |

### Mapping tools to REST / gRPC

| Tool | Backend | Notes |
|------|---------|-------|
| `get_order` | `GET /orders/{id}` or `OrderService.Get` | Pass **server-side** user/tenant, not model-supplied |
| `cancel_order` | `POST /orders/{id}/cancel` | Same auth context as a normal API call |
| `search_kb` | internal search service | Truncate results before returning to the model |

### Never trust model-supplied identity

| Bad (model provides) | Good (your server injects) |
|----------------------|----------------------------|
| `user_id` in tool args | JWT / session → `ctx.UserID` |
| `tenant_id` from the prompt | Resolve from auth middleware |
| “as admin” in the description | Real RBAC on the API |

If the model can invent `user_id="admin"`, it will eventually try.

### Failure modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| **Infinite loops** | Same tool called repeatedly | Max iterations; detect duplicate calls |
| **Bad args** | Schema mismatch, wrong IDs | Strict JSON Schema validation; clear error strings back to model |
| **Over-calling** | Tools for every trivial step | Tighter descriptions; fewer tools |
| **Leaking writes** | Refund without intent | Separate write tools; human-in-the-loop for irreversible actions |

---

## Simple example

```python
# Pseudocode: one tool-loop turn
tools = [{
    "type": "function",
    "function": {
        "name": "get_order",
        "description": "Get order status for the authenticated user.",
        "parameters": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
}]

msg = client.chat.completions.create(model="...", messages=messages, tools=tools)
call = msg.choices[0].message.tool_calls[0]  # model proposes

# Your code — never take user_id from the model
args = json.loads(call.function.arguments)
order = order_svc.get(user_id=ctx.user_id, order_id=args["order_id"])  # authz inside

messages.append(msg.choices[0].message)
messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(order)})
final = client.chat.completions.create(model="...", messages=messages, tools=tools)
```

---

## When to use / trade-offs

- **Use tool calling** when the model needs live data or must trigger real actions through your existing APIs.
- **Prefer a single well-scoped tool** over a mega “do_anything” tool.
- **Trade-off:** more round-trips (latency + cost) vs richer, grounded answers. Cap loops and payload size.

---

## Pitfalls

- Letting the model supply identity or authorization claims.
- Exposing raw write APIs without idempotency or confirmation.
- Returning huge JSON blobs as tool results (burns tokens, confuses the model).
- No max-iteration guard → runaway tool loops.
- Mapping tools 1:1 to every endpoint — start with the 3–5 the agent actually needs.

---

## Interview trigger phrase

> “The model only *proposes* tool calls from a schema; my service validates arguments, enforces authz from the real session, executes against our APIs, and feeds results back — I never trust model-supplied identity.”

---

## Exercise

Design one read tool and one write tool for an order API (`GET /orders/{id}`, `POST /orders/{id}/cancel`).
1. Write the JSON schemas (name, description, parameters).
2. List what your server injects vs what the model may pass.
3. Name two failure modes for the cancel tool and how you’d stop them.
