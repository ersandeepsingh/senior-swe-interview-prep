# Encryption

> Encrypt **in transit** (TLS) so the network can’t read traffic. Encrypt **at rest** so stolen disks/backups aren’t plaintext. Use a **KMS** so app servers never hard-code master keys — they request data keys and leave key custody to a vault.

## Plain English

| Layer | Protects against | Typical tech |
|-------|------------------|--------------|
| **TLS (in transit)** | Sniffing on the wire / Wi-Fi | HTTPS, mTLS between services |
| **At rest** | Lost laptop, stolen volume, backup leak | Disk/volume encryption, DB TDE, field crypto |
| **KMS / HSM** | Key sprawl in config files | AWS KMS, GCP KMS, Vault, CloudHSM |

```text
  Client ══TLS══► API ══TLS/mTLS══► Service
                      │
                      ▼
                 Encrypted disk / DB
                      │
              data key wrapped by
                      ▼
                    ┌─────┐
                    │ KMS │  (master keys stay here)
                    └─────┘
```

## Simple example

Storing SSNs or card tokens:

```text
  App: generate data key (or ask KMS)
       encrypt field → store ciphertext + key id
  Read: KMS decrypts data key → app decrypts field
```

Disk encryption alone isn’t enough if the app dumps plaintext into logs. **Field-level** encryption for highly sensitive columns; TLS everywhere on the path.

```text
  Stolen EBS snapshot (at-rest on)     → ciphertext, need keys
  Attacker on coffee-shop Wi-Fi (TLS)  → can’t read HTTPS body
  Key in GitHub (.env)                 → game over despite TLS
```

## Why prefer one over the other

| Prefer **TLS everywhere** when… | Prefer **also field-level crypto** when… |
|---------------------------------|------------------------------------------|
| Always — default for public and internal | Regulated PII/PCI; need app-level control |
| Stopping passive network attackers | DBAs / backups shouldn’t see plaintext |

| Prefer **KMS-managed keys** when… | Prefer **app-local keys** when… |
|-----------------------------------|----------------------------------|
| Production multi-service systems | Never, for serious secrets (avoid) |
| Need rotation, audit, IAM on decrypt | Toy/local only |

**Envelope encryption:** KMS holds master key; encrypts per-object data keys. Rotate master without re-encrypting all data immediately (re-wrap keys).

### Real systems (interview name-drops)

- **ACM / Let’s Encrypt**, **AWS KMS**, **Hashicorp Vault**, **S3 SSE-KMS**, **RDS encryption**.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| TLS terminate at LB only | Simple cert management | Hop LB→app may be plaintext on VPC (policy choice) |
| mTLS service mesh | Strong service identity | Operational complexity |
| Encrypt everything at rest | Baseline compliance story | Key management becomes critical path |
| Per-field encryption | Least privilege on data | Search/sort on ciphertext harder; more code |

**Common interview trap:** Saying “we’re secure, we use HTTPS” and ignoring at-rest keys, secrets in env, or plaintext internal hops.

## Interview trigger phrase

> “I’d enforce **TLS in transit**, encrypt **at rest** with **KMS-managed keys**, and field-encrypt the highest-sensitivity columns so backups aren’t enough to leak PII.”

## Exercise

**Design storage for a health-records API.**

1. List three places data could leak without TLS, at-rest, or KMS — one each.  
2. Why shouldn’t the master key live in the app’s config map?  
3. One sentence on key rotation: what do you rotate first (data keys vs master), and why envelope encryption helps?
