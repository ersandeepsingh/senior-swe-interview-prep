# Race Conditions & -race

> A **data race** occurs when two goroutines access the same memory concurrently and at least one write is unsynchronized. Go’s **race detector** (`go test -race`, `go run -race`) instruments memory accesses and reports races at runtime. Races are bugs — not “rare timing issues.”

## Plain English

If two people edit the same spreadsheet cell without locking, corruption is inevitable. The race detector watches accesses while your tests/load run and screams when it sees conflicting unsynchronized access. It finds bugs that code review misses — but only on paths that execute.

## Interviewer Angle

- Define data race vs general race condition (logic races, TOCTOU).
- How does `-race` work at a high level? (shadow memory, happens-before)
- Cost of `-race`? (~2–20× CPU, more memory — use in CI/tests, not always prod)
- How do you fix races? (mutex, channel ownership, atomics, copy-on-write)
- Map concurrent access? (fatal races; can panic)

## Go Examples

### Classic race

```go
var count int
var wg sync.WaitGroup
for i := 0; i < 1000; i++ {
	wg.Add(1)
	go func() {
		defer wg.Done()
		count++ // DATA RACE
	}()
}
wg.Wait()
```

### Fix with mutex

```go
var (
	mu    sync.Mutex
	count int
)
// ...
mu.Lock()
count++
mu.Unlock()
```

### Fix with atomic

```go
var count atomic.Int64
count.Add(1)
```

### Fix with ownership (no shared write)

```go
results := make(chan int, n)
// each goroutine sends its result; main aggregates — no shared counter
```

```bash
go test -race ./...
go run -race .
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| “No race report ⇒ no races” | Only on executed paths; need good tests/load |
| Fixing by sleeping | Not a fix |
| Interface / slice header races | Headers are multiword — still races |
| False sense from buffered channels | Sync only at actual send/receive |
| Ignoring races in tests as flaky | Treat as P0 |

## Trigger Phrase

> “A data race is unsynchronized concurrent access with a write — I run `-race` in CI, then fix with clear ownership, a mutex, or atomics, never with sleeps.”

## Exercise

Here’s a buggy cache. Identify the race(s), write a failing test that `-race` catches, and fix it two ways (Mutex vs “confine map to one goroutine”).

```go
type Cache struct{ m map[string]string }

func (c *Cache) Get(k string) string { return c.m[k] }
func (c *Cache) Set(k, v string)     { c.m[k] = v }
```
