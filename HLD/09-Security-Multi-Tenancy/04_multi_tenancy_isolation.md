# Multi-Tenancy Isolation

> **Multi-tenancy** serves many customers from one platform. Isolation ranges from **shared everything** (tenant_id on rows) to **siloed** (per-tenant DB/cluster). Pick based on compliance, noisy-neighbor risk, and cost — then enforce **per-tenant limits** so one customer can’t starve others.

## Plain English

| Model | How isolation works | Typical fit |
|-------|---------------------|-------------|
| **Pooled / shared** | Same app + DB; `tenant_id` on every row | Early SaaS, cost-sensitive |
| **Bridge** | Shared app; separate DB/schema per tenant | Mid-market; easier backup/restore per customer |
| **Silo** | Separate app stack / account per tenant | Enterprise, strict compliance |

```text
  Shared (pool)                    Silo
  ┌──────────────────┐             ┌────────┐ ┌────────┐
  │ App (all tenants)│             │ App T1 │ │ App T2 │
  │ DB: rows +       │             │ DB T1  │ │ DB T2  │
  │     tenant_id    │             └────────┘ └────────┘
  └──────────────────┘
```

**Every query** in pooled mode must be tenant-scoped. Missing `WHERE tenant_id = ?` is a data-breach class bug.

## Simple example

SaaS CRM, two tenants: Acme and Globex.

```text
  Shared table contacts
  id | tenant_id | name
  1  | acme      | Ada
  2  | globex    | Grace

  Bad:  SELECT * FROM contacts WHERE id=2
        → Acme user sees Globex contact 💥

  Good: SELECT * FROM contacts WHERE id=2 AND tenant_id=acme
```

**Noisy neighbor:** Acme runs a huge export. Without quotas, Globex’s API p99 explodes. Fix: per-tenant RPS, concurrency, and storage caps.

## Why prefer one over the other

| Prefer **shared / pooled** when… | Prefer **isolated / silo** when… |
|----------------------------------|----------------------------------|
| Cost and ops simplicity dominate | Contract requires dedicated env |
| Tenants trust logical isolation | Regulated data; blast-radius limits |
| Fast feature deploy to all | Per-tenant upgrade/freeze schedules |

| Prefer **per-tenant rate/storage limits** always when… |
|--------------------------------------------------------|
| Any shared compute or DB — isolation of *performance* ≠ isolation of *data* |

**Enterprise “we need our own VPC”** often means silo or dedicated schema + private networking — name the requirement (compliance vs ego) and cost it.

### Real systems (interview name-drops)

- **Row-level security (Postgres RLS)**, **Shopify-style shard-by-tenant**, **dedicated Aurora per enterprise**.
- **Kubernetes namespaces / separate accounts** for silo compute.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Pooled multi-tenant | Lowest cost; one deploy | Cross-tenant bug risk; noisy neighbors |
| DB-per-tenant | Cleaner backup/restore; stronger boundary | Connection sprawl; migration fleets |
| Full silo | Max isolation; custom SLAs | Cost; slow rollout of features |
| No per-tenant limits | Simpler initially | One tenant takes the platform down |

**Common interview trap:** “Shared DB with tenant_id” drawn — no mention of mandatory tenant filter or quotas.

## Interview trigger phrase

> “I’d start **pooled with tenant_id on every row** plus **per-tenant rate and storage limits**, and offer **silo/DB-per-tenant** for enterprise compliance — isolation level is a product tier.”

## Exercise

**Design a multi-tenant document store.**

1. Argue pooled vs DB-per-tenant for a free tier of 100k small customers.  
2. How do you prevent Tenant A’s search reindex job from starving Tenant B’s interactive API?  
3. One sentence you’d tell the interviewer about the #1 bug class in pooled tenancy (missing tenant predicate / IDOR).
