# IAM — Identity & Access Management

> **IAM answers two questions:** *Who are you?* (identity) and *What are you allowed to do?* (access). Everything else is mechanism.

---

## 1. Plain English (start here)

Without IAM, a system is either:

- **wide open** (anyone can do anything), or
- **locked with shared passwords** (unsafe, un-auditable).

IAM is the control plane that says:


| Term                       | Meaning                  | Everyday analogy                           |
| -------------------------- | ------------------------ | ------------------------------------------ |
| **Identity**               | A principal that can act | A person, service, or machine “badge”      |
| **Authentication (AuthN)** | Prove who you are        | Showing ID at the door                     |
| **Authorization (AuthZ)**  | Decide what you may do   | Which rooms your badge opens               |
| **Policy / permission**    | The rule itself          | “Alice can read invoices, not delete them” |
| **Credential**             | Proof of identity        | Password, API key, JWT, temporary token    |


**Interview one-liner:**  

> “AuthN is *who*; AuthZ is *what*. IAM is the system that stores identities, verifies them, and evaluates permissions.”

```text
  Request ──► Authenticate ──► Authorize ──► Allow / Deny
                 (who?)          (what?)
```

---

## 2. Core building blocks

### Identities (principals)


| Principal         | Examples                                                        |
| ----------------- | --------------------------------------------------------------- |
| **Human user**    | Employee, customer account                                      |
| **Service / app** | Payment API, worker job                                         |
| **Machine**       | EC2 instance, Lambda, Kubernetes pod                            |
| **Role**          | Temporary “hat” an identity can wear (e.g. `ReadOnly`, `Admin`) |


### Credentials


| Type                               | Use                | Risk                         |
| ---------------------------------- | ------------------ | ---------------------------- |
| Long-lived password / access key   | Humans, legacy     | Leaks are catastrophic       |
| **Temporary credentials / tokens** | Preferred for apps | Expire; blast radius smaller |
| Certificates / mTLS                | Service-to-service | Strong, heavier ops          |


### Policies (authorization rules)

Typical shape: **Principal + Action + Resource + Conditions**

```text
  Allow:
    Principal: role/checkout-service
    Action:    dynamodb:GetItem, dynamodb:PutItem
    Resource:  table/Orders
    Condition: only from VPC / only if MFA / only business hours
```

**Least privilege:** grant the minimum needed — not `*` on everything.

### Common AuthZ models


| Model                | Idea                        | Example                         |
| -------------------- | --------------------------- | ------------------------------- |
| **RBAC**             | Permissions via roles       | `admin`, `editor`, `viewer`     |
| **ABAC**             | Permissions via attributes  | `dept=finance` AND `env=prod`   |
| **ACL**              | Per-resource allow list     | S3 object ACL (less common now) |
| **Policy documents** | Declarative JSON/YAML rules | AWS IAM policies, OPA/Rego      |


---

## 3. How a single request works (happy path)

```text
  Client
    │  1. Login / assume role → get token (JWT / STS creds)
    ▼
  API Gateway / Service
    │  2. Validate token (signature, expiry, issuer)
    │  3. Extract identity (user_id / service_role)
    │  4. Check policy: can this identity do action X on resource Y?
    ▼
  Allow → call DB / S3 / next service
  Deny  → 401 (unauthenticated) or 403 (authenticated but forbidden)
```

**401 vs 403**

- **401 Unauthorized** — we don’t know who you are (or token invalid)
- **403 Forbidden** — we know who you are; you’re not allowed

---

## 4. IAM in the cloud (AWS mental model)

AWS IAM is the textbook example interviewers expect:


| Concept    | Meaning                                                   |
| ---------- | --------------------------------------------------------- |
| **User**   | Long-lived human/service identity (prefer avoid for apps) |
| **Group**  | Bunch of users sharing policies                           |
| **Role**   | Assume-able identity with temporary creds                 |
| **Policy** | JSON allow/deny rules                                     |
| **STS**    | Issues short-lived credentials when you assume a role     |


**Golden rule for backends:**  

> Apps should use **IAM roles** (instance profile / task role / Lambda execution role), **not** hardcoded access keys.

```text
  EC2 / ECS / Lambda
       │ assumes
       ▼
  IAM Role  ──policies──►  S3, DynamoDB, SQS, Secrets Manager...
       │
       ▼
  Temporary keys via STS (auto-rotated by SDK)
```

---

## 5. How distributed systems use IAM

In a monolith, one login check might be enough.  
In a **distributed system**, many services talk to each other across network boundaries — every hop needs identity + permission.

### Problem IAM solves at scale

```text
  User → API Gateway → Order Service → Payment Service → Ledger DB
                         │                 │
                         └── without IAM: how does Payment know
                             Order Service is trusted, not a random caller?
```

### Patterns used in distributed systems

#### A) End-user identity (human → system)

