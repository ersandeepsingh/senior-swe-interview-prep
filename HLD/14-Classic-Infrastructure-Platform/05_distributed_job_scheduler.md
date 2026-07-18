# Design a Distributed Job Scheduler 🔴

> **Crux:** Run cron-at-scale with **exactly-once intent** under failure — **leader election / leases** so one logical owner fires a job, plus retries and idempotent workers.

## Clarify (say this first)

**Functional**
- Cron / one-shot / delayed jobs; priorities
- At-least-once execution with idempotent handlers (usual)
- Pause, cancel, inspect next run
- Fan-out: millions of jobs, thousands of workers

**Non-functional**
- No missed fires under single-node loss
- Bounded duplicate runs on failover
- Horizontal worker scale
- Audit: who ran what when

## Back-of-envelope

```text
10M scheduled jobs; 1% fire per minute → ~1.7k fires/s average
Peak: 10× → ~17k dispatch/s
Job metadata ~500 B → 10M × 500 B ≈ 5 GB (+ indexes)
Workers: 500; each handles ~30–40 jobs/s at peak
Lease TTL: 10–30s; renew at ≤ TTL/3
```

## API + data model

```text
POST   /jobs          {cron|run_at, payload, timeout}
GET    /jobs/{id}
POST   /jobs/{id}/pause|cancel
GET    /jobs/{id}/runs
```

| Entity | Fields |
|--------|--------|
| Job | `id`, `schedule`, `payload`, `next_run`, `state` |
| Run | `job_id`, `attempt`, `worker`, `status`, `lease_until` |
| Shard | time-bucket or hash(job_id) → scheduler partition |

## High-level architecture

```text
  API ──► Job store (DB) ── next_run index
                │
                ▼
        Scheduler shards (each owns key range)
                │  claim due jobs via lease / CAS
                ▼
           Dispatch queue
                │
                ▼
           Worker pool ── execute ── ack / retry / DLQ
                │
         Coordinator (ZK/etcd) for shard leadership
```

## Deep dive: the crux

**Who fires the job?**
| Pattern | Idea | When |
|---------|------|------|
| **Single global leader** | One scheduler ticks all | Small fleets; SPOF risk mitigated by election |
| **Sharded leaders** | Hash/time shards; leader per shard | Large job counts |
| **DB lease / `FOR UPDATE SKIP LOCKED`** | Workers pull due rows | Simple; DB is bottleneck |
| **Calendar queue + timer wheel** | In-memory per shard | Ultra-low latency delays |

**Fault tolerance:** lease with TTL; on expiry another node claims. Fires may duplicate on network blip → **idempotent job handlers** + run_id dedup. Persist `next_run` only after durable claim.

**Pick:** sharded schedulers with ZK/etcd leadership per shard; lease-based claim; at-least-once + idempotency.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Sharded leaders | Scale scheduling | More coordination |
| Short lease TTL | Fast failover | More renew chatter / false expiry |
| At-least-once | No silent skips | Duplicate side effects unless idempotent |
| DB as source of truth | Simple ops | Hot `next_run` index |
| Push vs pull workers | Control vs elasticity | Coupling vs lag |

## Failure modes & scale

- **Leader dies mid-fire:** lease expires → second fire; dedupe with `run_id`
- **Clock skew:** use store time / logical schedule, not wall clock alone
- **Thundering herd:** millions due at midnight — jitter + rate-limited dispatch
- **Poison job:** max attempts → DLQ; don’t block shard
- **Scale:** split shards; move ranges; partition by tenant for noisy neighbors

## Interview trigger phrase

> “I’d **shard the schedule**, elect a **leader per shard**, and claim due jobs with a **lease** so failover is automatic — executions are **at-least-once**, so handlers must be **idempotent**.”

## Exercise

1. Job should run once at `T`; leader dies after enqueue but before ack — design to avoid skip *and* bound duplicates.  
2. 5M jobs all cron `0 * * * *` — how do you avoid a top-of-hour stampede?  
3. Compare ZK leader vs `SKIP LOCKED` poll for 20k fires/s.
