# API Security

> Harden the edge: **authenticate**, **validate inputs**, **rate-limit**, and put a **WAF** in front for common web exploits. Most “API got hacked” stories are boring — injection, auth gaps, and abuse — not exotic crypto breaks.

## Plain English

| Control | What it stops |
|---------|----------------|
| **Authn/Authz** | Anonymous or cross-tenant access |
| **Input validation / schema** | Injection, oversized payloads, type confusion |
| **Rate limiting / quotas** | Credential stuffing, scraping, noisy neighbors |
| **WAF** | Known XSS/SQLi patterns, bots (layer 7) |
| **Least privilege / scope** | Stolen token doing everything |

```text
  Internet
      │
      ▼
  ┌─────────┐
  │   WAF   │  block obvious attacks / bots
  └────┬────┘
       ▼
  ┌─────────┐
  │ Gateway │  TLS, auth, rate limit, request size
  └────┬────┘
       ▼
  ┌─────────┐
  │   API   │  validate schema, authz, parameterized queries
  └─────────┘
```

## Simple example

Public `POST /login` without limits:

```text
  Attacker sprays 1M password attempts
  → account takeover / DB melt
```

Fix shape:

```text
  Rate limit: 5/min per IP + per username
  Lockout / backoff + MFA for sensitive accounts
  WAF: block obvious bot signatures (help, not sole defense)
  Body: max size; JSON schema; never string-concat SQL
```

Another classic: `GET /users/{id}` with only “logged in” check — IDOR. Authz must bind **resource to tenant/user**.

## Why prefer one over the other

| Prefer **gateway rate limits** when… | Prefer **app-level quotas** when… |
|--------------------------------------|-----------------------------------|
| Coarse IP/token abuse protection | Per-tenant / per-plan fairness |
| Edge drops junk early | Business rules (“100 API calls/min on Pro”) |

| Prefer **WAF** when… | Don’t rely on WAF alone when… |
|----------------------|-------------------------------|
| Public HTTP surface, compliance checkbox | You skipped authz / validation in the app |
| Filtering known attack patterns | Attacker uses valid auth + slow logic abuse |

**Defense in depth:** WAF ≠ substitute for parameterized queries and proper authz.

### Real systems (interview name-drops)

- **AWS WAF + API Gateway, Cloudflare, Kong, Envoy/rate-limit service**.
- **OWASP API Top 10** — worth naming in interviews (BOLA/IDOR, broken auth, injection).

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Strict rate limits | Abuse resistance | False positives for NAT’d campuses / mobile |
| Schema validation | Fewer parse/injection surprises | Flexibility; versioning discipline |
| WAF rules | Cheap mitigation of commodity attacks | Bypass via legitimate-looking requests |
| Verbose error messages | Easier debugging | Info leak to attackers |

**Common interview trap:** Drawing microservices with zero mention of rate limits, IDOR, or input validation.

## Interview trigger phrase

> “At the edge I’d put **WAF + gateway auth + rate limits**, then in the service **schema validation and per-resource authz** — WAF doesn’t replace IDOR checks.”

## Exercise

**Design a public REST API for a SaaS notes app.**

1. Name three concrete edge controls you’d put before the notes service.  
2. User A guesses User B’s note UUID — which control stops the leak (be specific)?  
3. One sentence: how do free-tier vs enterprise rate limits differ architecturally?
