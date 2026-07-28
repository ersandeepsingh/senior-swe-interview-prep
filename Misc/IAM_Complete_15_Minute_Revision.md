# IAM Complete Revision Guide

> A concise revision guide covering general IAM concepts, authentication, authorization, OAuth, OIDC, SSO, service identities, and AWS IAM.

---

## 1. IAM in One Sentence

**Identity and Access Management (IAM)** controls:

1. **Who** is requesting access
2. **How** their identity is verified
3. **What** actions they can perform
4. **Which** resources they can access
5. **Under what conditions**
6. **How their activity is audited**

A useful mental model:

```text
Identity -> Authentication -> Authorization -> Resource -> Audit
```

---

# Part 1: IAM Foundations

## 2. Identity, Principal, Credential, and Account

### Identity

An entity known to a system.

Examples:

- Human employee
- Customer
- Backend service
- Mobile application
- Server
- Device
- External partner

### Principal

An identity currently making a request.

```text
Principal: order-service
Action: Read
Resource: orders database
```

### Account

The representation of an identity inside a particular system.

One person may have separate accounts in Google Workspace, GitHub, Jira, AWS, and other systems.

### Identifier

Tells the system which identity is being claimed.

```text
Email: sandeep@company.com
Username: sandeep
Client ID: reporting-service
```

### Credential

Proof used to verify the identity.

Examples:

- Password
- OTP
- Passkey
- API key
- Certificate and private key
- Access token

```text
Identifier: sandeep@company.com
Credential: password + security key
```

---

## 3. Authentication vs Authorization

### Authentication

Answers:

> Who are you?

Examples:

- Password verification
- OTP verification
- Passkey challenge
- Certificate validation
- Token validation

### Authorization

Answers:

> What are you allowed to do?

Example:

```text
Authenticated user: Sandeep
Allowed: Read own orders
Denied: Read another customer's orders
```

### HTTP status codes

- **401 Unauthorized:** Authentication is missing or invalid
- **403 Forbidden:** Identity is known, but permission is denied

### AAA model

```text
Authentication -> Who are you?
Authorization  -> What can you do?
Accounting     -> What did you do?
```

---

## 4. Human and Workload Identities

### Human identity

Used by employees, customers, administrators, contractors, and partners.

Usually authenticated using:

- Password
- MFA
- Passkey
- Enterprise SSO

### Workload identity

Used by software.

Examples:

- `order-service`
- CI/CD pipeline
- Kubernetes pod
- Lambda function
- Scheduled job

A workload should not use a developer's personal credentials.

Bad:

```text
Deployment pipeline -> developer password
```

Good:

```text
Deployment pipeline -> dedicated workload identity -> limited deployment permission
```

---

## 5. Service Accounts

A **service account** is a non-human identity used by software or automation.

Used in:

- Kubernetes pods
- CI/CD pipelines
- Backend services
- Database connections
- Scheduled jobs
- Cloud applications

Best practices:

- Use one identity per application or workload
- Grant least privilege
- Avoid shared service accounts
- Avoid hardcoded credentials
- Prefer temporary credentials
- Rotate credentials automatically
- Audit all usage

Cloud terminology:

| Platform | Typical workload identity |
|---|---|
| Google Cloud | Service Account |
| Azure | Managed Identity / Service Principal |
| AWS | IAM Role |
| Kubernetes | Kubernetes ServiceAccount |

---

# Part 2: Authentication

## 6. Authentication Factors and MFA

Authentication factors:

| Factor | Meaning | Example |
|---|---|---|
| Something you know | Secret knowledge | Password, PIN |
| Something you have | Possession | Phone, security key |
| Something you are | Biometric | Fingerprint, face |
| Somewhere you are | Location signal | Office network |
| Something you do | Behaviour | Typing pattern |

### MFA

MFA requires factors from different categories.

```text
Password + security question = Not true MFA
Password + authenticator app = MFA
Password + hardware key = Strong MFA
```

### Authentication strength

Approximate order:

```text
Password only
< Password + SMS OTP
< Password + authenticator OTP
< Passkey or hardware security key
```

### Important terms

- **Step-up authentication:** Request stronger proof for a sensitive action
- **Reauthentication:** Ask an already logged-in user to authenticate again
- **Risk-based authentication:** Change requirements based on device, location, behaviour, and risk
- **Phishing-resistant authentication:** Credentials cannot easily be reused on a fake site

