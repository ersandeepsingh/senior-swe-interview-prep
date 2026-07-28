# RBAC / ABAC

> **RBAC** grants permissions through **roles**. **ABAC** grants them through **attributes** and policies (user, resource, environment). Most products start RBAC and grow toward ABAC when “admin vs user” isn’t enough.

## Plain English

| | **RBAC** | **ABAC** |
|---|----------|----------|
| Core idea | User → Role → Permissions | Policy over attributes |
| Example | `editor` can `update_post` | Allow if `user.dept == doc.dept` AND `time` is business hours |
| Strength | Simple, auditable | Fine-grained, contextual |
| Weakness | Role explosion | Policy complexity |

```text
  RBAC:  alice ∈ {editor}  →  editor permits edit_article
  ABAC:  allow edit if subject.id == resource.owner_id
                      OR subject.clearance >= resource.classification
```

**ReBAC** (relationship-based, e.g. Google Zanzibar-style) is another modern variant: permission from graph relations (`owner`, `parent`, `viewer`).

## Essentials (must-know for this topic)

### RBAC vs ABAC vs ReBAC

| Model | Core idea | Example |
|-------|-----------|---------|
| **RBAC** | User → **role** → permissions | `editor` can `update_post` |
| **ABAC** | Policy over **attributes** (user, resource, env) | Allow if `user.dept == doc.dept` |
| **ReBAC** | Permission from **relationships** | `viewer` of doc via folder parent |

### When each fits

| Prefer | When |
|--------|------|
| **RBAC** | Few clear job functions; simple admin UX |
| **ABAC** | Context/data-dependent decisions; time, clearance, tenant |
| **ReBAC** | Sharing graphs (Docs/Drive-style) |

### Multi-tenant note

| Idea | Meaning |
|------|---------|
| **Scoped role** | `org:acme/admin` ≠ global admin |
| **Role explosion** | Smell that you need attributes/relationships |
| **Server-side enforce** | UI roles are not AuthZ |

## Simple example

**Hospital system:**

```text
  RBAC alone:
    roles: doctor, nurse, admin  → too coarse for "this patient's chart"

  ABAC / ReBAC:
    doctor can read chart if assigned_to(patient)
    break-glass role with audit for emergencies
```

**SaaS multi-tenant RBAC:** roles scoped per tenant/org — `org:acme/admin` ≠ global admin.

## When to use / trade-offs

| Prefer **RBAC** when… | Prefer **ABAC** when… |
|-----------------------|-----------------------|
| Few clear job functions | Decisions depend on data/context |
| Need simple admin UX | Multi-tenant, sharing, hierarchies |

| Prefer **coarse roles + checks in code** when… | Prefer **central policy engine** when… |
|------------------------------------------------|----------------------------------------|
| Early product | Many services must enforce same rules |
| Speed to ship | Compliance needs uniform audit |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Few roles | Clarity | Coarse grants |
| Many roles | Precision | Role explosion / confusion |
| ABAC | Expressiveness | Harder to reason & test |

## Pitfalls

- Global `admin` for convenience.  
- Roles that encode **attributes** poorly (`us-east-editor-tier2-temp`) — that’s a smell for ABAC.  
- AuthZ only in UI.  
- Mixing tenant boundaries incorrectly (IDOR across orgs).  
- No audit log of who granted which role.

## Interview trigger phrase

> “I’d start with **tenant-scoped RBAC** for clarity, and move to **ABAC/ReBAC** when permissions depend on ownership, relationships, or context — always enforced server-side.”

## Exercise

**Google Docs–style sharing.**

1. Why do pure roles get awkward?  
2. Model “anyone with link can comment” in RBAC vs ABAC/ReBAC terms.  
3. User leaves the company — how does access get revoked in each model?
