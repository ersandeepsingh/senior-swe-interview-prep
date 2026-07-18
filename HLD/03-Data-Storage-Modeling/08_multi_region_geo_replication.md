# Multi-Region Geo-Replication

> Put data near users for **latency** and **disaster recovery**. **Active-passive** = one region takes writes; **active-active** = many regions take writes (and you own conflict story).

## Plain English

| Mode | Writes | Failover | Hard part |
|------|--------|----------|-----------|
| **Active–passive** | Primary region only | Promote secondary | RPO/RTO; DNS/traffic shift |
| **Active–active** | Multiple regions | Traffic already local | Conflicts; cross-region consistency |

```text
  Active-passive                     Active-active
  ┌─────────┐  async/sync            ┌─────────┐     ┌─────────┐
  │ Region A│ ───────────►           │ Region A│◄───►│ Region B│
  │ PRIMARY │            ┌─────────┐ │ writes  │     │ writes  │
  └─────────┘            │ Region B│ └─────────┘     └─────────┘
     ▲                   │ STANDBY │      conflicts possible
  all writes             └─────────┘
```

Also decide: **replicate everything** vs **shard by geo** (user pinned to home region).

## Simple example

**Banking app India + Singapore.**

| Choice | Behavior |
|--------|----------|
| Active–passive (Mumbai primary) | Singapore users write with higher latency; DR ready |
| Active–active both write balances | Fast local writes; risk of divergent balances without careful CRDT/consensus |

```text
  Prefer:
    accounts / ledger → single-primary region or consensus (CP)
    static content / public catalog → active-active or CDN
```

**RPO / RTO (say them in interviews):**

- **RPO:** how much data you may lose (async lag).  
- **RTO:** how long until service is back after region death.

## Why prefer one over the other

| Prefer **active–passive** when… | Prefer **active–active** when… |
|---------------------------------|--------------------------------|
| Strong single write truth | Users worldwide need local write latency |
| Regulated money / inventory | Data is mergeable (likes, notes, presence) |
| Ops team wants simpler failover runbook | You’ve designed conflict resolution |

**Why not active-active for everything?** Cross-region sync latency (~50–200ms+) fights synchronous strong consistency. Most “active-active” systems are **eventually consistent** per record.

**Why geo-pin users?** Avoid conflicts: user always writes to home region; other regions are read-only replicas for that key.

### Real systems (interview name-drops)

- **Active–passive:** Postgres cross-region replica + promote; Aurora Global DB.
- **Active–active / multi-master:** Cosmos DB, DynamoDB global tables, Cassandra multi-DC, Spanner (different model: true-time consensus).

## Trade-offs

| Choice | You gain | You give up |
|--------|----------|-------------|
| Active–passive | Simpler consistency | Write latency for remote users; failover event |
| Async cross-region | Lower primary write latency | Non-zero RPO on region loss |
| Sync cross-region | Tiny RPO | High write latency; coupled availability |
| Active–active | Local writes; regional autonomy | Conflicts; harder testing |
| Geo-pinned keys | Fewer conflicts | Bad UX if user travels; uneven region load |

**Common interview trap:** “Multi-region = always available and strongly consistent.” Seniors pick **per data class** and state RPO/RTO.

## Interview trigger phrase

> “I’d run **active–passive** for the ledger with a clear RPO/RTO, and **active–active or CDN** for catalog/media — not one mode for the whole system.”

## Exercise

**Design multi-region for a collaborative docs product.**

1. Active-passive vs active-active for document body edits — argue one.  
2. Region A dies — what do users in Region B see for unsynced keystrokes (tie to RPO)?  
3. One sentence on using geo-pinning for paid org data residency (EU data stays in EU).
