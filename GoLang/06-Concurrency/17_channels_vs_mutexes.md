# Channels vs Mutexes

> Go proverb: **“Don’t communicate by sharing memory; share memory by communicating.”** Channels transfer ownership and synchronize; mutexes protect shared memory in place. Seniors choose based on ownership, contention, API clarity, and cancellation — not dogma.

## Plain English

| Tool | Mental model |
|------|----------------|
| **Channel** | Pass the data (or token) to someone else; after send, you don’t touch it |
| **Mutex** | Many goroutines may touch the same data; lock while you do |

Channels shine for pipelines, handoffs, and bounding work. Mutexes shine for caches, registries, and graphs of shared mutable state where “message everything” would be awkward.

## Interviewer Angle

- When would you refuse channels?
- When is a mutex clearer than a channel?
- “Share by communicating” — what does ownership mean?
- Hybrid designs? (mutex inside a struct; channel for jobs)
- Performance: is one always faster? (no — measure)

## Go Examples

### Channel ownership (no shared mutation)

```go
func sum(ch <-chan int) int {
	total := 0
	for v := range ch {
		total += v // only this goroutine touches total
	}
	return total
}
```

### Mutex for shared map

```go
type Store struct {
	mu sync.RWMutex
	m  map[string]int
}

func (s *Store) Incr(k string) {
	s.mu.Lock()
	s.m[k]++
	s.mu.Unlock()
}
```

### Channel as semaphore (bound concurrency)

```go
sem := make(chan struct{}, 8)
```

### Prefer mutex: complex in-place update

```go
// Updating many related fields atomically is clearer under one Lock
// than round-tripping messages for every field.
mu.Lock()
acct.Balance -= amt
acct.Updated = time.Now()
mu.Unlock()
```

## Decision guide

| Prefer **channels** when… | Prefer **mutexes** when… |
|---------------------------|---------------------------|
| Transferring ownership of a value/task | Many readers/writers of one structure |
| Pipelines / fan-in / fan-out | Caches, indexes, connection tables |
| Natural backpressure between stages | Fine-grained in-place updates |
| Signaling done/cancel (often with `ctx`) | Hot counters (or use atomics) |
| You want the type system to show direction | Graph-like shared state |

## Gotchas

| Gotcha | Detail |
|--------|--------|
| Channel for everything | Callback spaghetti; hard cancellation |
| Mutex for everything | Hidden coupling; easy lock-order bugs |
| Big channel buffers as “async mutex” | Latency and memory bombs |
| Holding mutex across channel send | Deadlock risk |
| Treating proverb as absolute law | Idiomatic Go uses both freely |

## Trigger Phrase

> “Channels when I’m passing ownership through a pipeline; mutexes when I’m protecting shared structures — I pick the one that makes ownership and exit paths obvious.”

## Exercise

Design an in-memory rate limiter used by 1000 goroutines. Sketch (1) a mutex + map design and (2) a single coordinating goroutine with channels. Discuss latency, fairness, cancellation, and testability — pick one and justify.
