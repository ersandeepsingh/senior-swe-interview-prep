# Rate Limiting & DDoS Protection

> **Rate limiting** caps how often a client can call you (fairness + abuse). **DDoS protection** absorbs or sheds volumetric and application-layer floods. Often layered: CDN/WAF → gateway → app → dependency limits.

## Plain English

| Layer | Role |
|-------|------|
| **CDN / Anycast scrubbing** | Absorb volumetric floods far from origin |
| **WAF** | Block known bad patterns / bots (OWASP rulesets) |
| **API gateway rate limit** | Per-IP, per-token, per-tenant quotas |
| **App limits** | Business rules (100 invites/day) |
| **Load shedding** | Drop low-priority work when overloaded |

**Algorithms (interview name-drops):** token bucket, leaky bucket, fixed/sliding window (often Redis-backed).

```text
  Internet → CDN/WAF → LB → API (token bucket per userId)
                              │ 429 + Retry-After
```

## Essentials (must-know for this topic)

### Layered defense

| Layer | Role |
|-------|------|
| **CDN / scrubbing** | Absorb volumetric DDoS far from origin |
| **WAF** | Block known bad patterns / bots |
| **Gateway rate limit** | Per-IP, per-token, per-tenant quotas |
| **App business limits** | “100 invites/day” style rules |
| **Load shedding** | Drop low-priority work under overload |

### Algorithms (name-drop)

| Algorithm | Idea |
|-----------|------|
| **Token bucket** | Tokens refill over time; burst allowed up to bucket |
| **Leaky bucket** | Smooth outflow at fixed rate |
| **Fixed window** | Count in calendar window (edge: boundary burst) |
| **Sliding window** | Smoother count over last N seconds |

### Rate limit vs DDoS

| | **Rate limiting** | **DDoS protection** |
|---|-------------------|---------------------|
| Goal | Fairness / abuse per client | Survive floods that aim to take you down |
| Typical | 429 + identity/IP quotas | Anycast, WAF, capacity, shed |

**Always** protect expensive endpoints (login, search, export) harder than cheap GETs.

## Simple example

**Login endpoint:** 5 attempts / 15 min / account (+ IP cap) to slow credential stuffing. Return generic errors; alert on spikes.

**Public API:** free tier 100 req/min; paid 10k/min — enforce at gateway with Redis counters; never trust client.

## When to use / trade-offs

| Prefer **edge rate limits** when… | Prefer **app limits** when… |
|-----------------------------------|-----------------------------|
| IP/bot abuse, coarse protection | Per-user business quotas |
| Protect origin capacity | Need identity-aware rules |

| Prefer **429 + retry** when… | Prefer **shed / queue** when… |
|------------------------------|-------------------------------|
| Clients are polite/automated | Protect core path during overload |
| Transient overload | Prefer degraded UX over meltdown |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Strict IP limits | Simple | NAT’d users share fate; VPN false positives |
| Per-user limits | Fairness | Needs AuthN; unauthenticated still need IP |
| Aggressive WAF | Blocks attacks | False positives / maintenance |

## Pitfalls

- Rate limit only at app — origin dies before it runs.  
- No **Retry-After** / jitter guidance → retry storms.  
- Limits too coarse (one global bucket) or too fine (state explosion).  
- Forgetting **expensive endpoints** (search, export, login).  
- Equating “we have Cloudflare” with app-layer abuse solved.

## Interview trigger phrase

> “I’d rate-limit at the **edge and gateway** per IP and per identity, return **429 with backoff**, protect login from stuffing, and use **CDN/WAF** for volumetric DDoS — plus load shedding for dependency protection.”

## Exercise

**Public signup + password login + search API.**

1. Propose limits for each (unit + window).  
2. Attacker distributed across many IPs — what else helps?  
3. Your Redis rate-limiter dies — fail open or closed, and why?