---

## 7. Passkeys

Passkeys use public-key cryptography.

```text
Private key -> Remains on the user's device
Public key  -> Stored by the application
```

Login flow:

```text
Server sends challenge
-> Device signs challenge with private key
-> Server verifies signature using public key
```

Benefits:

- No reusable password sent to the server
- Resistant to phishing
- Resistant to credential stuffing
- Private key stays on the device

---

## 8. Password Storage

Never store passwords in plaintext or reversible encrypted form.

Use a password-hashing algorithm:

- Argon2id
- scrypt
- bcrypt
- PBKDF2

Avoid fast general-purpose hashes such as plain SHA-256 for password storage.

### Salt

A random value unique to each password.

```text
hash(password + unique salt)
```

Purpose:

- Same passwords produce different hashes
- Reduces usefulness of precomputed attacks

The salt is not secret and may be stored with the hash.

### Pepper

An optional shared secret stored separately from the password database.

```text
hash(password + salt + pepper)
```

### Online vs offline attacks

- **Online attack:** Guesses sent to the real login API
  - Defences: rate limiting, MFA, delays, risk detection
- **Offline attack:** Stolen hashes cracked on attacker hardware
  - Defences: slow password hashing, salts, strong passwords

### Common password attacks

- Brute force
- Dictionary attack
- Credential stuffing
- Password spraying
- User enumeration

---

## 9. Session-Based Authentication

After login, the server creates a session.

```text
Login -> Session created -> Session ID sent in cookie
```

The browser stores a random session ID, while session data remains server-side.

```text
session_id -> user_id, expiry, MFA state, roles
```

Important cookie settings:

```text
Secure   -> Send only over HTTPS
HttpOnly -> JavaScript cannot directly read it
SameSite -> Restricts cross-site sending
```

### Session security

- Use random, unpredictable session IDs
- Rotate session ID after login or privilege changes
- Apply idle and absolute timeouts
- Invalidate server-side session on logout
- Revoke all sessions after suspected compromise

### Common attacks

- **Session hijacking:** Attacker steals a valid session ID
- **Session fixation:** Victim logs in using a session ID already known to attacker
- **CSRF:** Browser automatically sends an authenticated cookie for an unwanted request
- **XSS:** Malicious JavaScript executes inside the trusted application

---

## 10. Token-Based Authentication

After authentication, a client receives a token and sends it with future API requests.

```http
Authorization: Bearer <access-token>
```

### Bearer token

Whoever possesses it can normally use it.

### Opaque token

A random value requiring a server-side lookup or introspection.

Advantages:

- Easy revocation
- Contents hidden

### Self-contained token

Carries claims and can often be validated locally. JWT is the common example.

### Access and refresh tokens

| Token | Purpose | Typical lifetime |
|---|---|---|
| Access token | Call an API | Short |
| Refresh token | Obtain new access tokens | Longer |

Refresh tokens should be strongly protected and preferably rotated.

### Important token checks

- Trusted issuer
- Correct audience
- Expiration
- Signature or token validity
- Required scope
- Correct token type

---

## 11. JWT

A JWT commonly contains:

```text
Header.Payload.Signature
```

### Header

Describes the signing method and key.

```json
{
  "alg": "RS256",
  "kid": "key-1"
}
```

### Payload

Contains claims.

```json
{
  "iss": "https://identity.example.com",
  "sub": "user-123",
  "aud": "orders-api",
  "scope": "orders:read",
  "exp": 1785042000
}
```

### Signature

Protects integrity and proves that a trusted signing key created the token.

### Important claims

| Claim | Meaning |
|---|---|
| `iss` | Issuer |
| `sub` | Subject or principal |
| `aud` | Intended recipient API/client |
| `exp` | Expiration time |
| `iat` | Issued-at time |
| `nbf` | Not valid before |
| `jti` | Unique token ID |

### Critical JWT rules

- Base64URL is encoding, not encryption
- Never trust decoded claims without signature validation
- Explicitly allow expected algorithms
- Validate `iss`, `aud`, and `exp`
- Do not put secrets in a normal signed JWT
- Do not use an ID token as an API access token
- Keep access tokens short-lived

---

# Part 3: OAuth, OIDC, SSO, and Federation

## 12. OAuth 2.0

