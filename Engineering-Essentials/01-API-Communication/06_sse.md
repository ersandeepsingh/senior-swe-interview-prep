# Server-Sent Events (SSE)

> One-way **server → client** stream of text events over a normal HTTP response that stays open.

## Plain English

The client opens a GET; the server keeps the response alive and writes `data: ...\n\n` chunks as events happen. The browser’s `EventSource` API reconnects automatically and can resume with `Last-Event-ID`.

## Essentials (must-know for this topic)

### Direction & connection model

| Trait | SSE |
|-------|-----|
| Direction | **Server → client only** |
| Transport | Normal HTTP (often GET), `Content-Type: text/event-stream` |
| Client → server | Separate REST/HTTP calls |
| Reconnect | Browser `EventSource` auto-reconnects; send `id:` for resume via `Last-Event-ID` |

### Wire format (vocab)

| Field | Meaning |
|-------|---------|
| `data:` | Payload (JSON text common); blank line ends the event |
| `event:` | Named event type (`status`, `token`) |
| `id:` | Last event id for resume |
| `retry:` | Reconnect delay hint (ms) |

### SSE vs WebSockets vs polling (this topic)

| | SSE | WebSockets | Polling |
|--|-----|------------|---------|
| Push | Yes (one-way) | Yes (two-way) | No (pull) |
| HTTP-friendly | High | Upgrade / special LB | Highest |
| Binary | Awkward (text) | Native frames | N/A |
| Browser limits | ~6 SSE per domain on HTTP/1.1 | Fewer hard limits | Request rate |

**When SSE wins:** LLM token streams, notification feeds, CI logs, progress bars — server push without duplex complexity.

## Why seniors get asked

SSE is the underrated answer for “live updates without WebSocket complexity” — LLM token streaming, notification feeds, progress bars.

## Simple example

```http
GET /api/v1/orders/42/events HTTP/1.1
Accept: text/event-stream

HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache

id: 1
event: status
data: {"status":"preparing"}

id: 2
event: status
data: {"status":"out_for_delivery"}
```

```javascript
const es = new EventSource("/api/v1/orders/42/events");
es.addEventListener("status", (e) => console.log(JSON.parse(e.data)));
```

## When to use / when not / trade-offs

| Use SSE when… | Prefer WebSockets when… |
|---------------|-------------------------|
| Server push only | Client must push often on same conn |
| You want HTTP/CDN/proxy friendliness | Binary frames or bidirectional protocol |
| Browser auto-reconnect is enough | You need custom framing beyond text |

**Trade-offs:** simpler than WebSockets; HTTP/1.1 browsers limit ~6 SSE conns per domain; some proxies buffer unless configured; less ideal for binary.

## Common pitfalls

- Proxy buffering (disable or flush correctly)
- Forgetting `id:` / resume semantics after disconnect
- Opening one SSE per tiny widget → connection exhaustion
- Using SSE where rare polling every 30s would do

## Interview trigger phrase

> “For one-way live updates I’d prefer SSE — simpler than WebSockets — and fall back to WebSockets only if we need bidirectional traffic.”

## Exercise

Compare SSE and short polling for a “CI build log” UI. When does SSE win on cost, and what’s one infra gotcha you’d check with the platform team?
