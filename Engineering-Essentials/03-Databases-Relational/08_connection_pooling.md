# Connection Pooling

> Opening a DB connection is expensive — a **pool** keeps a set of warm connections and hands them to requests briefly.

## Plain English

Each Postgres connection uses meaningful memory. Many app pods × large pools = DB meltdown. A pool (in-process or **PgBouncer**/RDS Proxy) caps concurrent DB connections and reuses them.

## Essentials (must-know for this topic)

### Why pool

| Cost of a raw connection | Pool benefit |
|--------------------------|--------------|
| TCP + auth + memory (~MBs each) | Amortize setup; cap concurrency |
| Slow under churn (serverless) | Hold warm server-side conns |

### Math interviewers expect

```text
total possible DB conns ≈ pods × pool_size_per_pod
must be ≤ max_connections (with headroom for admin/replicas)
```

If that product exceeds `max_connections`, put an external pooler in front or shrink pools.

### PgBouncer modes

| Mode | Holds server conn until… | Scale | Caveat |
|------|--------------------------|-------|--------|
| **Session** | Client disconnects | Lowest | Simple; fewer clients per server conn |
| **Transaction** | Txn ends | **Best scale** | Session features break (temp tables, some prepared stmts) |
| **Statement** | Each statement | Extreme | Very limited features |

### App pool knobs

| Setting | Meaning |
|---------|---------|
| `max_pool_size` | Cap per process |
| `min_idle` | Warm idle conns |
| `connection_timeout` | Fail fast when exhausted |
| Checkout lifetime | Don’t hold across HTTP to third parties |

**Serverless:** thousands of short-lived clients → **RDS Proxy / PgBouncer** mandatory; tiny per-instance pools still add up.

## Why seniors get asked

“We scaled pods and Postgres fell over” is a classic. Seniors size pools and know external poolers.

## Simple example

```yaml
# App pool (conceptual)
max_pool_size: 20
min_idle: 5
connection_timeout_ms: 2000
```

```ini
; PgBouncer sketch
[databases]
mydb = host=pg port=5432 dbname=mydb
[pgbouncer]
pool_mode = transaction
max_client_conn = 5000
default_pool_size = 40
```

Rule of thumb: **total app pools ≤ what the DB can handle**, often with a pooler in between.

## When to use / when not / trade-offs

| Use pooling when… | Watch out when… |
|-------------------|-----------------|
| Any non-trivial web app | Serverless: thousands of short clients → need pooler / RDS Proxy |
| Many app instances | Session features break in transaction pooling (temp tables, prepared stmts) |

**Trade-offs:** higher throughput with fewer DB conns; misconfigured pools cause waits or still overwhelm the DB.

## Common pitfalls

- Pool size = “number of threads” with no global math
- Leaking connections (not returning to pool)
- Transaction mode + session-level features
- Pooling *and* opening raw connections elsewhere

## Interview trigger phrase

> “I’d size pools from DB max_connections backward, put PgBouncer in transaction mode for many pods, and never hold a connection across external I/O.”

## Exercise

200 pods, each with pool 50, Postgres `max_connections=400`. What’s wrong? Propose a target architecture with PgBouncer numbers that fit.
