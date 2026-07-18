# DNS & GeoDNS

> **DNS** maps names to addresses. **GeoDNS** (geo-routing) answers with different IPs by client location so users hit the **nearest healthy region** — before any load balancer sees the request.

## Plain English

| Piece | What it does |
|-------|----------------|
| **Resolver chain** | Stub → recursive resolver → authoritative nameservers |
| **A/AAAA** | Name → IPv4/IPv6 |
| **CNAME** | Alias to another name (CDN, LB hostname) |
| **TTL** | How long resolvers cache the answer |
| **GeoDNS / latency routing** | Different answer based on geography or measured RTT |
| **Health-aware DNS** | Stop returning IPs for dead regions (failover) |

DNS is a **coarse, cached** control plane — great for region selection, bad for per-request micro-balancing.

```text
  User (Mumbai)              User (Virginia)
       │                          │
       ▼                          ▼
  Recursive DNS              Recursive DNS
       │                          │
       ▼                          ▼
  GeoDNS authoritative ── returns ──►
       │                          │
       ▼                          ▼
  api-in.example.com         api-us.example.com
  (Mumbai region VIP)        (US-East VIP)
```

## Simple example

**Global chat app** with regions `ap-south-1` and `us-east-1`:

```text
  chat.example.com  (GeoDNS)
        │
        ├─ Clients near IN → 13.x.x.x  (Mumbai ALB)
        └─ Clients near US → 52.y.y.y  (Virginia ALB)

  Mumbai DC down → health check fails → DNS stops advertising 13.x.x.x
  (after TTLs expire — not instant)
```

Users still need sticky sessions / regional data affinity *inside* the region; DNS only got them to the right front door.

## Why prefer one over the other

| Prefer **GeoDNS / latency DNS** when… | Prefer **anycast / global LB** when… |
|---------------------------------------|--------------------------------------|
| Multi-region active-active entry | You need faster failover than DNS TTL |
| Simple “nearest POP/region” | Fine-grained health + instant drain |
| You already use Route53/Cloud DNS policies | You operate a global anycast fabric (CDN/LB vendors) |

| Short TTL | Long TTL |
|-----------|----------|
| Faster failover / traffic shift | Less resolver load; more cache hits |
| More DNS query volume | Failover waits for cache expiry |

**Not “DNS load-balances pods.”** DNS picks a *region or VIP*. Pod balance is the regional LB’s job.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| GeoDNS | Lower RTT to nearest region | Resolver location ≠ user location sometimes |
| Low TTL | Quicker cutover | Higher DNS QPS; flapping if health is noisy |
| DNS failover only | Simple DR story | Minutes of bad answers until TTL drains |
| CNAME to CDN | Easy edge offload | Extra lookup; apex domain constraints |

## Interview trigger phrase

> “I’d use **GeoDNS** to steer users to the nearest region, with health checks to pull a bad region out of rotation — knowing failover is **TTL-bound**, so critical cutovers may need anycast or pre-warmed global LB.”

## Exercise

**Design DNS for a two-region payments API.**

1. Client in Delhi resolves `pay.example.com` — what should they get, and what does a 300s TTL imply during Mumbai outage?  
2. Why might a Delhi user still land on US-East even with GeoDNS?  
3. Compare DNS failover vs active-active with a global anycast VIP for “payments must fail over in <30s.”
