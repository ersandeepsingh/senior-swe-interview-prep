# Normalization vs Denormalization

> **Normalize** to avoid update anomalies (one fact, one place). **Denormalize** to avoid expensive joins on the hot read path. Seniors choose per query — not as a religion.

## Plain English

| | Normalization | Denormalization |
|---|---------------|-----------------|
| Data shape | Split into related tables | Duplicate fields into read models |
| Writes | Update once | Update many copies (or rebuild) |
| Reads | Join at query time | Pre-joined / embedded document |

```text
  Normalized                         Denormalized read model
  ┌─────────┐   ┌──────────┐         ┌─────────────────────┐
  │ users   │──<│ orders   │         │ order_view          │
  │ id,name │   │ user_id  │         │ order_id, user_name │
  └─────────┘   └──────────┘         │ items[], totals…    │
        ▲              │             └─────────────────────┘
        │         ┌────┴────┐              ▲
        │         │ order_  │              │ fed by
        │         │ items   │         CDC / app write /
        └─────────┴─────────┘         batch job
```

## Simple example

**Order confirmation email needs:** order id, user name, item titles, prices.

| Approach | How you get it |
|----------|----------------|
| **Normalized** | `JOIN users + orders + order_items + products` |
| **Denormalized** | Store `user_name` + line item snapshots on the order at checkout |

```text
  At checkout write:
    orders.user_name = "Riya"     ← snapshot (name may change later)
    line: "Nike Air", ₹7999       ← price at purchase time (correct!)

  Product price changes tomorrow → past orders stay historically correct.
```

Often **both**: normalized system of record + denormalized **read model** / cache.

## Why prefer one over the other

| Prefer **normalize** when… | Prefer **denormalize** when… |
|----------------------------|------------------------------|
| Fact must stay correct everywhere (email, role) | Read path is hot and join-heavy |
| Write rate dominates; few read shapes | Timeline / feed / product card needs one round-trip |
| Strong consistency across entities | You can tolerate stale copies or rebuild |

**Why not always normalize?** At feed scale, joining 20 tables per request won’t hit latency SLOs.

**Why not always denormalize?** User renames → thousands of rows to patch, or you show stale names forever without a sync plan.

### Real patterns (interview name-drops)

- **3NF / OLTP schema** in Postgres for source of truth.
- **CQRS / read models**, materialized views, Redis caches.
- **Document embedding** (Mongo: address inside user).
- **Star schema** in warehouses (intentional denorm for analytics).

## Trade-offs

| Approach | You gain | You give up |
|----------|----------|-------------|
| Strict normalization | Easy updates; less duplication bugs | Join cost; harder to serve one API payload |
| Application-level denorm | Fast reads; simple queries | Sync logic; inconsistency windows |
| Materialized view / CDC | Near-real-time read models | Pipeline complexity; lag |
| Snapshot at write (orders) | Historical correctness | Can’t “fix” past rows when catalog changes |

**Common interview trap:** Drawing only normalized ERD for Instagram feed. Seniors add a **timeline table** or cache that is deliberately denormalized.

## Interview trigger phrase

> “I’d keep **normalized OLTP** as source of truth and **denormalize** the hot read path — feed/timeline or order snapshots — accepting sync lag or write-time copies.”

## Exercise

**Design a food-delivery “restaurant card” on the home screen.**

1. What’s normalized (menu items, restaurant hours) vs what you’d denormalize onto the card (rating, ETA, cuisine tags)?  
2. Restaurant changes its name — how do open carts / past orders behave differently from the home feed?  
3. One sentence on how you’d refresh denormalized ratings without locking the write path.
