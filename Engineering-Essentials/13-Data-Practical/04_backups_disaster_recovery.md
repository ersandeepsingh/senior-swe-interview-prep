# Backups & Disaster Recovery

> Hope is not a strategy. Define how much data you can lose (**RPO**) and how long you can be down (**RTO**), then prove restores with drills.

## Plain English

Backups that were **never restored** are fiction. Schedule restore drills. Multi-AZ is HA; multi-region is DR — don't confuse them.

```text
  Backup:     copy of data (may be periodic)
  Replication: live/near-live copies (async or sync)
  DR:         plan + infra to run when a region/datacenter dies

  RPO ≈ 0     → sync replication (costs latency)
  RPO ≈ minutes → async replicas + WAL shipping / CDC
  RTO low     → automated failover, pre-provisioned infra
```

## Essentials (must-know for this topic)

### RPO vs RTO

| Term | Question | Example |
|------|----------|---------|
| **RPO** | How much data can we lose? | ≤ 5 minutes → frequent backup/replication |
| **RTO** | How long can we be down? | ≤ 1 hour → warm standby beats cold tape |

### Mechanisms ladder

| Mechanism | Typical RPO | Typical RTO |
|-----------|-------------|-------------|
| Sync replica (same region) | Near-zero | Minutes |
| Async replica / WAL / CDC | Seconds–minutes | Tens of minutes |
| Cross-region async | Minutes (possible loss on failover) | Tens of minutes with automation |
| Daily snapshot only | Up to 24h | Hours to rebuild |

### HA vs DR

| | **HA (e.g. multi-AZ)** | **DR (e.g. multi-region)** |
|---|------------------------|----------------------------|
| Survives | One AZ / node failure | Region / datacenter loss |
| Cost / complexity | Lower | Higher |
| Still need | Backups + restore drills | Runbooks, traffic flip, dependency restore |

**Golden rule:** untested backup ≠ recovery plan.

## Simple example

Postgres production:

| Tier | Mechanism | Approx RPO/RTO |
|------|-----------|----------------|
| Continuous | Streaming replica same region | Seconds / minutes |
| Cross-region | Async replica or PITR to S3 WAL | Minutes–hours / tens of minutes |
| Daily snapshot | AMI/snapshot only | Up to 24h loss / hours to rebuild |

App DR: multi-AZ for HA; multi-region if the business pays for the complexity. Document who declares disaster and how DNS/traffic flips.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Sync multi-AZ | Tiny RPO, HA | Write latency; correlated region risk remains |
| Async cross-region | Region DR | Possible data loss on failover |
| Cold backups only | Cheap | High RTO/RPO |
| Active-active multi-region | Low RTO | Conflict resolution hell |

## Pitfalls

- **Backups in the same blast radius** (same disk / same account without vaulting).
- **No restore test** — credentials wrong, dumps corrupted, runbooks stale.
- **Confusing HA with DR** — multi-AZ survives one AZ; not a whole-region outage.
- **Unencrypted backups** or overly open snapshot shares.
- **Ignoring dependent systems** — DB restored but Kafka offsets / object store / secrets not.

## Interview trigger phrase

> “I'd set **RPO/RTO from the business**, implement replication + backups to match, and run **restore drills** — because an untested backup isn't a recovery plan.”

## Exercise

A payments ledger needs RPO ≤ 1 minute and RTO ≤ 15 minutes for region failure. Propose a concrete architecture (replication + traffic switch) and one thing you'd drill quarterly.