1. User authenticates once (OAuth2 / OIDC / Cognito / Auth0)
2. Gets a **JWT / session token**
3. Each service validates the token (or asks an auth service)
4. Authorization uses roles/claims in the token (`role=customer`, `tenant_id=...`)

```text
  Browser ──login──► IdP (Identity Provider)
      │                    │
      │◄──── JWT ──────────┘
      │
      ▼
  Service A ──JWT──► Service B ──JWT──► Service C
       (each validates signature + permissions)
```

#### B) Service identity (service → service)

Services need their **own** identity (not the user’s password):


| Approach                       | How it works                                             |
| ------------------------------ | -------------------------------------------------------- |
| **IAM roles / cloud identity** | Order service role may call Payment API / write to queue |
| **mTLS**                       | Mutual certificates prove both sides                     |
| **SPIFFE / service mesh**      | Mesh (Istio, Linkerd) issues workload identity           |
| **Signed service tokens**      | Short-lived tokens minted by an internal issuer          |


#### C) Propagation of identity (important senior topic)

When Service A calls Service B on behalf of a user:


| Mode                              | Meaning                                                                |
| --------------------------------- | ---------------------------------------------------------------------- |
| **User context forwarded**        | B sees “Alice asked for this” (JWT passed or exchanged)                |
| **Service acts as itself**        | B sees “OrderService called” (audit + least privilege on service role) |
| **Token exchange / on-behalf-of** | A trades user token for a narrower downstream token                    |


Seniors mention: **don’t over-privilege the service role** just because it “might” need everything.

#### D) Gateways and zero-trust

```text
  Internet
     │
     ▼
  API Gateway / Ingress
     │  AuthN (JWT validate)
     │  coarse AuthZ (rate limit, API key, WAF)
     ▼
  Internal services
     │  fine-grained AuthZ (RBAC/ABAC per resource)
     │  service-to-service IAM / mTLS
     ▼
  Data stores (IAM policies, DB grants, encryption keys via KMS)
```

**Zero-trust idea:** never trust “inside the VPC” alone — authenticate and authorize every call.

#### E) Data-plane IAM (not only APIs)

Distributed systems apply IAM to **resources**, not just HTTP:

- Object storage bucket policies
- Queue publish/subscribe permissions
- KMS key usage (`kms:Decrypt` only for certain roles)
- Database IAM auth (RDS/IAM DB auth) instead of shared passwords

---

## 6. End-to-end example (e-commerce)

```text
  1. Alice logs in → IdP issues JWT (sub=alice, role=customer)
  2. Alice hits Checkout API → gateway validates JWT
  3. Checkout service (IAM role: checkout-role)
        - may Publish to payments-queue
        - may Read catalog table
        - may NOT Delete users
  4. Payment worker assumes payment-role
        - may call Stripe via secrets from Secrets Manager
        - may Write ledger entries
  5. Audit log records: alice + checkout-role + payment-role actions
```

If checkout is compromised, damage is limited by **role policies** — that is IAM’s real value in distributed systems.

---

## 7. Design principles (say these in interviews)

1. **Least privilege** — minimum actions on minimum resources
2. **Short-lived credentials** — prefer roles/tokens over long-lived keys
3. **Separate human IAM from workload IAM** — people ≠ services
4. **Deny by default** — explicit allow
5. **Central identity provider** — don’t invent login per microservice
6. **Audit everything** — who did what, when
7. **Defense in depth** — gateway checks + service checks + data-store policies

---

## 8. Common pitfalls


| Pitfall                                               | Better approach                          |
| ----------------------------------------------------- | ---------------------------------------- |
| Access keys in code / `.env` committed                | IAM roles + Secrets Manager              |
| One fat `admin` role for all services                 | Per-service roles                        |
| Only authenticate at the edge, trust internal network | Service identity + AuthZ on each service |
| Confusing 401 and 403                                 | Clear AuthN vs AuthZ errors              |
| Authorization only in UI                              | Always enforce on the server             |


---

## 9. Interview trigger phrases

> “IAM is identity + authentication + authorization. In distributed systems I’d use an IdP for users (OIDC/JWT), IAM roles for workloads with least privilege, and validate permissions at the gateway *and* inside services — never rely on network location alone.”

> “My EC2/Lambda assumes an IAM role so the SDK gets temporary STS credentials — no long-lived keys in config.”

---

## 10. Exercise

1. Draw AuthN vs AuthZ for: user login, service calling S3, admin deleting a user.
2. For a chat system, list **3 IAM roles** (API, WebSocket gateway, notification worker) and 2 permissions each.
3. Explain how you’d rotate credentials if a service’s cloud role was over-permissioned and possibly abused.

---

## 11. How OAuth2 works (add-on)

