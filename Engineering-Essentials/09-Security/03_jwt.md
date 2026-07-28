# JWT

> A **JWT** (JSON Web Token) is a signed (sometimes encrypted) string carrying claims. Common for **stateless** API auth — but misuse (no expiry, weak secrets, storing sensitive data) is an interview favorite.

## Plain English

JWT shape: `header.payload.signature` (Base64url JSON).

| Part | Contains |
|------|----------|
| **Header** | alg, typ |
| **Payload** | claims: `sub`, `exp`, `iat`, `aud`, custom |
| **Signature** | HMAC or asymmetric (RS256/ES256) over header+payload |

```text
  Client sends: Authorization: Bearer eyJhbGciOi...
  Server: verify signature → check exp/aud/iss → trust claims
```

**Access token** (short-lived) + **refresh token** (longer, stored carefully, rotatable) is the usual pattern.

## Essentials (must-know for this topic)

### Header / payload / signature

| Part | Contains | Notes |
|------|----------|-------|
| **Header** | `alg`, `typ` | Pin algorithms in libraries — reject `none` |
| **Payload** | Claims (`sub`, `exp`, `iat`, `aud`, …) | **Base64-readable**, not encrypted |
| **Signature** | HMAC (HS256) or asymmetric (RS256/ES256) | Proves integrity + authenticity |

Shape: `header.payload.signature` (three Base64url segments).

### Access vs refresh

| Token | Lifetime | Purpose | Storage care |
|-------|----------|---------|--------------|
| **Access JWT** | Minutes | Authorize API calls | Bearer header; short TTL |
| **Refresh** | Hours–days | Obtain new access tokens | HttpOnly / secure store; rotatable + revocable |

### Validation checklist (fail PR if missing)

| Check | Why |
|-------|-----|
| Signature | Not forged |
| `exp` | Not expired |
| `iss` / `aud` | Right issuer & audience |
| Algorithm allowlist | No alg confusion |

**RS256 vs HS256:** asymmetric scales verify across many APIs via JWKS; shared HMAC secret is harder to distribute safely.

## Simple example

```text
  Payload:
  {
    "sub": "user-42",
    "role": "admin",   // careful: authz in token can go stale
    "aud": "api.myapp.com",
    "exp": 1710003600
  }
```

**RS256:** IdP signs with private key; APIs verify with public key (JWKS). Better than sharing one HMAC secret across many services.

## When to use / trade-offs

| Prefer **JWT access tokens** when… | Prefer **opaque server sessions** when… |
|------------------------------------|-----------------------------------------|
| Stateless APIs, multiple resource servers | Need instant revoke / small tokens |
| OIDC / microservice ecosystem | Simple monolith with session store |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Short-lived access JWT | Lower theft window | Refresh complexity |
| Claims-heavy JWT | Fewer DB lookups | Stale authz; large headers |
| Symmetric HS256 | Simple | Secret distribution pain |
| Asymmetric RS256 | Scalable verify | Key rotation ops |

## Pitfalls

- `alg: none` or accepting algorithm confusion attacks — use a vetted library, pin algorithms.  
- Putting **secrets/PII** in payload (it’s readable Base64, not encrypted).  
- Long-lived JWT with no revoke list → theft lasts forever.  
- Storing JWT in **localStorage** (XSS risk) vs HttpOnly cookie (CSRF considerations).  
- Trusting `role` in token forever after demotion — use short TTL or server-side checks.

## Interview trigger phrase

> “I’d use **short-lived signed JWTs** (validate **sig/exp/aud**), keep **refresh tokens** rotatable and revocable, and never treat JWT payload as encrypted or as forever-fresh authorization.”

## Exercise

**API gateway validates JWT for 10 services.**

1. HS256 vs RS256 — which and why?  
2. Admin demotes a user — how soon is access gone?  
3. Name three validation checks you’d fail a PR for omitting.
