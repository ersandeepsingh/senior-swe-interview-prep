# Performance Profiling Workflow

> **Reproduce → measure → hypothesize → change one thing → re-measure → verify.** Never optimize blind.

## Plain English

A senior workflow is boring and effective: define the SLI (p99 latency, allocs/op, RSS), capture profiles under realistic load, pick the top offender, fix it, prove the win with benchmarks/`benchstat`, watch for regressions in CI.

## Why interviewers ask 🔴⭐

They want process, not folklore. Walk this loop out loud in system design / debugging rounds.

## The loop

```text
1. Define success     e.g. p99 < 50ms, or allocs/op < 10
2. Reproduce load     prod-like traffic, fixed dataset
3. Measure            pprof CPU/heap, trace, metrics, bench
4. Hypothesize        "JSON marshal dominates" / "lock contention"
5. Change one lever   buffer reuse, algorithm, sharding
6. Re-measure         same harness; benchstat before/after
7. Ship + guard       regression benchmark or dashboard alert
```

## Concrete command recipe

```bash
# Micro
go test -bench=BenchmarkHandler -benchmem -count=10 ./... | tee new.txt
benchstat old.txt new.txt

# Service under load
# terminal A: app with pprof on :6060
# terminal B: load generator
go tool pprof -http=:8080 http://localhost:6060/debug/pprof/profile?seconds=30
go tool pprof http://localhost:6060/debug/pprof/heap
go tool trace trace.out
```

## Decision tree (quick)

| Symptom | First tools |
|---------|-------------|
| High CPU | CPU pprof flame graph |
| Growing RSS | heap inuse + goroutine count |
| High latency, low CPU | trace, block/mutex profiles, GC gctrace |
| Throughput collapse under concurrency | mutex/block profiles, `-race` |

## Pitfalls

- Optimizing a bench that doesn’t match production shapes.
- Changing five things at once — can’t attribute the win.
- Celebrating lower CPU while latency worsens (or vice versa).
- Skipping `-race` after concurrency “optimizations.”

## Interview trigger phrase

> “I’d pin an SLI, profile under load, fix the top hotspot, prove it with benchstat, and only then tune GC or GOMAXPROCS.”

## Exercise

p99 jumps from 20ms to 200ms after a deploy. Outline your first 30 minutes: metrics, profiles, rollback criteria, and what code smells you’d hunt if heap `alloc_space` exploded.
