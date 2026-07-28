# Cloud Primitives (AWS / GCP / Azure)

> Cloud providers share the same **building blocks**: compute, object storage, managed databases, queues, load balancers, identity. Seniors map a design to primitives — not memorizing every product name.

## Plain English

| Need | Typical AWS | GCP-ish | Azure-ish |
|------|-------------|---------|-----------|
| VM compute | EC2 | Compute Engine | Virtual Machines |
| Containers | ECS/EKS | GKE | AKS |
| Serverless functions | Lambda | Cloud Functions | Azure Functions |
| Object storage | S3 | Cloud Storage | Blob Storage |
| Managed SQL | RDS / Aurora | Cloud SQL | Azure SQL |
| Managed NoSQL | DynamoDB | Firestore / Bigtable | Cosmos DB |
| Queue | SQS | Pub/Sub (pull) | Queue Storage / Service Bus |
| Pub/sub | SNS | Pub/Sub | Event Grid / Service Bus |
| Load balancer | ALB/NLB | Cloud Load Balancing | Azure Load Balancer / App Gateway |
| CDN | CloudFront | Cloud CDN | Azure CDN |
| Secrets | Secrets Manager / SSM | Secret Manager | Key Vault |

```text
  Users → DNS → CDN/LB → Compute (VM/container/function)
                              │
                    DB / cache / queue / object store
```

## Essentials (must-know for this topic)

### Primitive map (what you actually pick)

| Need | Think in primitives | AWS example |
|------|---------------------|-------------|
| Run code | VM / container / function | EC2, ECS/EKS, Lambda |
| Files/blobs | Object storage | S3 |
| Relational data | Managed SQL | RDS / Aurora |
| Fast KV / cache | Managed cache | ElastiCache |
| Async work | Queue / pub-sub | SQS / SNS |
| Edge | CDN + DNS | CloudFront + Route 53 |
| Identity | IAM roles / policies | IAM |
| Secrets | Secrets manager | Secrets Manager / SSM |

### Design defaults seniors name

| Prefer | Over |
|--------|------|
| Managed services for undifferentiated work | Self-managing DBs on day one |
| **IAM roles** for workloads | Long-lived access keys in config |
| Multi-AZ for stateful prod | Single-AZ “we’ll add later” |
| Object storage for blobs | Disk on the app box |

**Interview move:** sketch with primitives first, product names second.

## Simple example

**Typical web API on AWS:**

```text
  Route 53 → CloudFront → ALB → ECS/EKS services
  S3 for assets, RDS Postgres, ElastiCache Redis
  SQS for async jobs, Secrets Manager for DB creds
  IAM roles for tasks (no long-lived keys)
```

## When to use / trade-offs

| Prefer **managed service** when… | Prefer **self-managed on VMs** when… |
|----------------------------------|--------------------------------------|
| Undifferentiated heavy lifting | Exotic config / cost at huge scale |
| Team small; want less ops | Need features managed offering lacks |

| Prefer **object storage** when… | Prefer **block/disk** when… |
|---------------------------------|-----------------------------|
| Files, backups, data lake | Databases needing POSIX disk |
| HTTP-accessible blobs | Low-latency local volume |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Managed DB | Backups, failover helpers | Less knob-turning; cost model |
| Multi-AZ | Higher availability | Cost; cross-AZ latency/cost |
| Single-cloud deep use | Speed, integrations | Lock-in |

## Pitfalls

- Hardcoding access keys instead of **roles**.  
- Public S3 buckets by accident.  
- One giant VPC with no subnet strategy.  
- Using a queue as infinite storage.  
- Designing for “cloud agnostic” too early → slow everything.

## Interview trigger phrase

> “I’d map the design to **primitives** — LB, compute, managed DB, object storage, queue — prefer **managed** where it isn’t our edge, and wire access with **IAM roles**, not embedded keys.”

## Exercise

**Photo-sharing MVP.**

1. Pick primitives for upload, thumbnailing, metadata, and feed read path (any cloud).  
2. Where do secrets and IAM roles sit?  
3. What do you *not* build yourself on day one?