OAuth is primarily a framework for **delegated authorization**.

It allows an application to access an API on behalf of a user without receiving the user's password.

Example:

```text
Calendar app requests calendar.read
-> User approves
-> Authorization server issues access token
-> Calendar app calls Calendar API
```

### OAuth roles

| Role | Meaning |
|---|---|
| Resource Owner | Usually the user |
| Client | Application requesting access |
| Authorization Server | Issues tokens |
| Resource Server | Protected API |

### Authorization Code Flow

```text
1. Client redirects user to authorization server
2. User authenticates and approves access
3. Authorization server returns an authorization code
4. Client exchanges code at token endpoint
5. Client receives access token
6. Client calls API
```

### Important protections

- **State:** Protects browser flow and correlates the response
- **PKCE:** Protects the authorization code exchange
- **Redirect URI validation:** Prevents codes being sent to attacker-controlled locations

### Client types

- **Confidential client:** Backend that can protect a secret
- **Public client:** Mobile app, SPA, desktop app; cannot reliably protect a secret

Public clients should use Authorization Code Flow with PKCE.

### Common OAuth grants

- Authorization Code
- Client Credentials
- Device Authorization
- Refresh Token

Avoid obsolete patterns such as password grant and implicit grant in modern systems.

---

## 13. OIDC

OpenID Connect adds an authentication layer on top of OAuth 2.0.

```text
OAuth -> What can the application access?
OIDC  -> Who logged in?
```

OIDC introduces the **ID token**, usually a JWT.

### ID token vs access token

| ID token | Access token |
|---|---|
| Describes authentication and user identity | Used to call an API |
| Audience is the client application | Audience is the resource API |
| Used by the client | Used by the resource server |

OIDC requests include:

```text
scope=openid
```

OIDC also uses a **nonce** to protect against replay of authentication responses.

---

## 14. SSO and Federation

### Single Sign-On

Log in once and access multiple applications.

```text
Company login -> Gmail, Slack, Jira, AWS
```

### Federation

One system trusts another system to authenticate users.

```text
Company Identity Provider -> Confirms employee identity -> AWS trusts it
```

### Components

- **Identity Provider (IdP):** Authenticates users
- **Service Provider (SP):** Application being accessed

SSO is the user experience; federation is the trust relationship enabling it.

---

## 15. SAML

SAML is an XML-based protocol commonly used for enterprise web SSO.

```text
User -> Service Provider -> Identity Provider
-> Signed SAML assertion -> Service Provider
```

The SAML assertion may include:

- User identity
- Email
- Groups
- Roles
- Authentication information

### SAML vs OIDC

| SAML | OIDC |
|---|---|
| XML-based | JSON/JWT-based |
| Common in older enterprise web SSO | Common in modern web/mobile systems |
| Browser-centric | API-friendly |

---

# Part 4: Machine and Service Authentication

## 16. API Keys

An API key is a secret value identifying an application or integration.

```http
X-API-Key: abc123
```

Weaknesses:

- Often long-lived
- Easy to copy
- Commonly hardcoded
- Frequently over-permissioned

Use API keys only where appropriate and rotate them regularly.

---

## 17. Certificates and mTLS

A certificate binds an identity to a public key and is signed by a trusted Certificate Authority.

Each service has:

```text
Private key -> Kept secret
Certificate -> Contains identity and public key
```

### Normal TLS

The client verifies the server.

### Mutual TLS

Both client and server verify one another.

```text
order-service <-> payment-service
Both present and validate certificates
```

mTLS provides:

- Encryption
- Server authentication
- Client authentication

mTLS does not automatically provide authorization.

```text
Authenticated: order-service
Authorization check: Is order-service allowed to issue refunds?
```

Main operational challenges:

- Certificate issuance
- Rotation
- Expiration
- Revocation
- Private-key protection
- Trust-store distribution

Service meshes such as Istio or Linkerd can automate mTLS between workloads.

---

# Part 5: Authorization Models

## 18. ACL, RBAC, ABAC, and ReBAC

### ACL

Permissions attached directly to a resource.

```text
File A:
- Sandeep: read
- Priya: write
```

### RBAC

Permissions assigned to roles; users receive roles.

```text
Role: Developer
Permissions: Read logs, deploy to staging
```

### ABAC

Access based on attributes.

```text
Allow when user.department == resource.department
```

