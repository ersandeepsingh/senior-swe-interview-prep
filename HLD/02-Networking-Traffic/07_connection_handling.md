# Connection Handling

> **Keep-alive** and **connection pooling** amortize TCP/TLS setup. **WebSockets** (and similar) are **long-lived stateful** connections — great for push, harder to load-balance and scale than request/response HTTP.

## Plain English

| Mechanism | What it solves | Risk if mis-tuned |
|-----------|----------------|-------------------|
| **HTTP keep-alive** | Reuse TCP/TLS across requests | Too many idle conns; FD exhaustion |
| **Client connection pool** | Cap concurrent conns to each upstream | Pool too small → latency; too big → thundering herd on restart |
| **Server timeouts** | Kill idle / stuck conns | Too aggressive → churn; too long → stuck capacity |
| **WebSocket / SSE** | Server push, bi-directional events | Sticky affinity; memory per connection; fan-out design |
| **HTTP/2 multiplexing** | Many streams on one conn | Head-of-line at app layer still possible; different pool math |

```text
  Short HTTP (pooled):
  Client ══╗
           ╠══ keep-alive / H2 ══► API ──► DB pool ──► Postgres
  Client ══╝

  WebSocket (pinned):
  Client ════════════════════════► WS gateway (holds socket)
                                      │
                                      ▼
                                 Redis pub/sub / presence
```

## Simple example

**Chat + REST hybrid** for a support desk:

```text
  REST  /api/tickets/*     → stateless API, HTTP/2 keep-alive, DB pool size ≈ (cores × 2)
  WS    /ws/agent/{id}     → connection gateway; registry agentId → node
  Agent reconnects         → reattach via registry; miss at-most offline buffer in Redis
```

Without pooling, every ticket list pays TLS handshake. Without a WS registry, scaling to N gateways needs sticky LB forever — and sticky dies when a node drains.

## Why prefer one over the other

| Prefer **request/response + pool** when… | Prefer **WebSocket** when… |
|------------------------------------------|----------------------------|
| CRUD, infrequent updates | Sub-second push, typing, live location |
| Easy horizontal scale | You accept stateful gateway tier |
| Intermittent clients | Persistent online presence matters |

| Large pools | Small / bounded pools |
|-------------|------------------------|
| Absorb bursts | Protect DB/FD limits; fail fast |

**Not “WebSockets everywhere.”** Polling or SSE can be enough; WS adds operational weight.

### Timeouts seniors actually set

| Timeout | Typical intent |
|---------|----------------|
| Idle keep-alive | Free FDs from abandoned clients |
| Request / read | Bound stuck upstreams |
| WS heartbeat / ping | Detect half-open sockets |
| Drain period on deploy | Finish in-flight, refuse new WS |

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Keep-alive / H2 | Lower handshake cost | Idle conn memory; need timeouts |
| Aggressive pooling to DB | Throughput | DB max_connections meltdown if every pod over-pools |
| Sticky WS only | Simple routing | Bad deploys / imbalance |
| WS + pub-sub mesh | Scale-out messaging | More moving parts; ordering caveats |
| Short idle timeouts | Free capacity | Reconnect storms |

## Interview trigger phrase

> “I’d **pool and keep-alive** the HTTP API aggressively, bound DB pools per pod, and isolate **WebSockets** on a gateway with a **presence registry** — not sticky-only — so we can drain nodes safely.”

## Exercise

**Design connections for a multiplayer lobby service.**

1. Lobby chat + matchmaking status: justify WS vs short polling for each.  
2. 50k concurrent sockets, 20 gateway pods — what state lives where, and how does a message reach a user on another pod?  
3. Postgres `max_connections=500`, 40 API pods — how do you size pools so you don’t lock yourself out?
