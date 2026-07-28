# API Gateways & BFF

> A **gateway** is the shared front door (auth, routing, rate limits). A **BFF** (Backend-for-Frontend) is a tailored API layer for one client type (web, iOS, Android).

## Plain English

Clients shouldn’t talk to 15 microservices directly. An **API gateway** terminates TLS, checks tokens, applies rate limits, and routes `/orders` to the order service. A **BFF** goes further: payloads shaped for one client’s screens. Gateways are cross-cutting; BFFs are product-shaped.

```
Mobile App → Mobile BFF → [Order, User, Catalog services]
Web App    → Web BFF    ↗
Partners   → API Gateway → public REST services
```

## Essentials (must-know for this topic)

### Gateway vs BFF vs direct calls

| Layer | Job | Owns domain logic? |
|-------|-----|--------------------|
| **API Gateway** | TLS, authn, rate limit, WAF, routing, request IDs | **No** — cross-cutting only |
| **BFF** | Aggregate/trim/reshape for one client type | Light orchestration; still not core domain |
| **Services** | Business rules, persistence | **Yes** |
| **Smart client → many services** | Client fan-out | Avoid at scale (chatty, auth sprawl) |

### What belongs at the edge (gateway)

| Concern | Why at gateway |
|---------|----------------|
| Authn / JWT validation | One place to enforce |
| Rate limits / quotas | Protect backends |
| TLS termination | Cert management |
| Routing / canary | Traffic control |
| Correlation IDs | Observability from first hop |

### What belongs in a BFF

| Concern | Example |
|---------|---------|
| Aggregation | Home = profile + 5 orders + unread |
| Payload shaping | Mobile-sized fields vs web-rich |
| Protocol adapt | gRPC internally → JSON to app |

### Anti-patterns

| Anti-pattern | Problem |
|--------------|---------|
| **God gateway** | All business rules in gateway configs |
| **One mega-BFF** for every client | Defeats client-specific purpose |
| **BFF per screen** | Explosion of near-duplicate services |

## Why seniors get asked

Microservices designs always need an edge. Seniors distinguish gateway vs BFF vs “smart clients calling everything,” and know what belongs at the edge (auth, not business rules).

## Simple example

Gateway config sketch:

```yaml
routes:
  - path: /api/v1/orders/**
    service: order-svc
    auth: required
    rate_limit: 100/min/key
```

BFF aggregation pseudocode:

```python
def mobile_home(user_id):
    orders, recs = parallel(
        order_svc.recent(user_id, limit=5),
        reco_svc.for_user(user_id, limit=10),
    )
    return {"orders": slim(orders), "recs": slim(recs)}  # mobile-sized
```

## When to use / when not / trade-offs

| Use gateway when… | Use BFF when… |
|-------------------|---------------|
| Many services need one public edge | Web vs mobile need different shapes |
| Central auth, quotas, WAF | You’d otherwise over-fetch via generic GraphQL/REST |
| Partner API at a stable hostname | Client-specific orchestration / aggregation |

**Avoid:** putting all domain logic in the gateway (“god gateway”). **Avoid:** a BFF per tiny screen that duplicates forever.

**Trade-offs:** gateways add hop latency but simplify clients; BFFs speed mobile UX but mean more backend surfaces to own.

## Common pitfalls

- Business rules living only in the gateway
- One mega-BFF shared by all clients (defeats the point)
- No timeouts/retries to downstream → cascading failures
- Skipping correlation IDs at the edge

## Interview trigger phrase

> “I’d put cross-cutting concerns in an API gateway, and use BFFs when web and mobile need different aggregations — keep domain logic in services.”

## Exercise

A mobile app needs home feed = profile + 5 orders + unread count. Sketch gateway vs BFF responsibilities. Who calls the three services, and what does the gateway still do?
