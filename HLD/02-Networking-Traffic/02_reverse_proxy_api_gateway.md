# Reverse Proxy & API Gateway

> A **reverse proxy** sits in front of origin servers (TLS, buffering, static). An **API gateway** is the microservices **front door**: routing, authn/z, throttling, and cross-cutting policies in one place.

## Plain English

| Concern | Reverse proxy (nginx/Envoy-ish) | API gateway |
|---------|--------------------------------|-------------|
| Primary job | Terminate TLS, forward HTTP, cache static | Product API surface for many services |
| Routing | Host/path → upstream | Path/version → service + canary weights |
| Auth | Often passthrough or basic | JWT/OAuth validation, API keys, mTLS to backends |
| Throttling | Connection / request limits | Per-key, per-tenant quotas |
| Client view | “The website” | “The public API” |

They overlap in practice — many gateways *are* reverse proxies with policy plugins.

```text
  Mobile / Web / Partners
            │
            ▼
  ┌──────────────────────────┐
  │      API Gateway         │
  │  TLS · Auth · Rate limit │
  │  Route /v1/* → services  │
  └────────────┬─────────────┘
       ┌───────┼───────┐
       ▼       ▼       ▼
    Orders   Users   Catalog
    (svc)    (svc)   (svc)
```

## Simple example

**E-commerce checkout API** behind one public hostname `api.shop.com`:

```text
  GET  /v1/products/*     → catalog-svc   (cacheable, lighter auth)
  POST /v1/cart/*         → cart-svc      (session/JWT required)
  POST /v1/checkout       → order-svc     (strict auth + idempotency key)
  Partner /v1/partner/*   → same routes   (API key + tighter rate limit)
```

Gateway validates JWT once, strips internal headers, injects `X-Request-Id`, and rejects abusive keys before they fan out to 12 services.

## Why prefer one over the other

| Prefer **API gateway** when… | Prefer **plain reverse proxy** when… |
|------------------------------|--------------------------------------|
| Many microservices, one public contract | Few backends, mostly static + simple reverse |
| Auth, quotas, API versions centralized | You already enforce policy in each service / mesh |
| External developers / partner APIs | Internal-only traffic (maybe service mesh instead) |

| Centralize at gateway | Push to services / mesh |
|-----------------------|-------------------------|
| One place to audit auth & limits | Avoid gateway as SPOF / latency tax |
| Faster product policy changes | Per-service nuance without redeploying gateway |

**Not “gateway replaces service mesh.”** Gateway = north-south (clients → cluster). Mesh = east-west (service ↔ service).

Keep the gateway **policy-thin enough to reason about**: auth, rate limit, routing, request IDs — push domain logic to services.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Fat gateway | Consistent security & routing | Blast radius; team bottleneck; harder multi-region |
| Thin gateway + mesh | Clear north-south vs east-west | Two systems to operate |
| Auth only in services | Flexible per endpoint | Duplicated bugs; uneven enforcement |
| Aggressive buffering at proxy | Smooth backends | Memory pressure; hide client disconnects if careless |

## Interview trigger phrase

> “I’d put an **API gateway** as the north-south front door for auth, rate limits, and versioned routing — and keep east-west policy in the mesh so the gateway doesn’t become the whole control plane.”

## Exercise

**Design the front door for a multi-tenant SaaS API.**

1. List three policies you’d enforce at the gateway vs inside each microservice — and why.  
2. A partner’s API key is stolen — how does the gateway contain damage in under a minute?  
3. You need 10% of `/v2/search` traffic on a canary build — where do weights live, and what do you monitor to roll back?
