# MCP (Model Context Protocol) Servers

> **One-line definition:** MCP is a standard protocol so hosts (Cursor, Claude Desktop, custom agents) can discover and call your tools, resources, and prompts the same way — without every host inventing a private plugin format.

---

## Plain English

In-app tool calling wires tools into *your* chat API. **MCP** does something complementary: it standardizes how an **external host** talks to a **server** that exposes capabilities.

Your MCP server says: “here are my tools / resources / prompts.” The host lists them, then calls them when the model needs them. Under the hood you still wrap **your real APIs** — MCP is the adapter layer, not a replacement for authz.

**Still true:** the LLM/host proposes; your APIs enforce authz and execute.

```text
Host (Cursor / Claude / agent)
        │  MCP: list tools, call tool, read resource
        ▼
MCP Server (thin adapter)
        │  normal SDK / HTTP / gRPC
        ▼
Your existing Order / Docs / Ticket APIs  ← authz lives here
```

---

## Essentials

### What MCP exposes

| Surface | What it is | Example |
|---------|------------|---------|
| **Tools** | Actions the model can invoke (with schema) | `get_order`, `create_ticket` |
| **Resources** | Readable context (files, docs, configs) | `orders://{id}`, policy markdown |
| **Prompts** | Reusable prompt templates | “triage bug”, “summarize PR” |

### Lifecycle (list → call)

| Phase | What happens |
|-------|----------------|
| **Connect** | Host starts/connects to the MCP server (stdio, HTTP, etc.) |
| **List** | Host asks for tools/resources/prompts; caches the catalog |
| **Call / Read** | Model needs something → host invokes `tools/call` or reads a resource |
| **Result** | Server returns structured content; host feeds it into the model context |
| **Disconnect** | Session ends; don’t leave open write side effects hanging |

### MCP vs in-app tool calling

| | **In-app tool calling** | **MCP server** |
|--|-------------------------|----------------|
| **Where it lives** | Inside your product’s backend | Separate process/service the host connects to |
| **Who is the host** | Your app | Cursor, Claude, or any MCP-capable client |
| **Reuse** | Tied to one product | Same server usable across hosts |
| **Authz** | Your session/JWT | Must map host identity → your auth carefully |
| **Best for** | End-user product agents | Dev tools, shared internal capabilities, IDE assistants |

### Features / benefits

| Benefit | Why it matters |
|---------|----------------|
| **Standard discovery** | Hosts auto-list tools; less custom glue |
| **Separation** | Tool implementation lives next to the system of record |
| **Composable** | Multiple MCP servers in one host session |
| **Resources + prompts** | Not only actions — also context and templates |

### Effective usage

| Practice | Why |
|----------|-----|
| **Thin adapter over existing APIs** | Don’t reimplement business logic in MCP |
| **Least privilege** | Only expose tools the host actually needs |
| **Small results** | Truncate / summarize; models choke on megabyte dumps |
| **Idempotent writes** | Retries from hosts are common |
| **Read / write split** | Safer defaults; require explicit write tools |
| **Auth at the API** | MCP transport ≠ permission; enforce on every call |

### When NOT to use MCP

| Situation | Prefer instead |
|-----------|----------------|
| Single product agent talking only to your backend | In-app tool calling |
| You need tight per-request product auth UX | First-party tools with your session |
| Ultra-low latency hot path | Direct SDK call, no extra hop |
| Tool is one-off and host-specific forever | Local function is fine |

---

## Simple example

```python
# Pseudocode: MCP tool handler as a thin adapter
@mcp.tool()
def get_order(order_id: str) -> dict:
    """Fetch order status for the authenticated tenant."""
    # Identity from MCP session / gateway — not from model args
    user = current_auth_context()
    return order_api.get(user_id=user.id, order_id=order_id)  # authz in order_api
```

Host flow: `list_tools` → model picks `get_order` → `call_tool` → your handler → result into context.

---

## When to use / trade-offs

- **Use MCP** when multiple hosts should share the same tools/resources, or you’re building IDE/agent integrations.
- **Use in-app tools** when the agent is embedded in your product and shares the user’s session natively.
- **Trade-off:** portability and standard discovery vs another process to secure, deploy, and observe.

---

## Pitfalls

- Rebuilding business rules inside the MCP server instead of calling existing APIs.
- Treating “connected over MCP” as authorization.
- Huge resource reads dumping entire databases into context.
- Non-idempotent writes that double-apply on host retries.
- Over-exposing admin tools “for convenience.”

---

## Interview trigger phrase

> “MCP standardizes how hosts discover and call tools/resources/prompts; I still implement a thin, least-privilege adapter over existing APIs — the protocol doesn’t replace my authorization layer.”

---

## Exercise

You already have `GET /orders/{id}` and `POST /tickets`.
1. Sketch two MCP tools as thin adapters (inputs/outputs only).
2. Fill the MCP vs in-app table for “customer support chatbot in our app” vs “Cursor plugin for on-call engineers.”
3. Name one reason you would *not* wrap a destructive `DELETE` as an MCP tool without extra controls.
