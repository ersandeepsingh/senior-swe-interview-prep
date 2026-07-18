# Read/Write Splitting

> Send **writes to the primary**, fan **reads to replicas**. You buy read throughput cheaply — and inherit **replication lag** as the tax. Design for stale reads or pin critical reads to primary.

## Plain English

| Path | Routed to | Why |
|------|-----------|-----|
| INSERT / UPDATE / DELETE | Primary | Only primary accepts writes (classic) |
| Heavy GET / list / report | Replicas | Offload read QPS |
| Read-your-writes (profile after edit) | Primary or session sticky | Avoid seeing old self |

```text
                 ┌────────────┐
      writes ───►│  Primary   │
                 └─────┬──────┘
                       │ replicate
           ┌───────────┼───────────┐
           ▼           ▼           ▼
       Replica1    Replica2    Replica3
           ▲           ▲           ▲
           └──── reads ┴───────────┘
                 (LB / proxy / app)
```

## Simple example

**Twitter-like home timeline:** 100:1 read:write.

```text
  Post tweet     → Primary
  Load timeline  → Replica pool

  User edits bio → Primary
  Immediately refreshes profile
       → if replica lag 2s → old bio 💥
       → fix: read-after-write from primary / "monotonic reads" sticky
```

| Technique | Effect |
|-----------|--------|
| Always-primary for that session after write | Stronger UX, less replica benefit |
| Causal / version tokens | Client waits until replica caught up |
| Accept lag for public feeds | Max scale |

## Why prefer one over the other

| Prefer **read replicas** when… | Prefer **all reads on primary** when… |
|--------------------------------|----------------------------------------|
| Read-heavy workload | Tiny QPS; lag intolerable |
| Stale data OK for most paths | Strong read-after-write everywhere |
| Reporting / analytics isolation | Single-node still fine |

**Why not infinite replicas?** Replication bandwidth, lag under load, and **replica lag storms** after primary bursts. Also: replicas don’t fix write bottleneck.

**Why not split without a plan for lag?** Classic bug: “update then redirect to GET” shows stale data intermittently — flaky demos in interviews if you don’t mention it.

### Real systems (interview name-drops)

- **Proxies:** ProxySQL, MaxScale, Vitess, RDS reader endpoints.
- **ORM/app:** separate `writer` / `reader` datasources.
- **Managed:** Aurora reader instances, Cloud SQL replicas.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Read/write split | Horizontal read scale | Stale reads; dual connection logic |
| Pin post-write to primary | Correct UX after edits | Uneven primary load |
| Sync replication to one replica | Less lag / safer promote | Write latency |
| Use replica for analytics | Isolate OLTP | Heavy queries still can lag / contend |

**Common interview trap:** Drawing replicas and claiming “strong consistency for all reads.” Seniors explicitly separate **browse (replica)** vs **checkout read (primary)**.

## Interview trigger phrase

> “I’d **split reads to replicas** for feed/browse, keep **writes and read-your-writes on primary**, and call out replication lag as an explicit product trade-off.”

## Exercise

**Design DB routing for an e-commerce site.**

1. Route: place order, view product page, view “my orders” right after purchase — primary or replica?  
2. Replica is 5s behind during a flash sale — what user-visible bugs appear?  
3. One sentence on how a connection proxy helps the app vs routing in application code.
