# Stateless vs Stateful Services

> **Stateless** services don’t remember the client between requests — they push session/data to shared stores. That makes **horizontal scaling and failover** easy. **Stateful** services keep important memory on the node (connections, local cache, leader role).

## Plain English

| | Stateless | Stateful |
|---|-----------|----------|
| Request handling | Any instance can serve any user | Often needs the *same* instance (affinity) |
| Restart | Lose almost nothing local | May lose sessions / buffers / leadership |
| Scale-out | Add boxes behind LB — done | Rebalance state, sticky sessions, or careful protocols |

```text
  Stateless app tier                    Stateful connection tier
  ┌────┐ ┌────┐ ┌────┐                 ┌──────────────────┐
  │ A  │ │ B  │ │ C  │                 │ Chat server holds │
  └──┬─┘ └──┬─┘ └──┬─┘                 │ WebSocket to user │
     └──────┼──────┘                   └─────────┬────────┘
            ▼                                    ▼
     Shared Redis / DB                    Harder to LB freely
     (session, cart, cache)               (sticky or conn gateway)
```

## Simple example: shopping cart

**Stateful (bad default for scale):**

```text
  User → App-3 (cart stored in App-3 memory)
  Next request → App-7  → cart empty 💥
```

Fix with sticky sessions → then App-3 dies → carts vanish. Still fragile.

**Stateless (preferred):**

```text
  User → any App  →  Redis/DB key cart:{userId}
  Any instance works; scaling and deploys are boring (good).
```

### Where statefulness is unavoidable

| System | Why state lives on the node |
|--------|-----------------------------|
| WebSocket chat | Long-lived connection pinned to a server |
| Game room | In-memory simulation tick |
| Kafka broker | Partition data on disk for that broker |
| DB primary | Authoritative durable state |

Even then, seniors **isolate** stateful tiers and keep the HTTP API tier as stateless as possible.

## Diagram: request path

```text
  Client
    │
    ▼
  Load balancer  ──►  Stateless API (many replicas)
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       Redis         Postgres       Object store
      (session)     (durable)        (media)
```

## Why prefer stateless for the app tier

| Prefer **stateless APIs** because… | Keep **stateful** components when… |
|------------------------------------|------------------------------------|
| Autoscale, rolling deploys, no sticky sticky hacks | Protocol needs affinity (WS, streams) |
| Failover is “route elsewhere” | Durability requires local disk (brokers, DBs) |
| Interview designs stay clean | You’ve consciously limited which tier is stateful |

**Why not “store everything in the app process”?** You can’t scale out cleanly; deploys drop user state; load balancers become sticky nightmares.

**Why not “make everything stateless including the DB”?** Durable truth must live *somewhere*. Stateless means *app servers* don’t own it — stores do.

## Trade-offs

| Approach | Upside | Downside |
|----------|--------|----------|
| Stateless + shared store | Easy scale/failover | Extra network hop; store becomes critical dependency |
| Sticky sessions | Quick patch for legacy in-memory state | Uneven load; painful deploys; failover loses affinity |
| Stateful real-time servers | Low-latency local fan-out | Need presence/routing layer (“which node holds user X?”) |
| Local caches on app nodes | Faster reads | Inconsistency across nodes; need invalidation |

## Interview trigger phrase

> “I’d keep the API tier **stateless** — sessions and carts in Redis — so we can scale horizontally. WebSocket chat stays **stateful**, so I’d add a connection registry to find which node owns a user.”

## Exercise

**Design a collaborative whiteboard.**

1. Mark each component as mostly stateless or stateful: HTTPS REST API, WebSocket gateway, Redis presence, Postgres document store.  
2. User reconnects after a phone blip — where does “current stroke buffer” live, and what do you lose if that node dies?  
3. Say how you’d scale from 1 WebSocket server to 20 without sticky-only chaos (hint: routing / registry / pub-sub between nodes).
