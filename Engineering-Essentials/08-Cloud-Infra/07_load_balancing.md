# Load Balancing

> A **load balancer** spreads traffic across healthy backends. Interviewers expect **L4 vs L7**, common algorithms, and **health checks** — plus how this differs from a reverse proxy / API gateway.

## Plain English

| Layer | What it sees | Examples |
|-------|--------------|----------|
| **L4** | TCP/UDP connections (IP:port) | NLB, many network LBs |
| **L7** | HTTP (path, host, headers) | ALB, Nginx, Envoy |

| Algorithm | Idea |
|-----------|------|
| **Round robin** | Rotate backends |
| **Least connections** | Prefer quieter nodes |
| **Consistent hash** | Same client/key → same backend (affinity) |
| **Weighted** | Send more to bigger instances |

```text
  Clients → Load Balancer → [healthy app1][healthy app2][app3 failing ✗]
                              health checks remove app3
```

**Health checks:** LB probes `/healthz`; failing instances leave the pool until recovered.

## Essentials (must-know for this topic)

### L4 vs L7

| | **L4** | **L7** |
|---|--------|--------|
| Sees | TCP/UDP (IP:port) | HTTP path, host, headers |
| Examples | NLB, network LBs | ALB, Nginx, Envoy |
| Good for | Raw perf, non-HTTP, TLS pass-through | Path routing, TLS terminate, WAF |

### Algorithms

| Algorithm | Idea |
|-----------|------|
| **Round robin** | Rotate backends evenly |
| **Least connections** | Prefer quieter nodes (uneven request cost) |
| **Consistent hash** | Same client/key → same backend |
| **Weighted** | Bigger instances get more traffic |

### Related terms

| Term | Meaning |
|------|---------|
| **Health check** | Probe; unhealthy → leave pool |
| **Connection draining** | Finish in-flight on deploy/scale-in |
| **Sticky session** | Affinity to one backend (prefer external session store) |
| **Reverse proxy / API gateway** | Overlaps LB; gateway often adds auth/rate-limit/product APIs |

## Simple example

**Web tier:**

```text
  ALB (L7):
    api.example.com/v1/* → target group api
    example.com/*        → target group web
  Sticky sessions: only if you must (prefer stateless + external session store)
```

**gRPC / TCP:** often L4 or L7 with HTTP/2 awareness.

## When to use / trade-offs

| Prefer **L7** when… | Prefer **L4** when… |
|---------------------|---------------------|
| Path-based routing, TLS terminate, WAF | Extreme performance, non-HTTP protocols |
| Auth/header routing at edge | You want TLS pass-through |

| Prefer **least connections** when… | Prefer **hash affinity** when… |
|------------------------------------|--------------------------------|
| Varied request durations | Need session locality (careful) |
| Better balance under skew | Cache locality on local L1 |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Terminate TLS at LB | Central certs | LB sees plaintext (trust boundary) |
| Sticky sessions | Simpler stateful apps | Bad failover; uneven load |
| Active health checks | Faster remove bad nodes | Probe cost; false positives |

## Pitfalls

- Health check too weak (`TCP open` while app wedged) or too strict (flapping).  
- Sticky sessions hiding that the app isn’t stateless.  
- No connection draining on deploy → dropped in-flight requests.  
- Confusing LB with **API gateway** (auth, rate limit, product APIs) — overlapping but not identical.  
- Single LB AZ → availability myth.

## Interview trigger phrase

> “I’d put an **L7 LB** in front of HTTP services with **health checks and connection draining**, keep apps **stateless**, and use **L4** when I need raw TCP performance or pass-through.”

## Exercise

**Three API replicas, one slow.**

1. Round robin vs least connections — what happens?  
2. Design a health endpoint that means “ready for traffic.”  
3. Blue-green cutover — how does the LB participate?
