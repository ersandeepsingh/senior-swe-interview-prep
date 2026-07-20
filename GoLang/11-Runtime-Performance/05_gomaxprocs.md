# `GOMAXPROCS` — Parallelism vs Concurrency

> **`GOMAXPROCS`** sets how many OS threads may execute Go code **simultaneously** (the P count). Concurrency (many goroutines) ≠ parallelism (many running at once).

## Plain English

You can have 100,000 goroutines (concurrency) with `GOMAXPROCS=1` (they interleave on one P). Raise Ps to use multiple cores for CPU-bound Go code. Default since Go 1.5: number of CPUs (`runtime.NumCPU()`).

## Why interviewers ask 🟡⭐

Classic trap question: “Does more goroutines mean more cores used?” — No. Also: containers historically saw wrong CPU counts (cgroup); Go 1.5–1.18 era issues led to packages like `automaxprocs` — know the story.

## API

```go
n := runtime.GOMAXPROCS(0)     // read current
prev := runtime.GOMAXPROCS(4)  // set to 4, returns previous
fmt.Println(n, prev, runtime.NumCPU())
```

```bash
GOMAXPROCS=2 go run .
```

## When to change it

| Situation | Guidance |
|-----------|----------|
| CPU-bound pure Go | default ≈ NumCPU is usually right |
| Heavy cgo / foreign threads | may need careful tuning; measure |
| Latency-sensitive + noisy neighbor | sometimes pin lower to reduce scheduling noise |
| Container with CPU quota | ensure Go sees quota (runtime / `automaxprocs`) |

## Concurrency vs parallelism (say this)

```text
Concurrency: structure of the program (many tasks in flight)
Parallelism: simultaneous execution (needs multiple Ps + cores)
```

Channels/mutexes organize concurrency; `GOMAXPROCS` enables parallelism of Go code.

## Pitfalls

- Setting `GOMAXPROCS` ridiculously high “for speed” — more threads ≠ faster; more overhead.
- Confusing it with a goroutine limit — it isn’t.
- Ignoring container CPU limits → throttling + poor scheduling assumptions.
- Changing it at runtime casually without understanding impact on pools/third-party libs.

## Interview trigger phrase

> “`GOMAXPROCS` is the P count — parallelism of Go code — not a cap on goroutines; I’d leave it at CPU count unless profiling says otherwise, especially in containers.”

## Exercise

A CPU-bound worker pool has 10,000 jobs and 10,000 goroutines on an 8-core machine. What `GOMAXPROCS` do you want, and how would you size the worker pool instead of spawning 10k goroutines?
