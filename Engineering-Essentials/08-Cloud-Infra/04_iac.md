# Infrastructure as Code (IaC)

> **IaC** defines cloud resources in versioned files (Terraform, CloudFormation, Pulumi, CDK) instead of click-ops. Infra becomes **reviewable, repeatable, and (mostly) immutable**.

## Plain English

| Idea | Meaning |
|------|---------|
| **Declarative** | You state desired end state; tool plans/applies diff |
| **State** | Terraform tracks what it manages (state file / backend) |
| **Immutable infra** | Replace servers/images rather than SSH-mutate snowflakes |
| **Modules** | Reusable building blocks (VPC, ECS service, …) |

```text
  code (*.tf) → plan → review → apply → cloud resources
                     │
              PR diff shows +aws_db_instance
```

## Essentials (must-know for this topic)

### IaC vocabulary

| Term | Meaning |
|------|---------|
| **Declarative** | Describe desired end state; tool diffs/applies |
| **Plan** | Preview of create/update/destroy before apply |
| **State** | Record of what the tool manages (must be remote + locked) |
| **Module** | Reusable chunk (VPC, service, …) |
| **Drift** | Reality diverged from code (console click-ops) |
| **Immutable infrastructure** | Replace instances/images; don’t SSH-mutate snowflakes |

### Common tools (know the names)

| Tool | Style |
|------|-------|
| **Terraform** | Multi-cloud declarative HCL |
| **CloudFormation / CDK** | AWS-native |
| **Pulumi** | IaC in general-purpose languages |
| **Ansible** | Often config management (mutable) vs pure provision |

**Golden rules:** PR every infra change; remote state + locks; never commit state secrets; codify break-glass fixes after incidents.

## Simple example

**Terraform sketch:**

```text
  resource "aws_s3_bucket" "assets" {
    bucket = "myapp-assets-prod"
  }

  resource "aws_iam_role" "api" { ... }
```

Environments: `dev` / `staging` / `prod` via workspaces or separate state + variables — **never** hand-edit prod to “just fix it” without updating code.

## When to use / trade-offs

| Prefer **Terraform** when… | Prefer **CloudFormation / CDK** when… |
|----------------------------|---------------------------------------|
| Multi-cloud or multi-tool ecosystem | Deep AWS-native, org standard |
| Large community modules | Want AWS support surface |

| Prefer **IaC** when… | Click-ops leftover when… |
|----------------------|--------------------------|
| Anything non-trivial / long-lived | Break-glass emergency (then codify after) |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Immutable replace | Reproducibility | Must automate data/disk migration |
| Shared modules | Speed | Bad module = wide blast radius |
| Remote state + locks | Team safety | State security becomes critical |

## Pitfalls

- State file with secrets committed to git.  
- Drift: manual console changes vs code.  
- God modules nobody understands.  
- `apply` without `plan` review in prod.  
- Destroying stateful resources by renaming carelessly.

## Interview trigger phrase

> “I’d manage cloud resources with **Terraform (or equivalent)**, remote state and PRs for changes, and treat servers as **cattle** — replace via new images, don’t snowflake-configure by hand.”

## Exercise

**Add a Redis cache to prod.**

1. What goes in IaC vs app config vs secrets manager?  
2. How do you roll out safely across staging then prod?  
3. Someone created a security group rule in the console — how do you detect and fix drift?
