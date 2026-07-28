# OWASP Top 10

> The **OWASP Top 10** is a living list of the most critical web app risks. Seniors don’t recite all ten robotically — they **explain the attack, the fix, and where it shows up in their design**.

## Plain English (high-frequency items)

| Risk | In one line | Fix sketch |
|------|-------------|------------|
| **Injection** (SQLi, command) | Untrusted input becomes code/query | Parameterized queries; never string-build SQL/shell |
| **Broken auth** | Weak login/session | MFA, secure session/JWT hygiene, lockout/alerts |
| **XSS** | Attacker script runs in victim browser | Encode output; CSP; sanitize wisely |
| **CSRF** | Browser sends victim’s cookies to your site | SameSite cookies; CSRF tokens; prefer non-cookie tokens carefully |
| **SSRF** | Server fetches attacker-controlled URL | Allowlists; block link-local/metadata IPs |
| **Broken access control** | IDOR / missing AuthZ | Server-side checks every object |
| **Misconfig** | Default creds, open buckets | Harden baselines; scan |
| **Vulnerable components** | Old libs with CVEs | SBOM, patch, dependabot |
| **Insecure design** | No threat model | Design reviews, abuse cases |
| **Integrity failures** | Untrusted CI/artifacts | Sign builds, verify provenance |

```text
  SQLi:  "SELECT * FROM users WHERE id = " + userInput   💥
  Safe:  SELECT * FROM users WHERE id = $1   with bound param
```

## Essentials (must-know for this topic)

### Short list — risk → one-line meaning → fix sketch

| Risk | One-line meaning | Fix sketch |
|------|------------------|------------|
| **Injection** | Input becomes SQL/command/code | Parameterized queries; never string-build |
| **Broken access control** | Missing AuthZ / IDOR | Check every object server-side |
| **Broken auth** | Weak login/session | MFA, secure tokens, lockout/alerts |
| **XSS** | Attacker script in victim browser | Output encode; CSP |
| **CSRF** | Browser sends victim cookies to you | SameSite; CSRF tokens |
| **SSRF** | Server fetches attacker URL | Allowlist; block metadata IPs |
| **Security misconfig** | Defaults, open buckets, verbose errors | Harden baselines; scan |
| **Vulnerable components** | Known-CVE libs | Patch, SBOM, Dependabot |
| **Insecure design** | No threat model | Abuse cases in design review |
| **Software/data integrity** | Untrusted build/artifact | Sign & verify provenance |

### Highest-frequency interview trio

| Attack | Classic symptom |
|--------|-----------------|
| **SQLi** | String-concatenated queries |
| **XSS** | Unescaped user HTML |
| **IDOR** | `/resource/{id}` without ownership check |

## Simple example

**IDOR:** `GET /invoices/214` returns another customer’s invoice because you only checked “logged in,” not “owns 214.”

**SSRF:** image-fetcher URL `http://169.254.169.254/` steals cloud metadata credentials.

**XSS:** comment stored as `<script>…</script>` rendered raw on a page.

## When to use / trade-offs

Security controls always trade friction for risk reduction:

| Prefer **strict allowlists** when… | Prefer **flexible validation** when… |
|------------------------------------|--------------------------------------|
| SSRF, redirects, file types | Rich user content with careful sanitization |
| Admin tools | Consumer UX that needs power |

| Control | You gain | You give up |
|---------|----------|-------------|
| CSP + encoding | Strong XSS defense | Some third-party script freedom |
| Parameterized SQL | Injection safety | Can’t dynamically invent SQL freely (good) |
| MFA | Account takeover resistance | UX friction |

## Pitfalls

- Client-only validation.  
- Blacklist sanitizers for HTML/SQL (“remove DROP”) — attackers bypass.  
- Disabling CSRF “because SPA.”  
- Logging secrets in error traces.  
- Assuming internal networks don’t need AuthZ (SSRF pivots).

## Interview trigger phrase

> “I’d threat-model for **injection, XSS, CSRF, SSRF, and broken access control** — parameterized queries, output encoding, server-side AuthZ per object, and allowlisted egress for fetches.”

## Exercise

**URL preview feature (fetch title for a link).**

1. Which OWASP risks appear immediately?  
2. Give two concrete SSRF mitigations.  
3. Preview HTML title has a script tag — how do you display safely?
