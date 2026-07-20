# Profiling — `pprof` (CPU/Heap/Goroutine) & `trace`

> Measure before optimizing: **`pprof`** for CPU, heap, blocking, mutex, goroutines; **`trace`** for latency/scheduling timelines.

## Why interviewers ask 🔴⭐

Senior signal: don’t guess hotspots. Know how to capture a profile, open it, and read a flame graph / top entries.

## Ways to capture

### 1) Tests / benchmarks

```bash
go test -bench=. -cpuprofile=cpu.out -memprofile=mem.out ./pkg
go tool pprof cpu.out
```

### 2) `net/http/pprof` in a service

```go
import _ "net/http/pprof"

go func() {
    log.Println(http.ListenAndServe("localhost:6060", nil))
}()
```

```bash
go tool pprof https://localhost:6060/debug/pprof/profile?seconds=30
go tool pprof https://localhost:6060/debug/pprof/heap
go tool pprof https://localhost:6060/debug/pprof/goroutine
curl -o trace.out https://localhost:6060/debug/pprof/trace?seconds=5
go tool trace trace.out
```

### 3) One-off in code

```go
f, _ := os.Create("cpu.out")
_ = pprof.StartCPUProfile(f)
defer pprof.StopCPUProfile()
```

## Reading pprof

```text
(pprof) top10
(pprof) list MyFunc
(pprof) web          # needs graphviz
```

Or UI:

```bash
go tool pprof -http=:8080 cpu.out
```

Look for: flat % (self time) vs cum % (including callees). Heap: `inuse_space` vs `alloc_space`.

## What each profile answers

| Profile | Question |
|---------|----------|
| CPU | Where is time spent executing? |
| heap | What holds memory / who allocates? |
| goroutine | What’s runnable or stuck? stacks of all Gs |
| mutex / block | Who contends on locks / channel blocks? |
| trace | How do latency & scheduling look over time? |

## Pitfalls

- Profiling a quiet process — capture under realistic load.
- Leaving `pprof` exposed on public interfaces — bind to localhost or protect it.
- Optimizing a function that is 0.5% of CPU because it “looks slow.”
- Confusing allocated bytes with retained heap (`alloc_space` vs `inuse_space`).
- Ignoring GC — sometimes high CPU is GC from allocation churn (see Runtime section).

## Interview trigger phrase

> “I’d reproduce under load, grab CPU and heap pprof, confirm the hotspot, optimize, then re-bench and re-profile to verify.”

## Exercise

Your service RSS grows over hours. Which profiles do you take first, what do you look for, and how do you tell a leak from a growing legitimate cache?
