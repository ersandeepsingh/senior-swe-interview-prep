# Service Mesh

> A **service mesh** (Istio, Linkerd, Consul Connect) puts a **sidecar proxy** (often Envoy) next to each service. The mesh handles **mTLS**, retries, timeouts, traffic shaping, and observability **without** baking that into every app.

## Plain English

| Piece | Role |
|-------|------|
| **Sidecar proxy** | Intercepts inbound/outbound traffic for the pod |
| **Control plane** | Configures proxies (policies, certs, routes) |
| **Data plane** | The proxies carrying traffic |
| **mTLS** | Service-to-service encryption + identity |
| **Traffic policy** | Canary weights, retries, circuit breaking |

```text
  App A → sidecar A ──mTLS──► sidecar B → App B
              ▲                   ▲
              └──── control plane ┘
```

Apps speak plain HTTP to localhost; sidecars do the hard parts.

## Essentials (must-know for this topic)

### Mesh pieces

| Piece | Role |
|-------|------|
| **Sidecar proxy** | Per-pod proxy (often Envoy) intercepts traffic |
| **Data plane** | The proxies carrying requests |
| **Control plane** | Pushes policies, certs, routes to proxies |
| **mTLS** | Encrypt + identity for service-to-service (east-west) |
| **Traffic policy** | Canary weights, retries, timeouts, circuit break |

### Mesh vs API gateway

| | **API gateway / Ingress** | **Service mesh** |
|---|---------------------------|------------------|
| Focus | North-south (edge → services) | East-west (service ↔ service) |
| Typical jobs | Auth, rate limit, public routing | mTLS, retries, fine traffic split |
| When enough alone | Few services | Many polyglot microservices |

### Cost/benefit flashcard

| You gain | You pay |
|----------|---------|
| Uniform mTLS + observability | CPU/RAM per sidecar; ops complexity |
| Canary without app code | Misconfigured retries → storms |
| Consistent timeouts/CB | Debug: app vs Envoy? |

**Rule:** don’t install a mesh for 3 services “because Netflix.”

## Simple example

**Canary without app code:**

```text
  VirtualService: 90% → reviews-v1, 10% → reviews-v2
  PeerAuthentication: STRICT mTLS in namespace
  DestinationRule: outlier detection eject failing pods
```

**Golden signals:** mesh emits latency/error metrics per hop → better tracing between services.

## When to use / trade-offs

| Prefer **service mesh** when… | Prefer **library / gateway only** when… |
|-------------------------------|-----------------------------------------|
| Many microservices, polyglot | Few services; mesh ops cost too high |
| Need uniform mTLS + traffic policy | Edge gateway + app middleware enough |
| Platform team can own it | Startup speed matters more than uniformity |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Sidecar mesh | Consistent policy, mTLS | CPU/RAM per pod; complexity |
| Mesh retries | Resilience | Retry storms if misconfigured |
| Strict mTLS | Zero-trust east-west | Cert/identity debugging |

## Pitfalls

- Installing Istio “because Netflix” for 3 services.  
- Retries at mesh **and** app **and** client → amplification.  
- Blind to sidecar resource cost at scale.  
- Debugging: is the bug in app or Envoy config?  
- Overlapping features with API gateway — clarify edge vs east-west.

## Interview trigger phrase

> “I’d consider a **service mesh** when we have many services needing **uniform mTLS and traffic control**; for a small system I’d keep **resilience in libraries/gateway** and revisit when platform complexity pays for itself.”

## Exercise

**20 microservices on Kubernetes.**

1. List three problems a mesh solves that an ingress alone doesn’t.  
2. Why can mesh-level retries make an outage worse?  
3. Argue for *not* adopting a mesh yet — two strong reasons.
