# DNS

> The phone book of the internet: **names → addresses** (and other records), with caching controlled by **TTL**.

## Plain English

When you open `api.example.com`, resolvers translate the name to an IP (and cache the answer). Outages are often DNS: bad TTL, broken CNAMEs, or cutovers that ignore cache lag.

## Essentials (must-know for this topic)

### Resolution path (simplified)

1. Check local / OS cache  
2. Ask recursive resolver (ISP / 1.1.1.1 / 8.8.8.8)  
3. Walk hierarchy: root → TLD (`.com`) → authoritative NS for the zone  
4. Return **A** / **AAAA** (or follow **CNAME**)  
5. Cache for **TTL** seconds  

### Record types (vocab)

| Record | Meaning |
|--------|---------|
| **A** | Name → IPv4 |
| **AAAA** | Name → IPv6 |
| **CNAME** | Name → another name (alias) |
| **MX** | Mail servers |
| **TXT** | Verification, SPF/DKIM, etc. |
| **NS** | Authoritative nameservers for the zone |
| **ALIAS/ANAME** | Apex-friendly alias (provider feature; not classic CNAME-at-apex) |

### TTL & cutover

| TTL choice | Effect |
|------------|--------|
| **High** (hours) | Fewer queries; slow failover |
| **Low** (30–60s) | Faster cutover; more DNS load |

**Migration pattern:** lower TTL hours ahead → change record → wait → raise TTL.

### Routing extras interviewers mention

| Technique | Use |
|-----------|-----|
| **GeoDNS / latency-based** | Different answers by region (Route 53 policies, etc.) |
| **Health-check failover** | Swap to backup IP when primary fails (still TTL-lagged) |

DNS change ≠ global instant update — caches you don’t control linger.

## Why seniors get asked

Outages are often DNS: bad TTL, broken CNAME chains, cutover mistakes. Seniors plan migrations with TTL strategy.

## Simple example

```bash
dig api.example.com +short
dig api.example.com A
dig example.com MX
dig example.com NS

# Follow CNAME
dig www.example.com CNAME +short
```

Cutover pattern: lower TTL to 60s hours ahead → change record → wait → raise TTL again.

## When to use / when not / trade-offs

| Technique | Use when |
|-----------|----------|
| Low TTL | Imminent migration / failover testing |
| High TTL | Stable endpoints; less resolver load |
| CNAME to CDN | Apex limitations may need ALIAS/ANAME |
| GeoDNS | Regional user affinity / compliance |

**Trade-offs:** low TTL = faster failover but more DNS queries; DNS failover is not instant everywhere because of caches you don’t control.

## Common pitfalls

- Leaving TTL at 24h then needing emergency cutover
- CNAME at zone apex (not always allowed)
- Forgetting both A and AAAA
- Assuming DNS change = global instant update

## Interview trigger phrase

> “Before a cutover I’d drop DNS TTL, swap A/CNAME carefully, and expect full propagation to lag because of caches.”

## Exercise

Move `api.example.com` from IP A to IP B with <5 minutes of split-brain risk. Write the TTL steps and one reason some users might still hit A afterward.
