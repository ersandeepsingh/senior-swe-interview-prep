# Authentication & Authorization

> **Authentication (authn)** answers *who are you?* **Authorization (authz)** answers *what are you allowed to do?* OAuth2 / OIDC issue identity; **JWT** carries claims; **RBAC** (and ABAC) decide permissions. Mixing these up is a common interview slip.

## Plain English

| Term | Meaning | Example |
|------|---------|---------|
| **Authn** | Prove identity | Login, SSO, MFA |
| **Authz** | Enforce permissions | “Can edit invoice #12?” |
| **OAuth2** | Delegated authorization framework | “App may read my calendar” |
| **OIDC** | Identity layer on OAuth2 | ID token = who you are |
| **JWT** | Signed token with claims | `sub`, `roles`, `exp` |
| **RBAC** | Roles → permissions | `admin`, `viewer` |

```text
  User ──login──► IdP (Auth0/Cognito/Okta)
                     │
                     ▼
              access token (JWT)
                     │
                     ▼
  API Gateway / service
       │  1) verify signature + exp   ← authn
       │  2) check role/permission    ← authz
       ▼
     Business handler
```

## Simple example

Docs app: Alice is `editor` on doc-7, Bob is `viewer`.

```text
  Alice JWT: { sub: alice, roles: ["editor"] }
  PUT /docs/7  → authn OK → authz: editor on doc-7 → allow

  Bob JWT:   { sub: bob, roles: ["viewer"] }
  PUT /docs/7  → authn OK → authz: viewer cannot write → 403
```

Valid token ≠ allowed action. **403** is authz; **401** is missing/invalid authn.

## Why prefer one over the other

| Prefer **JWT access tokens** when… | Prefer **opaque tokens + introspection** when… |
|------------------------------------|------------------------------------------------|
| Stateless APIs at scale; local verify | Need instant revoke without short TTL tricks |
| Microservices verify with public key | Central session store is acceptable |

| Prefer **RBAC** when… | Prefer **ABAC / fine-grained** when… |
|-----------------------|--------------------------------------|
| Coarse roles map cleanly | Per-resource ACLs (doc/share links) |
| Admin / member / viewer enough | Policy needs attributes (dept, time, geo) |

**Refresh tokens** stay private (browser httpOnly / secure backend). Don’t put secrets in localStorage casually in a senior design.

### Real systems (interview name-drops)

- **OAuth2/OIDC:** Auth0, Cognito, Okta, Keycloak.
- **Service-to-service:** mTLS, SPIFFE, signed service JWTs.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| JWT in each request | No session lookup; easy horizontal scale | Revocation harder until expiry; token size |
| Server sessions | Instant logout / revoke | Sticky or shared session store |
| Coarse RBAC | Simple to reason about | Coarse = over/under permission |
| Per-object ACLs | Precise sharing | More data model + check cost |

**Common interview trap:** “We’ll use JWT for authentication” and never mentioning authorization checks on the resource.

## Interview trigger phrase

> “I’d separate **authn** (OIDC/JWT verify) from **authz** (RBAC plus resource checks) — a valid token still gets **403** if the role can’t mutate that object.”

## Exercise

**Design a multi-user project management API.**

1. Map login (SSO) vs “can close sprint” — which is authn vs authz?  
2. Why might you keep JWT TTL short and use refresh tokens?  
3. One sentence: how does service B trust a request forwarded from API gateway (hint: verify JWT or internal identity)?
