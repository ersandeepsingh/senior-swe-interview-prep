# Load Balancing

> A **load balancer** spreads traffic across healthy backends. **L4** routes on IP/port; **L7** routes on HTTP path/host/headers. Algorithm choice (RR, least-conn, consistent-hash) decides fairness vs affinity.

## Plain English

| Layer | Sees | Good for |
|-------|------|----------|
| **L4** (transport) | TCP/UDP 5-tuple | Raw throughput, TLS passthrough, simple fan-out |
| **L7** (application) | HTTP method, path, cookies, headers | Path-based routing, A/B, auth at edge, gRPC methods |

| Algorithm | Behavior | Pick when… |
|-----------|----------|------------|
| **Round-robin** | Next server in turn | Homogeneous backends, similar request cost |
| **Least connections** | Prefer fewest open conns | Long-lived / uneven request duration |
| **Consistent hash** | Same key → same backend | Sticky cache locality, session affinity without sticky-LB hacks |

```text
                    Clients
                       │
                       ▼
              ┌─────────────────┐
              │  Load balancer  │
              │  L4 or L7       │
              └────────┬────────┘
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
      ┌─────┐       ┌─────┐       ┌─────┐
      │ App │       │ App │       │ App │
      │  1  │       │  2  │       │  3  │
      └─────┘       └─────┘       └─────┘
```

## Simple example

**Video streaming API:** millions of short GETs for metadata + fewer long uploads.

```text
  Metadata GET /v1/titles/*  → L7 LB, round-robin across API pods
  Live WebSocket /ws         → L4 or L7 + least-conn (long-lived)
  User upload chunk key=uid  → consistent-hash(uid) → same upload worker
```

Homogeneous metadata pods: RR is fine. Chat sockets pile up on one pod under RR if durations vary — least-conn helps. Resumable upload wants the same node’s local temp disk — consistent-hash on `uploadId`.

## Why prefer one over the other

| Prefer **L4** when… | Prefer **L7** when… |
|---------------------|---------------------|
| You need max pps / TLS ends on app | You route by path, host, header, cookie |
| Protocol isn’t HTTP (raw TCP, DB proxy) | You want WAF, request transforms, canary by URL |
| Simpler failure model | You accept more LB CPU / TLS termination cost |

| Prefer **RR** | Prefer **least-conn** | Prefer **consistent-hash** |
|---------------|----------------------|----------------------------|
| Equal cheap requests | Uneven or long connections | Cache hit rate / affinity matters |

**Not “L7 is always smarter.”** L7 costs more and can become a bottleneck; many shops terminate TLS at L7 then L4 inside the mesh.

Health checks matter as much as the algorithm: fail open vs fail closed, and slow-start when a pod rejoins so it isn’t flooded cold.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| L7 routing | Smart traffic shaping | Higher LB cost; more config surface |
| Least-conn | Better balance under skew | Slightly more state in the LB |
| Consistent-hash | Locality / sticky behavior | Rebalance churn when nodes add/remove (use virtual nodes) |
| Health checks | Avoid dead backends | Mis-tuned checks flap traffic |

## Interview trigger phrase

> “I’d put an **L7 LB** for path-based API routing, **least-conn** for WebSockets, and **consistent-hash** on userId only where we need cache locality — otherwise plain round-robin.”

## Exercise

**Design load balancing for a food-delivery backend.**

1. Pick L4 vs L7 for: public HTTPS REST, Postgres primary failover proxy, and WebSocket courier tracking — one sentence each.  
2. Courier location updates are bursty and long-lived — which algorithm, and why not RR alone?  
3. You add 30% more API pods mid-peak — what happens to consistent-hash mappings, and how do virtual nodes help?
