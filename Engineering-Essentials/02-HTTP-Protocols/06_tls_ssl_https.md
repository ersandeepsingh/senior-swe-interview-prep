# TLS/SSL & HTTPS

> **TLS** encrypts and authenticates the connection so HTTPS is HTTP over a secure channel — eavesdroppers can’t read or easily tamper with traffic.

## Plain English

**SSL** is the old name; **TLS** is what we use now. HTTPS = HTTP over TLS. The server proves its identity with a certificate; then traffic is encrypted. **mTLS** adds client certificates for service identity.

## Essentials (must-know for this topic)

### Handshake in 4 beats (TLS 1.3 era)

| Step | What happens |
|------|----------------|
| 1 | Client connects; server presents **certificate** (domain ↔ public key, CA-signed) |
| 2 | Client verifies chain + hostname (SAN) |
| 3 | Agree on keys (TLS 1.3 = fewer round trips) |
| 4 | HTTP (or other) data flows encrypted |

### Vocab

| Term | Meaning |
|------|---------|
| **TLS** | Transport Layer Security (current) |
| **SSL** | Legacy name — avoid saying “we use SSL” as the whole story |
| **Certificate / CA** | Binds identity; trust anchored at Certificate Authorities |
| **SAN** | Subject Alternative Name — hostnames the cert covers |
| **mTLS** | Mutual TLS — client also presents a cert |
| **Termination** | LB decrypts TLS; backend may see HTTP on private network |

### HTTPS vs mTLS vs token auth

| Mechanism | Proves | Common where |
|-----------|--------|--------------|
| **HTTPS (server TLS)** | Server identity + encryption | Public web |
| **mTLS** | Client **and** server identity | Service mesh / internal APIs |
| **JWT / API keys** | Application-level caller | After TLS is up |

### Ops must-knows

| Topic | Interview line |
|-------|----------------|
| Expiry | Automate renewal (ACM, Let’s Encrypt) or outage |
| Rotation | Plan for SAN/cert swaps without pinning forever |
| Trust boundary | Know where TLS ends (edge vs hop-by-hop) |

## Why seniors get asked

Security and infra interviews expect handshake intuition, mTLS vs token auth, and how broken certs fail in production.

## Simple example

```bash
# Inspect certificate
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null | openssl x509 -noout -dates -subject

curl -vI https://example.com 2>&1 | grep -E "SSL|TLS|subject|expire"
```

mTLS sketch: sidecar/service mesh presents client cert; server rejects connections without a trusted client CA.

## When to use / when not / trade-offs

| Use | Notes |
|-----|-------|
| HTTPS everywhere public | Non-negotiable |
| mTLS inside mesh | Strong service identity; operational cost |
| TLS termination at LB | App sees HTTP on private network — know the trust boundary |

**Trade-offs:** TLS adds CPU and handshake latency (mitigated by session resumption / TLS 1.3); mTLS is secure but painful to rotate and debug.

## Common pitfalls

- Certificates expired / wrong SAN (hostname mismatch)
- Terminating TLS then sending cleartext across an untrusted network without noticing
- Pinning certs too hard → breakage on rotation
- Calling it “SSL” and stopping at “we use HTTPS” with no revocation/rotation story

## Interview trigger phrase

> “HTTPS is TLS: verify server cert, encrypt the session; for service identity I’d consider mTLS and automate cert rotation.”

## Exercise

Users see `NET::ERR_CERT_DATE_INVALID`. Name two operational causes and how you’d prevent recurrence. When would you choose mTLS over only JWT between services?