Attributes can include:

- Department
- Team
- Region
- Environment
- Resource tags

### ReBAC

Access based on relationships.

```text
Allow edit when user is owner or member of owning team
```

### Policy-Based Access Control

Access decisions come from written rules or policy documents. AWS IAM is mainly policy-based and can implement RBAC and ABAC patterns.

---

## 19. Policy Evaluation

A common policy evaluation model:

```text
1. Start with implicit deny
2. Look for a matching allow
3. Check for explicit deny
4. Explicit deny wins
```

```text
Allow + Explicit Deny = Deny
```

Permissions may come from:

- User policy
- Group membership
- Role
- Resource policy
- Organization policy
- Session restrictions

---

## 20. Multi-Tenant Authorization

A multi-tenant system serves multiple organisations.

Every request must enforce tenant isolation.

```json
User token:
{
  "sub": "user-123",
  "tenant_id": "company-a"
}

Resource:
{
  "order_id": "order-999",
  "tenant_id": "company-a"
}
```

Required check:

```text
principal.tenant_id == resource.tenant_id
```

Being authenticated is not enough. Every data query and authorization check must include tenant context.

---

# Part 6: Identity Lifecycle and Governance

## 21. Joiner, Mover, Leaver

### Joiner

- Create identity
- Assign required groups and roles
- Register MFA
- Grant minimum necessary access

### Mover

- Remove old permissions
- Add new permissions
- Review privileged access

A common mistake is adding new access without removing old access.

### Leaver

- Disable account
- Revoke sessions and tokens
- Remove API keys
- Remove application access
- Transfer ownership

### SCIM

SCIM is commonly used to automate user and group provisioning.

```text
HR system -> Identity Provider -> Slack, Jira, GitHub
```

```text
SCIM      -> Account provisioning and deprovisioning
SAML/OIDC -> Login and SSO
```

---

## 22. Privileged Access and JIT

Privileged access includes actions such as:

- Managing identities
- Changing policies
- Reading secrets
- Deleting production resources

Prefer **Just-in-Time (JIT)** access:

```text
Developer requests production access
-> Approval
-> Admin access granted for 30 minutes
-> Access automatically expires
```

This is safer than permanent administrator access.

---

## 23. Zero Trust

Zero Trust means:

> Do not trust based only on network location. Verify every request.

A decision may consider:

- User identity
- Workload identity
- Device security
- Authentication strength
- Location
- Requested action
- Resource sensitivity
- Risk signals

---

## 24. Auditing and Access Reviews

Audit logs should record:

- Actor
- Action
- Resource
- Time
- IP/device
- Success or failure
- Role or session used

Monitor for:

- Repeated failed logins
- Unusual countries or devices
- Privileged actions
- Large data downloads
- Permission changes
- Disabled-account activity

Access reviews answer:

> Does this user or service still need this permission?

---

# Part 7: AWS IAM

## 25. AWS IAM Identities

### Root user

The AWS account root user has complete account access.

Best practices:

- Enable MFA
- Do not use for daily work
- Do not create root access keys
- Use only for rare account-level tasks

### IAM user

A long-term identity with password or access keys.

Prefer federation and temporary roles for employees instead of creating many IAM users.

### IAM group

A collection of IAM users.

```text
Developers Group
-> Sandeep
-> Priya
-> Rahul
```

Policies attached to the group are inherited by members.

Groups cannot contain roles or nested groups.

### IAM role

An identity that is assumed temporarily and normally has no permanent credentials.

Used by:

- Employees through SSO
- EC2
- Lambda
- ECS tasks
- EKS pods
- Other AWS accounts
- External vendors

---

## 26. Group, Role, and Policy Relationship

```text
Policy = Defines permissions
Group  = Organizes IAM users
Role   = Temporary identity that can be assumed
```

### Group flow

```text
Policy -> Group -> IAM users inherit permissions
```

### Role flow

```text
Policy -> Role -> User or application assumes role -> Temporary permissions
```

A user may belong to a group and also assume a role.

```text
Sandeep
-> Developers group for regular access
-> ProductionSupportRole for temporary production access
```

---

## 27. AWS IAM Policies

