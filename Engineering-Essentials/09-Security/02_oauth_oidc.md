# OAuth 2.0 / OIDC

> **OAuth 2.0** is a **delegation** framework: an app gets limited access to a user’s resources without the user’s password. **OIDC** (OpenID Connect) layers **identity** (who logged in) on top of OAuth.

## Plain English

| Term | Meaning |
|------|---------|
| **Resource owner** | The user |
| **Client** | Your app requesting access |
| **Authorization server** | Issues tokens (e.g. Google, Auth0, Okta) |
| **Resource server** | API that accepts tokens |
| **Scope** | Bounded permission (e.g. `read:email`) |
| **OIDC** | Adds ID token + UserInfo — login/SSO |

**Common flows:**

| Flow | Typical use |
|------|-------------|
| **Authorization Code (+ PKCE)** | Web/mobile apps — preferred |
| **Client Credentials** | Service-to-service (no user) |
| **Device Code** | TVs / CLIs |
| **Implicit** | Legacy; avoid for new apps |

```text
  User → Auth server login/consent → auth code
  App → exchange code (+ PKCE) → access token (+ refresh)
  App → API with Bearer access token
```

## Essentials (must-know for this topic)

### OAuth vs OIDC

| | **OAuth 2.0** | **OIDC** |
|---|---------------|----------|
| Purpose | **Delegation** — app acts with limited access | **Identity** — who logged in (SSO) |
| Main artifact | **Access token** (call APIs) | **ID token** (+ UserInfo) |
| Without the other | Can grant API access without “login product” | Built **on top of** OAuth |

### Roles & tokens

| Term | Meaning |
|------|---------|
| **Resource owner** | User |
| **Client** | Your app |
| **Authorization server** | Issues tokens (Okta, Auth0, Google, …) |
| **Resource server** | API that accepts access tokens |
| **Scope** | Bounded permission (`read:email`) |
| **Access token** | Short-lived; call APIs |
| **Refresh token** | Longer-lived; get new access tokens; store/rotate carefully |
| **PKCE** | Protects public clients in Auth Code flow |

### Flows to name

| Flow | Use |
|------|-----|
| **Authorization Code + PKCE** | Web/mobile user login — **preferred** |
| **Client Credentials** | Service-to-service, no user |
| **Implicit** | Legacy — avoid |

## Simple example

**“Login with Google”:**

```text
  OIDC: ID token says sub=google-user-123, email verified
  OAuth scopes: openid email profile
  Your API trusts ID token signature → creates local session/user row
```

**GitHub App reading repos:** OAuth scopes `repo` — access token calls GitHub API; your app never sees the user’s GitHub password.

## When to use / trade-offs

| Prefer **Auth Code + PKCE** when… | Prefer **Client Credentials** when… |
|-----------------------------------|-------------------------------------|
| User login / delegated access | Daemon/service with its own identity |
| SPAs/mobile (public clients) | No user in the loop |

| Prefer **OIDC SSO** when… | Prefer **home-grown password** when… |
|---------------------------|--------------------------------------|
| You want less password risk / enterprise SSO | Tiny internal tool (still usually better to use a library/IdP) |

| Decision | You gain | You give up |
|----------|----------|-------------|
| External IdP | Security expertise, MFA | Vendor dependency |
| Fine scopes | Least privilege | More consent UX |
| Long-lived refresh tokens | UX | Theft impact; need rotation/revoke |

## Pitfalls

- Using **implicit flow** or stuffing tokens in URLs.  
- Skipping **PKCE** on public clients.  
- Confusing **ID token** (identity to your app) with **access token** (call APIs).  
- Accepting tokens without validating **issuer, audience, signature, expiry**.  
- Over-broad scopes (`*` / full account).

## Interview trigger phrase

> “I’d use **OAuth 2.0 Auth Code with PKCE** for user delegation, **OIDC** when I need identity/SSO, and **client credentials** for service accounts — always validating **aud/iss/exp** on tokens.”

## Exercise

**SaaS app: “Connect Slack” + “Login with Okta.”**

1. Which is OAuth, which is OIDC-first, and why?  
2. Why PKCE for a mobile app?  
3. Access token leaked — what mitigations should already be in place?
