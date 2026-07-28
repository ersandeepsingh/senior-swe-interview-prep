# AWS Revision — Senior Backend Engineer

Suggested order: **1) IAM → 2) Compute (EC2/Lambda/containers) → 3) Storage (S3) → 4) Databases (RDS/DynamoDB) → 5) Networking & delivery (VPC/ELB/CloudFront/Route 53) → 6) App integration (API Gateway/SQS/SNS) → 7) Config & secrets → 8) Observability → 9) Scaling & the "how it fits together" story.**

---

## 1. IAM — Identity & Access Management (start here, always asked)

**What:** Controls *who* can do *what* on *which* AWS resources.

Four building blocks:

- **Users** — a person or app with long-lived credentials. (Avoid for apps.)
- **Groups** — a bunch of users sharing permissions (e.g., "Developers").
- **Roles** — a set of permissions that can be *assumed* temporarily, with no long-lived keys. The preferred way for services/apps to get access.
- **Policies** — JSON documents that grant/deny permissions, attached to users/groups/roles.

**Why it matters for backend:** Your Lambda/EC2 needs to read an S3 bucket or write to DynamoDB — you give it a **role**, not hardcoded keys.

**Policy example** (allow read on one bucket):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject"],
    "Resource": "arn:aws:s3:::my-app-bucket/*"
  }]
}
```

**Must-know talking points:**

- **Roles > access keys.** Never hardcode credentials; attach a role so apps get rotating temporary creds.
- **Least privilege** — grant only what's needed.
- **Explicit Deny always wins** over any Allow.
- **Trust policy** = who is allowed to assume a role (e.g., "the EC2 service" or "the Lambda service").

*Interview line:* "My EC2 instance assumes an IAM role with an instance profile, so the SDK automatically gets temporary credentials — no keys in code or config."

---



## 2. Compute



### EC2 — Elastic Compute Cloud

**What:** Virtual servers (VMs) you rent. You pick instance type (CPU/RAM), OS, and manage it.

**Why:** The classic "run my backend/app server" option when you want full control.

**Know:**

- **Instance types** (general/compute/memory-optimized), **AMI** (the machine image), **security groups** (instance-level firewall), **key pairs** (SSH).
- **Pricing models:** On-Demand (flexible), Reserved/Savings Plans (cheaper, committed), Spot (cheapest, can be reclaimed — good for batch/stateless).

*Example:* a `t3.medium` running your API behind a load balancer, in an Auto Scaling Group.

### Lambda — Serverless functions

**What:** Run code without managing servers; AWS runs it on demand and scales automatically. Pay per invocation + duration.

**Why:** Great for event-driven backends, glue code, APIs (with API Gateway), and spiky/low-volume workloads.

**Know:**

- **Triggers/events:** API Gateway request, S3 upload, SQS message, EventBridge schedule, DynamoDB stream.
- **Stateless**, short-lived (max 15 min), config: memory, timeout, concurrency.
- **Cold starts** — first invocation after idle is slower (know this trade-off).
- Uses an **execution role** (IAM) for permissions.

*Example:* S3 upload triggers a Lambda that generates a thumbnail and writes it back to S3.

### EC2 vs Lambda vs Containers (common question)

- **EC2** — full control, always-on, you manage scaling/patching. Steady load.
- **Lambda** — no servers, auto-scales, pay-per-use. Event-driven / spiky / short tasks.
- **Containers (ECS/EKS/Fargate)** — package app in Docker; **ECS** = AWS's orchestrator, **EKS** = managed Kubernetes, **Fargate** = serverless containers (no EC2 to manage). Good middle ground for microservices.

*Interview line:* "Steady high-traffic service → containers on ECS/Fargate or EC2 ASG; event-driven or bursty → Lambda."

---



## 3. Storage — S3 (Simple Storage Service)

**What:** Object storage — store files ("objects") in "buckets," accessed via HTTP API. Virtually unlimited, highly durable (11 nines).

**Why:** The backend workhorse for user uploads, static assets, backups, logs, data-lake files, and serving files via CloudFront.

**Know:**

- **Objects & keys** (the "path"), buckets are globally unique names.
- **Storage classes:** Standard, Infrequent Access, Glacier (archival, cheap/slow) — cost vs access speed.
- **Access control:** private by default; grant via bucket policy / IAM; use **pre-signed URLs** for temporary access.
- **Versioning** and **lifecycle rules** (auto-move old files to Glacier or delete).
- Not a filesystem or a database — no partial in-place edits; you replace whole objects.

*Example (pre-signed URL):* backend generates a time-limited URL so a user can upload directly to S3 without proxying through your server.

*Interview line:* "For uploads I hand the client a pre-signed S3 URL — the file goes straight to S3, offloading bandwidth from my app, and an S3 event triggers post-processing."

---



## 4. Databases



### RDS — Relational Database Service

**What:** Managed SQL databases (PostgreSQL, MySQL, etc.) — AWS handles backups, patching, replication, failover.

**Why:** You want a relational DB without operating it yourself.

**Know:** **Multi-AZ** (standby in another zone for HA/failover), **read replicas** (scale reads), automated backups/snapshots. **Aurora** = AWS's high-performance MySQL/Postgres-compatible engine.

### DynamoDB — Managed NoSQL

**What:** Fully managed key-value/document NoSQL, single-digit-ms latency, scales horizontally automatically.

**Why:** Massive scale, serverless, predictable performance; pairs naturally with Lambda.

**Know:** **Partition key** (+ optional sort key) design around access patterns, on-demand vs provisioned capacity, **GSI** (global secondary index) for extra query patterns, **DynamoDB Streams** (trigger Lambdas on changes).

*Interview line:* "Relational data with complex queries/transactions → RDS/Aurora; simple key-based access at huge scale → DynamoDB."

---



## 5. Networking & Content Delivery



### VPC — Virtual Private Cloud (know the basics)

**What:** Your private, isolated network in AWS.

**Know (just enough):**

- **Subnets:** public (has internet access via Internet Gateway) vs private (no direct internet; egress via NAT Gateway).
- **Security groups** (stateful, instance-level firewall) vs **NACLs** (stateless, subnet-level).
- Typical pattern: load balancer in public subnet, app servers + database in private subnets.



### ELB — Elastic Load Balancer

**What:** Distributes incoming traffic across multiple targets (instances/containers).

- **ALB** (Application LB, Layer 7 — HTTP, path/host routing) — most common for backends.
- **NLB** (Network LB, Layer 4 — TCP, ultra-low latency/high throughput).

*Example:* ALB routes `/api/`* to one target group and `/images/`* to another; does health checks and TLS termination.

### CloudFront — CDN

**What:** Content Delivery Network — caches content at edge locations worldwide, close to users.

**Why:** Lower latency + less origin load for static assets (and cacheable API responses); also adds TLS and DDoS protection.

*Example:* CloudFront in front of an S3 bucket serves images from the nearest edge; the origin only handles cache misses.

### Route 53 — DNS (brief)

**What:** AWS's DNS service — maps domains to resources, with health checks and routing policies (latency-based, weighted, failover).

*Example:* `api.myapp.com` → your ALB; failover routing sends traffic to a backup region if the primary is unhealthy.

---



## 6. Application Integration



### API Gateway

**What:** Managed front door for APIs — routing, auth, throttling, request/response mapping — commonly in front of Lambda or backend services.

*Example:* `API Gateway → Lambda → DynamoDB` is the classic serverless REST API.

### SQS — Simple Queue Service

**What:** Managed message queue for decoupling and buffering work (producer → queue → consumer).

**Why:** Smooths spikes, decouples services, enables async processing and retries. **DLQ** for messages that keep failing. At-least-once delivery → make consumers **idempotent**.

*Example:* Checkout drops an "order placed" message on SQS; a worker processes fulfillment independently, so a slow downstream doesn't block checkout.

### SNS — Simple Notification Service

**What:** Pub/sub — publish a message to a topic, fan out to many subscribers (Lambdas, SQS queues, HTTP, email).

**SQS vs SNS (common question):** SQS = one queue, work pulled by consumers (point-to-point). SNS = broadcast one message to many subscribers (fan-out). Often combined: SNS topic → multiple SQS queues.

*Example:* `OrderPlaced` published to SNS fans out to an email queue, an analytics queue, and a shipping service.

---



## 7. Configuration & Secrets (short but important)

- **Secrets Manager** — store/rotate DB passwords, API keys; apps fetch at runtime (with rotation).
- **Parameter Store (SSM)** — store config values and secrets (cheaper, simpler).
- **Rule:** never hardcode secrets or put them in env files in the repo — fetch from Secrets Manager/SSM, access controlled by IAM.

*Interview line:* "DB credentials live in Secrets Manager; the app's IAM role grants read access and rotation is automated — nothing sensitive in code."

---



## 8. Observability

- **CloudWatch** — metrics, logs, alarms, dashboards. Your Lambda/EC2/ALB emit metrics here; you alarm on error rate or latency.
- **CloudWatch Logs** — centralized application/service logs.
- **X-Ray** — distributed tracing across AWS services (find the slow hop).
- **CloudTrail** — audit log of *who did what* in your AWS account (security/compliance).

*Example:* CloudWatch alarm on ALB 5xx rate > 1% → triggers SNS → pages on-call.

---



## 9. Scaling & Resilience

- **Auto Scaling Group (ASG)** — automatically add/remove EC2 instances based on load (CPU, request count). Pairs with ELB.
- **Multi-AZ** — deploy across Availability Zones for high availability (survive a datacenter failure).
- **Multi-Region** — for disaster recovery / global low latency (harder, do it when needed).
- **Managed auto-scaling** — Lambda, DynamoDB on-demand, and Fargate scale automatically.

*Interview line:* "App servers in an ASG across 3 AZs behind an ALB; the DB is Multi-AZ RDS with read replicas; static assets on S3 + CloudFront."

---



## Putting it together — the reference architecture to describe

A clean answer to "how would you deploy a backend on AWS?":

```
Route 53 (DNS)
   │
