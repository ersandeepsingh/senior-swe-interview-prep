# Secrets Management

> **Secrets** (DB passwords, API keys, private keys) must not live in source code or world-readable config. Use a **secrets manager** (Vault, AWS Secrets Manager, GCP Secret Manager, Azure Key Vault), inject at runtime, and **rotate**.

## Plain English

| Bad | Good |
|-----|------|
| Secret in git / Docker image | Secret in manager; reference by name |
| Long-lived static key in `.env` committed | Runtime fetch + IAM auth |
| One shared prod password forever | Rotation + per-env secrets |
| Logging config dumps | Redaction |

```text
  App starts
    → authenticates to cloud (role/identity)
    → fetches secret myapp/db-url
    → connects to DB
    → (optional) refreshes on rotation
```

## Essentials (must-know for this topic)

### Bad vs good secret handling

| Bad | Good |
|-----|------|
| In git / `.env` committed | Secrets manager; reference by name |
| Baked into Docker image layers | Inject at **runtime** |
| Long-lived shared prod password | Per-env secrets + **rotation** |
| Static access keys in config | Workload **IAM role** / identity |
| Echo secrets in CI logs | Mask/redact |

### Tools & terms

| Term | Meaning |
|------|---------|
| **Secrets manager** | Vault, AWS Secrets Manager, GCP SM, Azure Key Vault |
| **Rotation** | Change credentials on a schedule / after breach |
| **Least privilege** | Role can read only the secrets it needs |
| **Sealed secrets / SOPS** | Encrypted-at-rest in GitOps (still needs key discipline) |
| **K8s Secret** | Not strongly safe by default — protect etcd / use external store |

**Interview line:** secrets never in code; fetch via identity at runtime; rotate.

## Simple example

**AWS:** ECS task role may `secretsmanager:GetSecretValue` on one ARN. App reads at boot (or sidecars inject env). Rotate RDS password in Secrets Manager with rotation Lambda; app reconnects.

**Kubernetes:** prefer external secrets operator / CSI driver over giant base64 Secrets in git (K8s Secrets are not strongly encrypted by default depending on setup).

## When to use / trade-offs

| Prefer **managed secrets service** when… | Prefer **sealed/encrypted files in git** when… |
|------------------------------------------|-----------------------------------------------|
| Cloud-native apps, rotation needs | GitOps with strong encryption (SOPS) + discipline |
| Multiple runtimes need dynamic access | Small static set, offline install |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Central vault | Audit, rotation, ACL | Availability dependency |
| Short-lived credentials | Lower blast radius | App must handle refresh |
| Env var injection | Simple | Easy to leak via `/proc`/logs/child procs |

## Pitfalls

- Committing `.env` “just for local” that contains prod.  
- Baking secrets into CI logs (`echo $KEY`).  
- Over-permissioned roles that can read all secrets.  
- No rotation after employee/vendor offboarding.  
- Treating K8s Secret YAML in git as safe without encryption.

## Interview trigger phrase

> “Secrets never live in code — I’d store them in a **secrets manager**, grant access via **workload identity/IAM**, inject at runtime, and **rotate** with an app that can refresh.”

## Exercise

**Microservice needs Stripe key + DB password.**

1. Where do they live in dev vs prod?  
2. Design rotation for the DB password without downtime.  
3. A secret was committed last year — list remediation steps.
