# 9. Security ⭐

Identity, access, and protecting data in motion and at rest. Seniors separate **AuthN vs AuthZ**, speak clearly about **OAuth/JWT**, and treat **OWASP** and secrets as design constraints — not afterthoughts.

| # | Topic | One-line intent |
|---|-------|-----------------|
| 01 | [AuthN vs AuthZ](01_authn_vs_authz.md) | Identity vs permissions |
| 02 | [OAuth 2.0 / OIDC](02_oauth_oidc.md) | Flows, tokens, scopes, third-party auth |
| 03 | [JWT](03_jwt.md) | Structure, signing, expiry, refresh, pitfalls |
| 04 | [RBAC / ABAC](04_rbac_abac.md) | Role- vs attribute-based access control |
| 05 | [OWASP Top 10](05_owasp_top_10.md) | Injection, XSS, CSRF, SSRF, broken auth |
| 06 | [Encryption](06_encryption.md) | Symmetric/asymmetric, hashing, KMS |
| 07 | [Secrets management](07_secrets_management.md) | Vault, rotation, never in code |
| 08 | [Rate limiting & DDoS](08_rate_limiting_ddos.md) | Throttling, WAF |
| 09 | [Input validation](09_input_validation.md) | Trust boundaries, sanitization |

**How to use:** For each file — read Plain English → example → trade-offs → say the interview trigger phrase out loud → do the Exercise without peeking.