CloudFront (CDN, static assets/cache)
   │
Application Load Balancer  ── public subnet
   │
App servers (ECS/Fargate or EC2 in an Auto Scaling Group) ── private subnet
   │            │                      │
 RDS/Aurora   DynamoDB              SQS ── worker (async jobs)
 (Multi-AZ)   (scale)                │
   │                              (SNS fan-out)
 Secrets Manager (creds) · CloudWatch (metrics/logs/alarms) · IAM roles everywhere
```

**Narration:** users hit Route 53 → CloudFront serves cached/static, dynamic goes to the ALB → app servers (auto-scaled, in private subnets) → data in RDS/DynamoDB → heavy/async work offloaded to SQS workers → everything uses IAM roles, secrets from Secrets Manager, monitored by CloudWatch.

---



## The must-know shortlist (if time is tight)

1. **IAM** — users/groups/roles/policies, roles-over-keys, least privilege. *(most asked)*
2. **EC2 vs Lambda vs Containers** — when to use each.
3. **S3** — objects/buckets, pre-signed URLs, storage classes.
4. **RDS vs DynamoDB** — SQL managed vs NoSQL scale.
5. **VPC basics** — public/private subnets, security groups.
6. **ALB + Auto Scaling** — distribute + scale.
7. **CloudFront** — CDN/edge caching.
8. **SQS vs SNS** — queue vs pub/sub, decoupling, idempotency.
9. **Secrets Manager / SSM** — no hardcoded secrets.
10. **CloudWatch** — metrics, logs, alarms.

For each, be ready to say **what it is, when you'd choose it, and the trade-off** — that's the senior signal.