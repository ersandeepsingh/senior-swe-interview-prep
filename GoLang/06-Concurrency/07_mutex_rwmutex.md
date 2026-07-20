# sync.Mutex / RWMutex

> A **`Mutex`** provides exclusive mutual exclusion: only one goroutine holds the lock. An **`RWMutex`** allows many concurrent readers **or** one writer. Both are in package `sync`. Unlock must be called by the locking goroutine (no recursive locks).

## Plain English

When goroutines share memory (map, struct fields, counters), you need a lock or atomic ops so reads/writes don’t race. Mutex = bathroom lock (one at a time). RWMutex = library: many can read together, but writing needs the room alone.

Go’s mantra prefers channels, but mutexes are correct and idiomatic for protecting in-memory shared state (caches, registries, metrics).

## Interviewer Angle

- Value vs pointer receiver for types embedding Mutex? (don’t copy the mutex — hold by pointer / never copy the struct after first use)
- RWMutex when? (read-heavy; writers rare)
- Can RWMutex deadlock with upgrade? (no lock upgrade; don’t Lock while holding RLock in same goroutine)
- Defer Unlock — yes/no? (yes for clarity; watch long critical sections)
- Mutex vs channel for a counter?

## Go Examples

```go
type Counter struct {
	mu sync.Mutex
	n  int
}

func (c *Counter) Inc() {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.n++
}

func (c *Counter) Value() int {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.n
}
```

```go
type Cache struct {
	mu sync.RWMutex
	m  map[string]string
}

func (c *Cache) Get(k string) (string, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()
	v, ok := c.m[k]
	return v, ok
}

func (c *Cache) Set(k, v string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.m[k] = v
}
```

```go
// Copying a struct with a mutex is a bug.
type Bad struct {
	mu sync.Mutex
	n  int
}

func oops(b Bad) { // copies mutex state — undefined / races
	b.mu.Lock()
	b.n++
	b.mu.Unlock()
}
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| Copying Mutex / containing struct | Broken locking; vet warns with `-copylocks` |
| Lock order A→B vs B→A | Classic deadlock |
| Holding lock across slow I/O | Kills throughput; release early |
| RWMutex always “faster” | Writers can starve; overhead if writes aren’t rare |
| Recursive lock expectations | Go mutexes are not reentrant → self-deadlock |

## Trigger Phrase

> “Mutex guards shared memory; RWMutex helps read-heavy paths — never copy a locked struct, keep critical sections short, and fix lock ordering to avoid deadlocks.”

## Exercise

Implement a thread-safe TTL cache with `Get`/`Set`/`Delete`. Explain whether you chose `Mutex` or `RWMutex`, how expiry interacts with locking, and how you’d avoid holding the lock during a slow “load on miss” DB call (singleflight).
