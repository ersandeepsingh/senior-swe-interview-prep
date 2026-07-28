# Load Balancer vs Reverse Proxy vs API Gateway

> Overlapping boxes at the edge. Know the **primary job** of each so you don't invent three products when one nginx can wear two hats.

## Plain English

Same software (Envoy, nginx, HAProxy, cloud ALB/API Gateway) often combines roles. In interviews, separate **concerns**, not product SKUs.

```text
  Clients
     → API Gateway (JWT validate, rate limit, route /v1/orders)
        → L7 LB / Ingress (round-robin to pods)
           → Service pods

  Or simpler:  Clients → ALB (LB + some L7) → pods
  Or:          Clients → nginx (reverse proxy + LB) → pods
```

## Essentials (must-know for this topic)

### Primary jobs

| Component | Primary job | Typical layer |
|-----------|-------------|---------------|
| **Load balancer** | Spread traffic across healthy instances | L4 (TCP/UDP) or L7 (HTTP) |
| **Reverse proxy** | Sit in front of servers: TLS, routing, caching, buffering | L7 |
| **API gateway** | Edge for APIs: auth, rate limit, routing, maybe transform | L7 + policy |

### L4 vs L7 load balancing

| | **L4** | **L7** |
|---|--------|--------|
| Sees | IP / port / TCP|UDP | HTTP host, path, headers |
| Speed | Faster, simpler | More features, more CPU |
| Good for | TLS pass-through, non-HTTP | Path routing, sticky cookies, WAF-ish features |

### Concern checklist

| Concern | Usually lives at |
|---------|------------------|
| JWT / API key auth | API gateway |
| Per-user rate limit | API gateway |
| Path/host routing | Gateway and/or L7 LB / reverse proxy |
| Health-checked distribution | Load balancer / ingress |
| TLS terminate, gzip, cache GETs | Reverse proxy / L7 LB |

## Simple example

Public mobile API:

1. **API Gateway** — verify JWT, apply per-user rate limits, route `/payments/*` to payments service.
2. **LB / Ingress** — distribute to 20 payment pods using health checks.
3. Optional **reverse proxy** features — gzip, cache GETs for catalog, terminate TLS.

Internal east-west traffic might skip the gateway and use service mesh or plain ClusterIP + client-side LB.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Heavy API gateway | Central auth/limits | Latency hop; gateway as bottleneck/SPOF risk |
| Dumb L4 LB only | Speed, simplicity | No path-based routing / app policies |
| One nginx doing everything | Few moving parts | Mixed ops concerns; harder multi-team ownership |
| Mesh + gateway | Fine-grained east-west control | Complexity |

## Pitfalls

- **Double rate limiting / double auth** at gateway and service with conflicting rules.
- **Health checks that hit a dumb `/`** while `/ready` would catch dependency failure.
- **Idle timeouts** at LB shorter than app long-polls → mysterious disconnects.
- **Calling everything an API gateway** when you only needed TLS + round-robin.

## Interview trigger phrase

> “I'd use an **API gateway** for cross-cutting API policy, and a **load balancer** for distributing to healthy instances — often one product does both, but the **concerns** stay distinct.”

## Exercise

You need JWT auth, path routing, and even distribution across pods. Sketch where each concern lives if you may use at most two components.
