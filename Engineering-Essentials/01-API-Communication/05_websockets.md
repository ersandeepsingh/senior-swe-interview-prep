# WebSockets

> A long-lived, **full-duplex** TCP connection upgraded from HTTP — both client and server can push messages anytime.

## Plain English

Normal HTTP is request → response → done. WebSockets start with an HTTP upgrade, then stay open. Chat, multiplayer games, collaborative cursors, and live dashboards use them because either side can send without waiting for a poll.

## Essentials (must-know for this topic)

### WebSockets vs SSE vs polling

| | **WebSockets** | **SSE** | **Short / long poll** |
|--|----------------|---------|------------------------|
| **Direction** | Full duplex (both ways) | Server → client only | Client asks; server answers |
| **Connection** | Long-lived after HTTP upgrade | Long-lived HTTP response | Repeated HTTP requests |
| **Client → server** | Same socket | Separate normal HTTP | Each poll request |
| **Best for** | Chat, games, collab | Feeds, LLM tokens, progress | Fallback / simple infra |
| **Scale pain** | Stateful conns, sticky/fan-out | Conn limits, proxy buffering | Request volume / worker hold time |

### Connection model (what to say in interviews)

1. Client sends HTTP request with `Upgrade: websocket`
2. Server responds `101 Switching Protocols`
3. Connection stays open; frames go both ways
4. Need **heartbeat/ping**, **reconnect + backoff**, and usually a **pub/sub backplane** (Redis/Kafka) so any node can reach any client

### Stateful scaling checklist

| Concern | Why |
|---------|-----|
| Sticky sessions / shared pub-sub | Connection lives on one node |
| Auth on upgrade | Don’t trust later messages alone |
| Heartbeats | Detect half-open sockets |
| Backpressure | Slow clients → buffer blowups |

## Why seniors get asked

Realtime features are common in system design. Interviewers want “WebSockets vs polling vs SSE” plus how you’d scale thousands of open sockets.

## Simple example

```http
GET /ws/orders HTTP/1.1
Host: api.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

```javascript
const ws = new WebSocket("wss://api.example.com/ws/orders");
ws.onmessage = (e) => console.log("update", JSON.parse(e.data));
ws.send(JSON.stringify({ action: "subscribe", orderId: "42" }));
```

## When to use / when not / trade-offs

| Use WebSockets when… | Prefer SSE / polling when… |
|----------------------|----------------------------|
| Bidirectional messages (chat, games) | Server → client only (feeds, tokens) |
| Low-latency interactive UX | Simple infra, HTTP-friendly proxies |
| You can invest in conn management | Occasional updates; polling is enough |

**Trade-offs:** great UX latency; worse fit for serverless (idle connections), some proxies, and horizontally scaling without a pub/sub backplane (Redis, Kafka, etc.).

## Common pitfalls

- No heartbeat → silent half-open connections
- Holding business state only in memory on one node
- Forgetting auth on the upgrade request
- Using WebSockets for rare updates (overkill vs SSE/poll)

## Interview trigger phrase

> “I’d use WebSockets for bidirectional realtime, back them with pub/sub for fan-out, and design reconnect + heartbeat explicitly.”

## Exercise

Design live order tracking for a food-delivery app. Argue WebSockets vs SSE in two sentences, and name one component you’d add so any server instance can push to any client.
