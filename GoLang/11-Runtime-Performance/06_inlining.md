# Inlining & Compiler Optimizations

> The compiler **inlines** small functions (copies callee into caller) to remove call overhead and unlock further opts; see decisions with `-gcflags="-m"`.

## Plain English

A function call has cost (stack setup, register shuffle). If a function is small/leaf-ish, the compiler may inline it. After inlining, more escape analysis and constant folding can kick in. Not all functions inline — `go:noinline`, large bodies, some constructs block it.

## Why interviewers ask 🔴

Shows you understand performance comes from the compiler + algorithms, not hand-written macros. Know how to *observe* inlining, not worship it.

## Observe

```bash
go build -gcflags="-m" ./pkg 2>&1 | grep inline
# can inline Foo
# inlining call to Foo
```

Force for experiments:

```go
//go:noinline
func sink(x int) { _ = x }
```

## What helps inlining

- Small functions
- Leaf functions (don’t call much else)
- Avoiding language features that inhibit mid-stack inlining in older compilers (varies by version)

## Other compiler goodies (high level)

| Opt | Idea |
|-----|------|
| Escape analysis | stack vs heap |
| Bounds check elimination | prove indices safe |
| Devirtualization | sometimes concrete calls behind interfaces |
| Dead code elimination | drop unused results |
| PGO (profile-guided opts) | Go 1.20+: feed CPU profile to optimize hotter paths |

```bash
go test -bench=. -cpuprofile=cpu.pprof ./...
go build -pgo=cpu.pprof -o app ./cmd/app
```

## Pitfalls

- Manually micro-splitting or merging functions “for inlining” without benchmarks.
- Assuming interface calls are free — they can inhibit some opts; still prefer clear design.
- Using `//go:noinline` in production without reason (debugging only usually).
- Ignoring PGO for large services where it’s an easy win.

## Interview trigger phrase

> “I’d check inlining with `-m`, keep hot helpers small enough to inline, and for big services consider PGO from production CPU profiles.”

## Exercise

Write a tiny `max(a, b int) int` and a loop that uses it. Show how you’d confirm it inlines, then explain why wrapping it in an interface method might change the story.
