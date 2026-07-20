# Garbage Collector — Concurrent Tri-Color Mark-Sweep

> Go’s GC is a **concurrent, non-generational (mostly), tri-color mark-sweep** collector with write barriers; tune with **`GOGC`** / memory limit (`GOMEMLIMIT`).

## Plain English

When you allocate, the heap grows. The GC finds live objects (reachable from roots: stacks, globals, registers) and reclaims the rest. Marking runs **concurrently** with your program; short “stop-the-world” (STW) phases exist but are designed to be brief. Tri-color: **white** = not yet seen, **grey** = seen but children not scanned, **black** = scanned.

## Why interviewers ask 🔴⭐

Latency, allocation rate, and `GOGC` trade-offs are senior territory. Know write barriers exist so concurrent mutation doesn’t hide pointers, and that the best GC tuning is often **allocating less**.

## Lifecycle (simplified)

1. **STW** — enable write barrier, scan roots briefly.
2. **Concurrent mark** — drain grey objects; mutators may allocate / shade via barriers.
3. **Mark termination STW** — finish marking.
4. **Sweep** — reclaim white spans (often lazy/concurrent).
5. Repeat when heap grows enough vs last GC (controlled by `GOGC`).

## Tuning knobs

```bash
GOGC=100          # default: next GC when heap grows ~100% since last mark
GOGC=50           # more frequent GC → lower peak heap, more CPU
GOGC=200          # rarer GC → higher heap, less GC CPU
GOMEMLIMIT=8GiB   # soft memory limit (Go 1.19+); GC works harder near limit
GODEBUG=gctrace=1 # log GC lines
```

```go
debug.SetGCPercent(50)
debug.SetMemoryLimit(8 << 30)
runtime.GC() // manual — rare; mostly tests/benchmarks
```

## What to say about latency

- GC CPU is proportional to **allocation rate** and live-set scan work.
- Large pointer-rich heaps cost more to mark than large byte buffers.
- Reducing allocs (`sync.Pool`, reuse buffers, fewer interfaces boxing) beats micro-tuning `GOGC` alone.

## Pitfalls

- Setting `GOGC=off` in prod without a hard plan → OOM.
- Blaming GC for CPU when the app allocates 10GB/s — fix allocs.
- Assuming generational myths from JVM apply 1:1 (Go’s design differs; focus on concurrent mark + pacing).
- Ignoring `gctrace` / pprof heap when debugging latency spikes.

## Interview trigger phrase

> “Concurrent tri-color mark-sweep with write barriers; I’d cut allocation rate first, then tune `GOGC`/`GOMEMLIMIT` against latency and RSS goals.”

## Exercise

A service’s p99 latency spikes every few seconds; `GODEBUG=gctrace=1` shows frequent GCs and high assist time. What metrics do you check next, and what code-level changes do you try before changing `GOGC`?
