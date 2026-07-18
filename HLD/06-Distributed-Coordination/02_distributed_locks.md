# Distributed Locks

> A **distributed lock** tries to give only one process the right to do critical work across machines. Easy to draw; hard to get **safe** under pauses, GC, and clock skew.

## Plain English

Local mutex ≠ cluster mutex. Process A on box 1 and process B on box 2 need a shared lease: “only I hold `resource-X` until I release or the lease expires.”

| Approach | Idea | Caveat |
|----------|------|--------|
| **ZooKeeper / etcd lock** | Ephemeral node + watch; CP store | Still need fencing; hold time vs work time |
| **DB row lock / `SELECT FOR UPDATE`** | Transactional mutual exclusion | DB becomes bottleneck |
| **Redlock (Redis)** | Multi-key SET NX PX across N Redis | Controversial; clocks / pauses can break safety |

```text
     Worker A                         Worker B
        │                                │
        │  try acquire lock(key)         │
        ▼                                ▼
   ┌─────────────────────────────────────────┐
   │     Lock service (ZK / etcd / Redis)    │
   │   only one grant + lease TTL            │
   └─────────────────────────────────────────┘
        │ owner=A, fence=42
        ▼
   Do critical section (must check fence
   on every write to shared resource)
```

## Simple example

Two payment workers both retry “capture charge C123.”

Without a lock (or better: **idempotency**), both may call Stripe. With a lock:

```text
  Worker A acquires lock(C123) → captures → releases
  Worker B waits / fails → sees already captured → no-op
```

If A **pauses** (GC) past TTL, B may acquire while A still thinks it holds the lock → **two holders**.

```text
  t0  A gets lock, TTL=10s, fence=7
  t5  A enters long GC pause
  t11 lock expires; B gets lock, fence=8
  t12 A wakes, still thinks it holds lock
      A writes with fence=7 → STORAGE MUST REJECT
```

Fix: **fencing token** (monotonic) stored with the resource; storage rejects stale token.

## Why prefer one over the other

| Prefer **ZK/etcd lock** when… | Prefer **avoid lock** when… |
|-------------------------------|-----------------------------|
| Short critical section, need exclusion | You can use idempotency / compare-and-swap |
| Coordination already on CP store | High QPS hot key (lock becomes hotspot) |
| Lease + watches fit ops model | Long jobs (lease expiry races) |

**Redlock:** Martin Kleppmann’s critique — Redis is AP-ish; GC pauses + clock drift undermine safety. Fine for **best-effort** “only one cron”; not for bank correctness. Prefer etcd/ZK or DB transactions + fencing.

**Better than locks often:** unique DB constraints, conditional writes (`UPDATE … WHERE version=N`), idempotency keys.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Distributed lock | Simpler “critical section” thinking | Complexity under failure; thundering herd |
| Short TTL | Recover from crashed holders | Risk of dual holders without fencing |
| Long TTL | Fewer false expiries | Stuck locks if holder dies |
| Lock around slow I/O | Feels safe | Holds serialize throughput |

**Trap:** Treating Redlock as “exactly-once” for payments. Pair locks with **idempotency keys** and resource-side fencing.

## Interview trigger phrase

> “I’d use an **etcd/ZK lease with a fencing token**, not Redlock, for anything correctness-critical — and I’d rather design **idempotent** APIs so we lock less.”

## Exercise

**“Only one inventory decrement for SKU under flash sale.”**

1. Sketch failure when lock TTL expires while the holder is still writing.
2. Where does the fencing token get checked — lock service or inventory DB?
3. Name one design that avoids a distributed lock entirely for this decrement.
