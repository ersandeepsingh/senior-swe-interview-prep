# sync/atomic

> Package **`sync/atomic`** provides lock-free primitives for concurrent read/modify/write of integers and pointers: `Add`, `Load`, `Store`, `Swap`, `CompareAndSwap` (CAS). Correct use establishes happens-before; incorrect mixing with non-atomic access is still a data race.

## Plain English

Atomics are CPU-level indivisible ops on a word-sized value. Great for counters, flags, and lock-free snapshots of a pointer. They are not a substitute for designing algorithms carefully — CAS loops can livelock under contention, and compound invariants still need mutexes.

Prefer the typed APIs (`atomic.Int64`, `atomic.Pointer[T]`, etc., Go 1.19+) over the older `*int64` functions.

## Interviewer Angle

- When atomics vs Mutex?
- What is CAS and how do you use it for lock-free update?
- Is `i++` atomic? (no)
- Memory ordering / happens-before with atomics?
- Can atomics fix map races? (no — maps need mutex or sync.Map)

## Go Examples

```go
var hits atomic.Int64

func handler() {
	hits.Add(1)
}

func stats() int64 {
	return hits.Load()
}
```

```go
// Atomic flag
var ready atomic.Bool

go func() {
	initAll()
	ready.Store(true)
}()

for !ready.Load() {
	runtime.Gosched()
}
```

```go
// CAS loop: bump version only if unchanged
var version atomic.Uint64

func tryBump(expect uint64) bool {
	return version.CompareAndSwap(expect, expect+1)
}
```

```go
// atomic.Pointer for lock-free config swap
var cfg atomic.Pointer[Config]

func SetConfig(c *Config) { cfg.Store(c) }
func GetConfig() *Config  { return cfg.Load() }
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| Non-atomic read of atomically written var | Data race — always Load/Store |
| Using atomics for multi-field invariants | Need mutex or transactional design |
| Alignment on 32-bit | Shared ints historically needed alignment; prefer typed atomics |
| `sync.Map` “because atomics” | Different tool; know its use cases |
| Assuming atomics are always faster | Contended CAS can lose to a simple Mutex |

## Trigger Phrase

> “Atomics give lock-free single-word ops and happen-before — I use them for counters and pointer swaps, not for protecting multi-field state.”

## Exercise

Implement a lock-free “latest value” holder `type Slot[T any]` with `Store(*T)` and `Load() *T` using `atomic.Pointer`. Then explain why a method `Update(func(*T) *T)` that reads, mutates, and writes back is *not* safely lock-free without a CAS loop — and write the CAS version.
