# Disaster Recovery

> **DR** is surviving loss of a **region / datacenter / backup site**, not just a pod. Agree **RPO** (how much data you may lose) and **RTO** (how fast you’re back) *before* you draw multi-region boxes.

## Plain English

HA inside a region (multi-AZ) ≠ DR. DR answers: “Mumbai region is gone — now what?”

| Term | Meaning |
|------|---------|
| **RPO** | Recovery Point Objective — max acceptable data loss (time) |
| **RTO** | Recovery Time Objective — max acceptable downtime |
| **Backup** | Point-in-time copy (often colder) |
| **Multi-region** | Hot/warm/cold standby or active-active |

```text
  RPO = 5 min     ──►  async replicate ≤5 min lag / backup every 5 min
  RTO = 30 min    ──►  runbook + DNS/failover rehearsed to be live ≤30 min

  Region A (primary)  ~~~async~~~►  Region B (DR)
         ✕ outage                      │
                                       ▼ promote / redirect traffic
```

## Simple example

Payments: RPO 0 in-region (sync), RPO ≤1 min cross-region (async), RTO ≤15 min with rehearsed promote. Marketing blog: nightly backup, RPO 24h, RTO hours — cheap.

```text
  Tiering example:
    Ledger     → sync AZ, async region, RPO minutes, RTO 15m
    Media      → multi-region object store (S3 CRR)
    Analytics  → rebuild from lake; RTO hours OK
```

**3-2-1 backups:** 3 copies, 2 media, 1 offsite; **test restores** or you don’t have backups. Snapshots without restore drills are fiction.

## Why prefer one over the other

| Prefer **active-passive DR** when… | Prefer **active-active** when… |
|------------------------------------|--------------------------------|
| Simpler consistency, clear primary | Latency to users in many geos |
| Strict single-writer data | Read-heavy / mergeable data |
| Cost-sensitive warm standby | Willing to pay conflict/complexity tax |

**Cold DR** (restore from backup only) is fine for low-tier; not for checkout. **Pilot light / warm standby** balances cost vs RTO.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Lower RPO/RTO | Less loss / downtime | $$ and complexity |
| Cross-region sync | Tiny RPO | Latency / availability under partition |
| Untested DR plan | Comforting slide | Real outage surprise |
| Active-active writes | Local latency | Conflict resolution hard |

**Trap:** Multi-region drawn on the whiteboard with no RPO/RTO numbers. Interviewers want the **targets** and the **failover drill**.

**Runbook contents (say out loud):** who declares DR, how DNS/traffic shifts, how you promote DB, how you verify data, how you fail back. Untested runbooks fail first.

**Backup ≠ replica:** replicas can be corrupted by a bad write; periodic immutable backups / object-lock defend against ransomware-class events.

## Interview trigger phrase

> “I’d set **RPO/RTO with the product owner** — sync in-region for payments, async cross-region DR with a **rehearsed promote**, and backups we actually restore.”

## Exercise

**DR for “Design Uber” trip data vs static map tiles.**

1. Propose RPO/RTO for each and the mechanism (sync, async, CDN origin).
2. What do you test in a DR game day?
3. One sentence on active-active risk for trip payment state.