> **OAuth2 is a delegated authorization framework.** It lets an app access a user’s resources **without** taking the user’s password — the user grants limited permission via an **Authorization Server**, and the app gets a short-lived **access token**.

### Roles (memorize these 4)


| Role                     | Who                                 | Example                                  |
| ------------------------ | ----------------------------------- | ---------------------------------------- |
| **Resource Owner**       | The user                            | Alice                                    |
| **Client**               | The app asking for access           | Your mobile app / web frontend / backend |
| **Authorization Server** | Issues tokens after login + consent | Google, GitHub, Auth0, Cognito, Okta     |
| **Resource Server**      | API that holds the data             | Google Drive API, your `/orders` API     |


### Core idea

```text
  Alice wants "MyApp" to read her Google Drive files
       │
       ▼
  MyApp redirects Alice → Authorization Server (Google)
       │
       ▼
  Alice logs in + consents ("Allow read access")
       │
       ▼
  Auth Server redirects back with a short-lived code (or token)
       │
       ▼
  MyApp exchanges code → Access Token (+ optional Refresh Token)
       │
       ▼
  MyApp calls Drive API with:  Authorization: Bearer <access_token>
```

MyApp **never sees Alice’s Google password**. It only gets a scoped token.

### Important terms


| Term                   | Meaning                                                                |
| ---------------------- | ---------------------------------------------------------------------- |
| **Authorization Code** | One-time code returned to the client after consent (browser flow)      |
| **Access Token**       | Short-lived credential the API accepts (often opaque or JWT)           |
| **Refresh Token**      | Longer-lived secret used to get **new** access tokens without re-login |
| **Scope**              | What the token is allowed to do (`openid`, `email`, `drive.readonly`)  |
| **Redirect URI**       | Where the Auth Server sends the user back (must be pre-registered)     |
| **Client ID / Secret** | App identity; secret only on confidential clients (backends), not SPAs |


### Most common flow: Authorization Code (+ PKCE)

Used by web and mobile apps today.

```text
  1. Client redirects browser to /authorize
       ?client_id=...
       &redirect_uri=...
       &scope=openid profile
       &state=random          ← CSRF protection
       &code_challenge=...    ← PKCE (stops code interception)

  2. User logs in + consents

  3. Auth Server redirects to redirect_uri?code=...&state=...

  4. Client POSTs to /token
       code + code_verifier (+ client_secret if confidential)
       → access_token, expires_in, refresh_token?, id_token?

  5. Client calls APIs with Bearer access_token
```

**PKCE** (Proof Key for Code Exchange): public clients (mobile/SPA) prove they are the same app that started login — required in modern OAuth2.

### Other flows (know when to name them)


| Flow                            | Use when                    | Avoid when              |
| ------------------------------- | --------------------------- | ----------------------- |
| **Authorization Code (+ PKCE)** | User login for apps         | — (default choice)      |
| **Client Credentials**          | Service-to-service, no user | Need user identity      |
| **Device Code**                 | TVs / CLIs                  | Normal web apps         |
| **Implicit**                    | Legacy SPAs                 | Prefer Auth Code + PKCE |


### OAuth2 vs OpenID Connect (OIDC)


|                   | OAuth2                          | OIDC (on top of OAuth2)                    |
| ----------------- | ------------------------------- | ------------------------------------------ |
| Goal              | **Authorization** — access APIs | **Authentication** — prove who the user is |
| Main token        | Access token                    | **ID Token** (JWT with `sub`, email, etc.) |
| Question answered | “Can this app call that API?”   | “Who logged in?”                           |


**Interview line:**  

> “OAuth2 authorizes access; OIDC adds login identity via an ID token. For ‘Sign in with Google’ I use OIDC (Auth Code + PKCE).”

### How this fits IAM / distributed systems

```text
  User ──OIDC login──► IdP (Auth Server)
                           │
                    access_token / id_token
                           │
                           ▼
  API Gateway validates JWT ──► services trust claims (sub, roles, tenant)
                           │
                           ▼
  Downstream: services use their own IAM roles for AWS/DB;
              user token only for “on behalf of user” calls
```

- **Access token** → AuthZ at your APIs (scopes / claims)  
- **IAM roles** → still used for service → cloud resource access  
- Don’t put long-lived refresh tokens in localStorage if you can use secure httpOnly cookies / BFF pattern

### Security checklist (senior signal)

1. Use **Authorization Code + PKCE**; avoid Implicit
2. Validate `state`, redirect URI exact match, token **audience** + **issuer** + expiry
3. Least-privilege **scopes**
4. Short-lived access tokens; rotate / revoke refresh tokens
5. Confidential clients keep `client_secret` on the server only

### Interview trigger phrase

> “OAuth2 lets a client get a scoped access token from an authorization server after user consent — typically Auth Code + PKCE. OIDC adds an ID token for authentication. Our APIs validate the JWT; workloads still use IAM roles for cloud permissions.”

