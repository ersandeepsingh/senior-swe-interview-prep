# Runtime, Memory & Performance — Senior Go Prep

This is the **internals grill**. Be able to draw GMP, explain tri-color GC, and walk a profiling → optimize → verify loop.

| # | Topic | File |
|---|-------|------|
| 1 | Goroutine scheduler (GMP) | [01_gmp_scheduler.md](01_gmp_scheduler.md) |
| 2 | Garbage collector | [02_garbage_collector.md](02_garbage_collector.md) |
| 3 | Escape analysis & allocation | [03_escape_analysis_allocation.md](03_escape_analysis_allocation.md) |
| 4 | Memory optimization | [04_memory_optimization.md](04_memory_optimization.md) |
| 5 | `GOMAXPROCS` | [05_gomaxprocs.md](05_gomaxprocs.md) |
| 6 | Inlining & compiler opts | [06_inlining.md](06_inlining.md) |
| 7 | Performance profiling workflow | [07_performance_profiling_workflow.md](07_performance_profiling_workflow.md) |

**How to study:** whiteboard GMP + GC in 5 minutes each → explain one escape decision from `go build -gcflags="-m"` → narrate a pprof workflow.
