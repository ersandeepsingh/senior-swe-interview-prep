# Cookies & Sessions

> Cookies are small bits of data the browser stores and **sends back** on later requests — the usual glue for **session auth** (vs putting JWTs in `Authorization`).

## Plain English

Browsers automatically attach cookies to matching requests. That makes them convenient for web sessions — and dangerous if flags are wrong (XSS/CSRF). Seniors pick **session cookie vs bearer token** deliberately.

## Essentials (must-know for this topic)

### Session cookie vs bearer token

| | **Server session + cookie** | **Bearer token (JWT/opaque)** |
|--|----------------------------|-------------------------------|
| Where state lives | Server (Redis/DB) | Token (stateless) ± revoke list |
| Browser send | Automatic on cookie scope | App sets `Authorization` |
| Revocation | Delete session — instant | Harder until expiry (need blocklist) |
| Typical fit | First-party web apps | Mobile, CLI, service-to-service |

### Cookie flags (must memorize)

| Flag | Why |
|------|-----|
| `HttpOnly` | JS can’t read → mitigates XSS theft |
| `Secure` | HTTPS only |
| `SameSite=Lax` | Default CSRF mitigation for many apps |
| `SameSite=Strict` | No cross-site send at all |
| `SameSite=None` | Cross-site allowed — **requires `Secure`** |
| `Path` / `Domain` | Scope of where cookie is sent |
| `Max-Age` / `Expires` | Lifetime |

### CSRF vs XSS (one table)

| Attack | Idea | Mitigations |
|--------|------|-------------|
| **CSRF** | Evil site triggers browser to send **your cookies** | `SameSite`, CSRF tokens, don’t use cookies for pure APIs |
| **XSS** | Evil script runs on your origin | `HttpOnly` (can’t steal cookie), CSP, output encoding |

**localStorage JWTs:** XSS can steal them — prefer `HttpOnly` cookies for browser session tokens when possible.

## Why seniors get asked

Auth design questions always hit cookies vs tokens, CSRF, and XSS. Seniors must set flags correctly, not just “set a cookie.”

## Simple example

```http
HTTP/1.1 200 OK
Set-Cookie: session_id=abc123; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=86400
```

```bash
curl -c jars.txt -b jars.txt -X POST https://app.example.com/login \
  -d 'user=a&pass=b' -v
```

Pseudocode:

```python
def login(user):
    sid = new_id()
    redis.setex(f"sess:{sid}", 86400, user.id)
    response.set_cookie("session_id", sid, httponly=True, secure=True, samesite="Lax")
```

## When to use / when not / trade-offs

| Prefer cookies/sessions when… | Prefer bearer tokens when… |
|-------------------------------|----------------------------|
| First-party browser apps | Mobile / CLI / server-to-server |
| You want revocation by deleting server session | Pure APIs with `Authorization` header |
| Same-site CSRF can be controlled | Cross-service SPA calling many APIs |

**Trade-offs:** sessions are revocable and simple for browsers; sticky server state (or shared Redis). JWTs scale horizontally but are harder to revoke early.

## Common pitfalls

- Missing `HttpOnly` / `Secure` / `SameSite`
- `SameSite=None` without `Secure`
- Storing JWTs in `localStorage` (XSS steals them)
- CSRF on cookie-authenticated state-changing POSTs without tokens/SameSite

## Interview trigger phrase

> “For a first-party web app I’d use Secure HttpOnly SameSite cookies with server sessions; for mobile APIs I’d use bearer tokens and treat XSS/CSRF differently.”

## Exercise

Explain one CSRF attack against a cookie session and how `SameSite=Lax` plus a CSRF token reduce it. When is `SameSite=None` required?
