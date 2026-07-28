# Latency Numbers Every Engineer Should Know

> Orders of magnitude beat fake precision. Use them to spot impossible designs (“I'll check disk on every keystroke”) in system design interviews.

## Plain English

Exact chips vary; **ratios** matter. Classic teaching numbers (Jeff Dean / “latency numbers every programmer should know”) are still the interview lingua franca — quote orders of magnitude, not nanosecond pedantry.

```text
  Bad idea:  20 sequential cross-region calls in one user request
             20 × 80ms = 1.6s before app work

  Better:    parallelize, batch, cache, keep chatty calls in-AZ
```

## Essentials (must-know for this topic)

### Orders-of-magnitude table

| Operation | ~Latency | Rough mental model |
|-----------|----------|--------------------|
| **L1 cache** ref | ~1 ns | — |
| **L2 cache** ref | ~3–10 ns | — |
| **RAM** ref | ~100 ns | — |
| **SSD** random read | ~10–100 µs | ~1000× RAM |
| **HDD** seek | ~5–10 ms | ~50–100× SSD |
| Same-AZ network RTT | ~0.5–2 ms | — |
| Cross-AZ | ~1–5 ms | — |
| Cross-region | ~30–150+ ms | continent dependent |
| Packet CA ↔ EU | ~150 ms | — |
| Read 1 MB from RAM | ~µs order | sequential ≫ random |
| Read 1 MB from SSD | ~100s µs – 1 ms | — |
| Read 1 MB over 1 Gbps net | ~10 ms | serialization delay |

### Design rules of thumb

| Smell | Why it fails |
|-------|--------------|
| Many **sequential cross-region** RPCs | Each hop costs tens–hundreds of ms |
| N+1 remote calls | Same as N+1 SQL, but slower |
| Disk on every keystroke | SSD is fast-ish; still not free at QPS |
| Ignoring p99 | GC, noisy neighbors, slow disks live in the tail |

**Budget:** RAM ≪ SSD ≪ same-AZ ≪ cross-region.

## Simple example

Design check: “For each feed item, fetch user from another region.”

- 50 items × 80ms sequential ≈ 4s → fail.
- Batch get in one RTT, or cache user profiles in-region → ok.

Disk vs network: sometimes fetching from remote SSD/cache is comparable to local disk — but **cross-region** is almost never free.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Keep data in-AZ with compute | Low latency | Weaker isolation / DR story |
| Sync cross-region on request path | Fresh global data | Multi-hundred-ms tax |
| Cache aggressively | Speed | Staleness |
| Many tiny RPCs | Nice service boundaries | Death by RTT (chatty APIs) |

## Pitfalls

- **Counting only compute** and ignoring serialization + RTT.
- **N+1 RPCs** across the network (same smell as N+1 SQL).
- **Using HDD-era intuition** for SSD/NVMe world — still: random tiny reads hurt.
- **Pretending p99 doesn't include GC pauses / slow disks / neighbor noise**.

## Interview trigger phrase

> “I'd budget latency by **orders of magnitude** — RAM vs SSD vs same-AZ vs cross-region — and avoid sequential cross-region chatter on the request path.”

## Exercise

A handler does: 1 local Redis get (same AZ), 1 Postgres query (same AZ), 1 HTTP call to a partner in another region. Estimate a realistic p50 floor and which hop dominates.
