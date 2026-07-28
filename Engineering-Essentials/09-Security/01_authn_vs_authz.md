# AuthN vs AuthZ

> **Authentication (AuthN)** answers *who are you?* **Authorization (AuthZ)** answers *what are you allowed to do?* Mixing them up is a classic interview fail — and a classic production bug.

## Plain English

| | **AuthN** | **AuthZ** |
|---|-----------|-----------|
| Question | Who is this? | What can they access? |
| Examples | Password, OTP, SSO, passkey, mTLS client cert | Roles, policies, ACLs, scopes |
| Failure | 401 Unauthorized (often “unauthenticated”) | 403 Forbidden |

```text
  Request
    → Authenticate (validate session/JWT/API key) → identity
    → Authorize (can identity perform action on resource?) → allow/deny
```

You can be authenticated and still forbidden. You cannot be meaningfully authorized without knowing identity (except rare public/anonymous policies).

## Essentials (must-know for this topic)

### AuthN vs AuthZ — clear difference

| | **Authentication (AuthN)** | **Authorization (AuthZ)** |
|---|----------------------------|---------------------------|
| Question | **Who** are you? | **What** may you do? |
| Proves / enforces | Identity | Permissions on actions/resources |
| Examples | Password, OTP, SSO/OIDC, API key, mTLS | Roles, policies, ACLs, OAuth scopes |
| Typical HTTP | **401** unauthenticated | **403** authenticated but denied |

### Order of operations

```text
  Authenticate → identity  →  Authorize → allow / deny
```

| Fact | Implication |
|------|-------------|
| Logged in ≠ allowed | Always AuthZ sensitive actions server-side |
| No identity | Can’t do meaningful AuthZ (except public) |
| Client UI hide | UX only — not security |

## Simple example

**Alice logs into GitHub:**

```text
  AuthN: password + 2FA → session cookie / token proving "Alice"
  AuthZ: Alice is admin on repo X, reader on repo Y
         DELETE /repos/Y → 403 even though logged in
```

**Service-to-service:** AuthN via IAM role / mTLS; AuthZ via IAM policy / mesh authz.

## When to use / trade-offs

| Concern | Put it in AuthN layer | Put it in AuthZ layer |
|---------|----------------------|----------------------|
| Prove identity | Passwords, OIDC, API keys | — |
| Feature permissions | — | RBAC/ABAC, scopes |
| “Logged in?” | Session/token valid | Not enough alone |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Central IdP (AuthN) | SSO, one place for creds | Dependency on IdP |
| Fine-grained AuthZ | Least privilege | Policy complexity |
| Coarse roles only | Simple | Over-permissioned users |

## Pitfalls

- Returning **404 vs 403** inconsistently leaking resource existence (product choice — be intentional).  
- Checking AuthN once at gateway then trusting every internal call with no AuthZ.  
- Encoding permissions only on the client (“hide the button”).  
- Long-lived tokens with no revocation story.

## Interview trigger phrase

> “**AuthN** establishes identity; **AuthZ** enforces permissions. I’d authenticate at the edge, then authorize every sensitive action on the server with explicit policy — never ‘they’re logged in, so OK.’”

## Exercise

**Banking API: transfer money.**

1. What checks are AuthN vs AuthZ?  
2. User is logged in but transferring from someone else’s account — which failed?  
3. Service account for a worker — how do AuthN and AuthZ look different from a human user?
