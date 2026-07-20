# Map Gotchas

> Maps are **not concurrency-safe**. You cannot take the address of a map element. Writing to a **nil** map panics. Concurrent read+write without sync can crash the process (fatal race), not just misread data.

## Plain English

One goroutine writes, another ranges or reads — without a mutex or the map confined to one goroutine — the runtime may detect the race and terminate (`concurrent map writes` / `concurrent map read and map write`). Use `sync.Mutex`, `sync.RWMutex`, or `sync.Map` (specialized), or shard.

`&m[k]` is illegal — map values move on growth. Store pointers as values if you need addressability: `m[k] = &User{}` then mutate `*m[k]`.

Nil map: `var m map[string]int`; `x := m["a"]` is fine (`0`); `m["a"] = 1` panics.

## Interviewer Angle

- Why can’t you take `&m[k]`?
- How do you make a map safe for concurrent use?
- When is `sync.Map` appropriate vs plain map+mutex?
- What happens on concurrent map write?

## Go Examples

```go
var m map[string]int
fmt.Println(m["x"]) // 0 — ok
// m["x"] = 1      // panic

m = make(map[string]int)
m["x"] = 1
```

```go
// Not addressable
type Counter struct{ N int }
m := map[string]Counter{"a": {N: 1}}
// m["a"].N++ // compile error
c := m["a"]
c.N++
m["a"] = c // write whole value back

// Or store pointers
mp := map[string]*Counter{"a": {N: 1}}
mp["a"].N++
```

```go
// Concurrent access — protect
var (
	mu sync.Mutex
	m  = make(map[string]int)
)
mu.Lock()
m["k"]++
mu.Unlock()
```

## Bad vs Good

```go
// Bad: shared map, no lock
go func() { m["a"] = 1 }()
go func() { fmt.Println(m["a"]) }()

// Good: confine or lock
// (1) only one goroutine owns m
// (2) sync.Mutex around all access
// (3) communicate results over channels instead
```

## Trigger Phrase

> “Maps aren’t concurrent-safe, elements aren’t addressable, and nil maps panic on write. I either confine the map, lock it, or redesign around channels.”

## Exercise

Fix this type so callers can increment a named counter without the “cannot assign to struct field” error, and make increments safe under two goroutines:

```go
type Stats struct {
	counts map[string]int
}
func (s *Stats) Inc(name string) { /* ... */ }
```
