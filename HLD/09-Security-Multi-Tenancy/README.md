# 9. Security & Multi-Tenancy

Keep attackers and noisy neighbors out of the critical path story. Interviewers expect you to **separate authn vs authz**, name **encryption layers**, harden the **API edge**, and pick a **tenant isolation** model with explicit trade-offs.

| # | Concept | One-line intent |
|---|---------|-----------------|
| 01 | [Authn & Authz](01_authn_authz.md) | OAuth2 / JWT / RBAC — who you are vs what you can do |
| 02 | [Encryption](02_encryption.md) | TLS in transit, encryption at rest, KMS |
| 03 | [API security](03_api_security.md) | Rate limits, input validation, WAF |
| 04 | [Multi-tenancy isolation](04_multi_tenancy_isolation.md) | Shared vs isolated; per-tenant limits |

**How to use:** For each file — read Plain English → diagram → trade-offs → say the interview trigger phrase out loud → do the Exercise without peeking at notes.
