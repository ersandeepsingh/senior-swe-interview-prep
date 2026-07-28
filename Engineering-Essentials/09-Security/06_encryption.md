# Encryption

> **Encryption** protects confidentiality of data. Know **symmetric vs asymmetric**, **hashing vs encryption**, **in transit vs at rest**, and **KMS** for key management. Seniors don’t invent crypto — they use vetted libraries and managed keys.

## Plain English

| Concept | Meaning |
|---------|---------|
| **Symmetric** (AES) | Same key encrypts/decrypts — fast, bulk data |
| **Asymmetric** (RSA/EC) | Public encrypt / private decrypt (or sign/verify) |
| **Hashing** (SHA-256, bcrypt/argon2) | One-way fingerprint — not encryption |
| **In transit** | TLS on the wire |
| **At rest** | Disk/S3/DB volume encryption; app-level field encryption |
| **KMS** | Managed key service; apps get data keys / encrypt APIs |

```text
  TLS:     Client ──encrypted──► Server   (in transit)
  At rest: Disk/S3 encrypted with KMS-managed keys
  Passwords: hash+salt with argon2/bcrypt — NEVER encrypt reversibly
```

## Essentials (must-know for this topic)

### Symmetric vs asymmetric vs hashing

| Concept | Keys | Use |
|---------|------|-----|
| **Symmetric** (AES) | Same key encrypt/decrypt | Bulk data, speed |
| **Asymmetric** (RSA/EC) | Public/private pair | Key exchange, sign/verify, small secrets |
| **Hashing** (SHA-256, argon2) | One-way | Integrity; **passwords** (salted slow hash) |

### In transit vs at rest

| Where | Typical control |
|-------|-----------------|
| **In transit** | TLS (HTTPS); mTLS for service identity |
| **At rest** | Disk/S3/DB encryption; optional app-level field encryption |
| **Key management** | **KMS** — don’t hard-code keys |

### Envelope encryption (name it)

| Step | Idea |
|------|------|
| 1 | KMS provides/wraps a **data key** |
| 2 | Encrypt payload with AES data key |
| 3 | Store ciphertext + encrypted data key |
| 4 | On read: KMS unwraps data key → decrypt |

**Never** “encrypt” passwords — **hash** with argon2/bcrypt.

## Simple example

**Envelope encryption:**

```text
  KMS generates data key → encrypt file with AES data key
  Store encrypted file + encrypted data key
  On read: KMS decrypts data key → decrypt file
```

**TLS:** HTTPS everywhere; consider **mTLS** for service-to-service identity.

## When to use / trade-offs

| Prefer **TLS + disk encryption** when… | Prefer **app-level field encryption** when… |
|----------------------------------------|---------------------------------------------|
| Default baseline | Specific columns must stay secret from DBAs/backups readers |
| Compliance checkbox “encrypted” | You need per-tenant keys / crypto shredding |

| Prefer **managed KMS** when… | Prefer **local keys** when… |
|------------------------------|-----------------------------|
| Almost always in cloud | Air-gapped / special constraints |
| Audit + rotation helpers | You can secure key storage better (rare) |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Encrypt everything at rest | Breach cushion | Key management duty |
| Client-side encryption | Provider can’t read | Search/index harder |
| Custom crypto | — | Almost always lose |

## Pitfalls

- Rolling your own crypto protocols.  
- ECB mode / reused IVs / hard-coded keys.  
- “Encrypting” passwords instead of **hashing**.  
- Storing private keys in the repo.  
- Thinking HTTPS alone protects **stolen disk backups** without at-rest keys secured.

## Interview trigger phrase

> “I’d use **TLS in transit**, **KMS-backed encryption at rest**, **argon2/bcrypt for passwords**, and **envelope encryption** for sensitive fields — never home-grown ciphers.”

## Exercise

**Store customer SSNs / national IDs.**

1. Hash, encrypt, or tokenize — which and why?  
2. Who can decrypt, and how do you rotate keys?  
3. DB dump leaks — what is still protected if you did it right?