Example:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::company-reports/*"
    }
  ]
}
```

Main fields:

| Field | Meaning |
|---|---|
| `Effect` | Allow or Deny |
| `Action` | AWS API action |
| `Resource` | Resource ARN |
| `Condition` | Optional restrictions |
| `Principal` | Who is allowed, mainly in resource/trust policies |

AWS starts with implicit deny. A matching allow is required, and an explicit deny overrides allow.

---

## 28. Identity-Based and Resource-Based Policies

### Identity-based policy

Attached to:

- IAM user
- IAM group
- IAM role

Answers:

> What can this identity do?

### Resource-based policy

Attached directly to a resource.

Examples:

- S3 bucket policy
- SQS queue policy
- KMS key policy
- Lambda resource policy

Answers:

> Who can access this resource?

Resource-based policies are important for cross-account access and service-to-service access.

---

## 29. Assuming an AWS Role

When a user or application assumes a role, AWS STS issues temporary credentials.

```text
Caller -> sts:AssumeRole -> STS -> Temporary credentials
```

Temporary credentials contain:

- Access Key ID
- Secret Access Key
- Session Token
- Expiration

### Two important policy types

#### Trust policy

Defines who may assume the role.

```text
Who can enter this role?
```

#### Permissions policy

Defines what the role can do after assumption.

```text
What can the role do?
```

For user-initiated role assumption, both usually matter:

1. Caller is allowed to call `sts:AssumeRole`
2. Role trust policy trusts the caller

---

## 30. AWS STS

AWS Security Token Service issues temporary credentials.

Benefits:

- Automatically expire
- Reduce long-lived key exposure
- Support cross-account access
- Support federation
- Support workload identities

Applications using temporary credentials must send the session token along with the access key and secret key.

---

## 31. AWS Workload Roles

### EC2

```text
EC2 instance -> Instance Profile -> IAM Role
```

AWS SDK obtains credentials from the instance metadata service.

### Lambda

```text
Lambda function -> Execution Role
```

### ECS

```text
ECS task -> Task Role
```

Use a task role for the application, not the ECS execution role for application permissions.

### EKS

```text
Kubernetes Pod -> Kubernetes ServiceAccount -> IAM Role
```

Use EKS Pod Identity or IRSA so pods do not inherit broad worker-node permissions.

Best practice:

```text
One workload -> One role -> Minimum required permissions
```

---

## 32. Cross-Account Access

An identity in Account A assumes a role in Account B.

```text
Account A identity -> AssumeRole -> Role in Account B -> Account B resources
```

The role is created in the **target account**.

Required:

1. Source identity can call `sts:AssumeRole`
2. Target role trust policy trusts the source identity/account

### External ID

Used especially when a third-party vendor assumes a role in your account. It helps prevent the confused deputy problem.

---

## 33. IAM Identity Center

IAM Identity Center provides central workforce access to multiple AWS accounts.

```text
Employee -> Company IdP -> IAM Identity Center -> AWS accounts
```

It avoids creating separate IAM users in every account.

### Permission set

Defines the permissions a user or group receives in selected AWS accounts.

IAM Identity Center provisions roles in those accounts and provides temporary credentials.

Benefits:

- Central SSO
- Temporary credentials
- Multi-account access
- Easier onboarding and offboarding

---

## 34. Permission Boundaries and Session Policies

### Permission boundary

Defines the maximum permissions an IAM user or role may receive.

```text
Final identity permissions = Identity policy ∩ Permission boundary
```

A boundary does not grant access by itself.

### Session policy

Further limits one temporary role session.

```text
Role permissions: Read and write S3
Session policy: Read only
Final session: Read only
```

---

## 35. AWS Organizations and SCPs

AWS Organizations manages multiple AWS accounts.

### Service Control Policy

An SCP defines the maximum permissions available to principals in member accounts.

Example:

```text
Deny disabling CloudTrail
```

Even an account administrator is blocked if the SCP denies the action.

Important:

- SCPs do not grant permissions
- IAM permissions still need to allow the action
- Explicit deny in an SCP wins

### Resource Control Policy

RCPs restrict access to supported resources through resource-based permissions.

Simple distinction:

```text
SCP -> Limits principals in accounts
RCP -> Limits access to supported resources
```

---

## 36. AWS ABAC Using Tags

AWS ABAC uses tags on principals and resources.

```text
Principal tag: team=payments
Resource tag: team=payments
```

Policy idea:

```text
Allow when principal.team == resource.team
```

Benefits:

- Fewer policies
- Easier scaling across teams and projects
- Dynamic permissions based on tags

Security warning:

Users must not be allowed to freely change security-sensitive tags on themselves or resources.

---

## 37. AWS Auditing and Troubleshooting

### CloudTrail

Records AWS API activity.

Use it to answer:

- Who performed the action?
- Which role or session was used?
- Which resource was affected?
- Was the action successful?

### IAM Access Analyzer

Helps identify unintended external or public access and can assist with policy analysis.

### Policy Simulator

Tests whether a particular principal, action, and resource combination is allowed or denied.

### Access-denied checklist

When AWS returns `AccessDenied`, check:

1. Does an identity policy allow the action?
2. Is there an explicit deny?
3. Does the resource policy allow or block access?
4. Is the resource ARN correct?
5. Are policy conditions satisfied?
6. Is an SCP blocking the action?
7. Is a permission boundary limiting it?
8. Is a session policy limiting it?
9. For role assumption, does the trust policy allow it?
10. For KMS, does the key policy permit it?

---

# Final Revision Cheat Sheet

## Core IAM

```text
Identity       -> Who or what exists?
Principal      -> Who is making the request?
Credential     -> How is identity proved?
Authentication -> Who are you?
Authorization  -> What can you do?
Audit          -> What did you do?
```

## Authentication

```text
Password -> Store with Argon2id/bcrypt + unique salt
MFA      -> Use independent factors
Passkey  -> Public/private key, phishing-resistant
Session  -> Server-side state, cookie carries session ID
Token    -> Temporary API credential
JWT      -> Signed claims format, not encryption
```

## OAuth and OIDC

```text
OAuth -> Delegated API authorization
OIDC  -> User authentication on top of OAuth
Access token -> Sent to API
ID token     -> Used by client to identify authenticated user
PKCE         -> Protects authorization-code exchange
state        -> Protects browser flow
```

## Authorization Models

```text
ACL   -> Per-resource user permissions
RBAC  -> Permissions through roles
ABAC  -> Permissions through attributes
ReBAC -> Permissions through relationships
```

## AWS IAM

```text
IAM user  -> Long-term identity
IAM group -> Collection of IAM users
IAM role  -> Temporary assumable identity
Policy    -> Defines permissions
STS       -> Issues temporary credentials
Trust policy -> Who can assume role?
Permission policy -> What can role do?
```

## AWS Permission Evaluation

```text
Implicit deny by default
Matching allow is required
Explicit deny always wins
SCPs and boundaries limit maximum access
```

## Production Best Practices

1. Prefer federation and IAM Identity Center for employees
2. Prefer roles and temporary credentials for workloads
3. Avoid hardcoded access keys
4. Apply least privilege
5. Enable MFA for privileged access
6. Use separate AWS accounts for production and development
7. Use short-lived access and JIT elevation
8. Protect and rotate credentials
9. Audit with CloudTrail
10. Review permissions regularly
11. Revoke access immediately when users or services are decommissioned
12. Treat authentication and authorization as separate checks

---

# 10 Quick Interview Questions

1. **Authentication vs authorization?**  
   Authentication verifies identity; authorization checks permissions.

2. **OAuth vs OIDC?**  
   OAuth grants API access; OIDC authenticates the user.

3. **Access token vs ID token?**  
   Access token is for APIs; ID token is for the client application.

4. **Why use PKCE?**  
   It prevents a stolen authorization code from being exchanged by another client.

5. **What is a service account?**  
   A non-human identity used by software or automation.

6. **Normal TLS vs mTLS?**  
   Normal TLS authenticates the server; mTLS authenticates both client and server.

7. **IAM group vs IAM role?**  
   Group contains IAM users; role is temporarily assumed by a user or workload.

8. **Trust policy vs permissions policy?**  
   Trust policy defines who can assume a role; permissions policy defines what it can do.

9. **What does an SCP do?**  
   It limits the maximum permissions available in member AWS accounts; it does not grant permissions.

10. **Why are temporary AWS credentials safer?**  
    They expire automatically and reduce the risk of long-lived key leakage.

---

## Final Mental Model

```text
User or Workload
      |
      | proves identity
      v
Authentication System
      |
      | creates session or token
      v
Application / API
      |
      | evaluates role, policy, attributes, resource and context
      v
Allow or Deny
      |
      v
Audit Log
```
