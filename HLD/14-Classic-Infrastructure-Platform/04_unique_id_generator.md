# Design a Distributed Unique ID Generator 🟡

> **Crux:** Mint **globally unique** IDs that are roughly **time-ordered**, with **minimal coordination** on the hot path — Snowflake-style bits or range allocation.

## Clarify (say this first)

**Functional**
- 64-bit (or 128-bit) unique IDs
- Roughly sortable by time? (usually yes)
- Batch mint vs one-at-a-time
- Multi-region / multi-DC

**Non-functional**
- Very high QPS; low latency
- No single point of failure
- Clock skew tolerance story
- Uniqueness ≫ perfect global order

## Back-of-envelope

```text
Peak: 100k IDs/s cluster-wide
Snowflake: 41b time | 10b worker | 12b seq
  → 4096 IDs/ms/worker; 1024 workers
Range allocator: DB issues blocks of 1000 → 100k QPS / 1000 = 100 DB ops/s
UUID v4: unlimited scale, no order, 128-bit storage cost
```

## API + data model

```text
GET /v1/ids?count=1|n     → {ids: [...]}
POST /v1/workers/register → {worker_id}   # for Snowflake
```

| Scheme | Structure |
|--------|-----------|
| Snowflake | `timestamp \| datacenter \| worker \| sequence` |
| Range | `{start, end}` leased from allocator store |
| UUID | random 128-bit |

## High-level architecture

```text
  Clients
     │
     ▼
  ID Service (stateless replicas)
     │
     ├─ Snowflake path: local clock + assigned worker_id → bit-pack
     │
     └─ Range path: cache of [start,end); refill from Allocator DB
                         │
                         ▼
                   Allocator (strong consistency)
                   rows: worker → next_start
```

## Deep dive: the crux

| Approach | Pros | Cons | Pick when |
|----------|------|------|-----------|
| **Snowflake** | Fast, sortable, no DB on path | Needs unique worker IDs; clock skew | Default high-QPS product IDs |
| **DB ranges** | Simple uniqueness; easy ops | Allocator availability; less dense time-order | Moderate QPS; hate clock logic |
| **UUID v4** | Zero coord | No sort; larger indexes | Correlation IDs, no order need |
| **Redis INCR** | Easy | Hot key; SPOF unless carefully sharded | Small scale only |

**Snowflake pitfalls:** rewind clock → refuse or wait; worker_id from ZK/etcd lease; leave sequence bits for burst. **Ranges:** lease large blocks; tolerate gaps on crash (OK).

**Pick for interview:** Snowflake with ZK-assigned worker IDs; mention range allocation as alternative.

**Multi-region:** reserve DC bits in the ID; never share worker_id across DCs. Gaps are fine; collisions are not. Persist allocation leases so restarts don’t reuse in-flight sequences carelessly.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Time-ordered 64-bit | Index locality; sortable | Clock dependency |
| Central counter | Strict monotonic | Throughput ceiling |
| Large range blocks | Fewer allocator hits | Bigger gaps on crash |
| Multi-DC worker bits | Unique across regions | Bit budget / capacity |

## Failure modes & scale

- **Clock jump backward:** pause issuance or use logical tick until catch-up
- **Worker ID collision:** duplicate IDs — hard failure; lease IDs with TTL
- **Allocator down (ranges):** serve from cached blocks; degrade when empty
- **DC split:** separate DC bits so both sides stay unique
- **Exhaust sequence in 1ms:** wait next millisecond tick

## Interview trigger phrase

> “I’d use **Snowflake**: timestamp + worker + sequence so IDs are unique and roughly time-ordered **without a central counter on every request** — worker IDs leased from ZooKeeper/etcd.”

## Exercise

1. Two ID servers share the same worker_id — what’s the failure mode?  
2. Compare index locality of Snowflake vs UUID for a 1B-row `orders` table.  
3. Design range size for 50k QPS with allocator p99 budget of 100 QPS.
