# Benchmarks — `Benchmark*` & `b.N`

> Measure performance with `BenchmarkXxx(b *testing.B)`; the runner chooses `b.N` so the loop runs long enough to be stable.

## Plain English

Benchmarks live in `*_test.go` as `BenchmarkName`. You loop `for i := 0; i < b.N; i++` and do the work under test. The harness increases `N` until timing is meaningful. Report allocations with `b.ReportAllocs()`.

## Why interviewers ask

Seniors don’t guess — they benchmark before/after. Know how to avoid compiler dead-code elimination tricks and how to read `ns/op`, `B/op`, `allocs/op`.

## Example

```go
package strutil

import (
    "strings"
    "testing"
)

func BenchmarkConcatPlus(b *testing.B) {
    parts := []string{"a", "b", "c", "d", "e"}
    b.ReportAllocs()
    for i := 0; i < b.N; i++ {
        var s string
        for _, p := range parts {
            s += p
        }
        sink = s // prevent optimizing away
    }
}

func BenchmarkConcatBuilder(b *testing.B) {
    parts := []string{"a", "b", "c", "d", "e"}
    b.ReportAllocs()
    for i := 0; i < b.N; i++ {
        var sb strings.Builder
        for _, p := range parts {
            sb.WriteString(p)
        }
        sink = sb.String()
    }
}

var sink string
```

Run:

```bash
go test -bench=BenchmarkConcat -benchmem -count=5 ./...
go test -bench=. -cpuprofile=cpu.out ./...
```

Compare with `benchstat` (x/perf) when doing real optimizations.

## Tips for honest numbers

- Reset timer after setup: `b.ResetTimer()` (and `b.StopTimer`/`StartTimer` around expensive setup).
- Use `b.RunParallel` for concurrent code paths.
- Keep inputs realistic (size, hit rate, contention).
- Assign to a package-level `sink` so results aren’t eliminated.

## Pitfalls

- Benchmarking the allocator of test setup instead of the function (`ResetTimer`).
- Tiny microbenchmarks that don’t match production (caches, GC, PGO).
- Trusting a single run — use `-count` and `benchstat`.
- Forgetting `-benchmem` when claiming “fewer allocations.”

## Interview trigger phrase

> “I’d write a `Benchmark` with `ReportAllocs`, reset the timer after setup, run with `-count` and `benchstat`, then only optimize what the numbers show.”

## Exercise

Benchmark `json.Marshal` vs a hand-written `AppendJSON` for a small struct. What metrics convince you the custom path is worth the complexity?
