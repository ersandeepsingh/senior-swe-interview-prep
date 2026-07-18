# Replication & Failover

> **Replication** copies data so one node dying isn’t data death. **Failover** promotes a healthy replica (or redirects traffic) so the service keeps serving — hopefully without split-brain.

## Plain English

Replication alone ≠ HA. You also need **detection**, **promotion**, **client redirect**, and **fencing** so the old primary can’t write after demotion.

| Mode | Write path | Failover feel |
|------|------------|---------------|
| **Leader–follower** | Writes to primary; replicas stream | Promote follower; maybe brief RPO>0 if async |
| **Sync replication** | Ack after replica durable | Safer RPO≈0; higher latency / availability hit |
| **Multi-leader / leaderless** | Many writers | Conflict resolution; failover is “redirect clients” |

```text
     Clients
        │
        ▼
   ┌─────────┐   async/sync redo     ┌──────────┐
   │ Primary │ ───────────────────►  │ Replica  │
   │         │                       │ (hot)    │
   └────┬────┘                       └────┬─────┘
        │ dies                            │
        └──────── promote / DNS / VIP ────┘
                         ▼
                   New Primary
```

## Simple example

Checkout DB: primary in AZ-a, sync replica AZ-b, async DR AZ-c.

```text
  Client write ──► Primary AZ-a
                      │ sync ACK
                      ▼
                   Replica AZ-b  (failover candidate, RPO≈0)
                      │ async
                      ▼
                   DR AZ-c       (RPO = replication lag)
```

Primary dies → orchestrator / Patroni / RDS promotes AZ-b. Clients reconnect via new endpoint (DNS, VIP, driver-aware discovery). In-flight txns on old primary may be lost if they weren’t replicated (**async**) — hence sync for money when RPO must be ~0.

## Why prefer one over the other

| Prefer **sync replica** when… | Prefer **async** when… |
|-------------------------------|------------------------|
| RPO ≈ 0 (ledger, inventory) | Cross-region latency kills UX |
| Failover must not lose acked writes | Read replicas for scale |
| Small # of sync standbys | Throughput over zero data loss |

**Automatic vs manual failover:** automatic is faster; risk of flapping / split-brain without fencing. Manual is safer ops for some banks; slower RTO.

**Read replicas:** scale reads; watch **replication lag** so “read-your-writes” isn’t broken after a write to primary.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| More replicas | Durability, read scale | Cost, replication lag complexity |
| Auto failover | Low RTO | Need fencing, careful health checks |
| Cross-region async DR | Survive region loss | Minutes of data loss possible |
| Sync cross-AZ | Stronger RPO | Write latency; stall if sync peer dies |

**Trap:** “Replicas = HA” without discussing **promotion**, **lag**, and **client redirect**. Replication without failover rehearsal is hope, not reliability.

**Fencing:** on promote, bump epoch / use STONITH / revoke old primary’s lease so a network-healed zombie cannot accept writes.

**App retries:** after failover, expect connection resets — idempotent writes + reconnect backoff in the data-access layer.

## Interview trigger phrase

> “I’d run **sync replication in-region for RPO≈0**, async cross-region for DR, and **automatic failover with fencing** so a resurrected primary can’t accept writes.”

## Exercise

**Design HA for a payments primary in one region.**

1. Sync vs async to the failover candidate — what do you tell the interviewer about RPO?
2. How do app servers discover the new primary after promotion?
3. One sentence on split-brain if two nodes both think they’re primary.
