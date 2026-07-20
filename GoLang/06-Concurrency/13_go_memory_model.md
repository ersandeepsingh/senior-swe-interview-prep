# Go Memory Model

> The **Go memory model** defines when a write in one goroutine is **guaranteed visible** to a read in another. Visibility requires a **happens-before** edge created by synchronization (channel ops, mutex unlock/lock, `once`, atomics, `waitgroup`, etc.). Without sync, races are undefined — not “eventually consistent.”

## Plain English

CPUs and compilers reorder reads/writes. Within one goroutine, you see your own writes in program order. Across goroutines, **you need synchronization** or the other goroutine may see stale/torn values forever (or crash under `-race`).

Rule of thumb: if two goroutines access the same variable and at least one writes, they must synchronize — mutex, channel, atomic, etc.

## Interviewer Angle

- What is happens-before in Go?
- Does `go` create happens-before? (start of goroutine happens after the `go` statement’s initiation; but data written *before* `go` is visible to the new goroutine)
- Channel send happens-before corresponding receive?
- Unlock happens-before later Lock on same mutex?
- Why is unsynchronized “flag = true” then read elsewhere a race?

## Go Examples

### Data race (undefined)

```go
var a int
go func() { a = 1 }()
fmt.Println(a) // race: may print 0 or 1; illegal
```

### Channel establishes happens-before

```go
var a int
done := make(chan struct{})
go func() {
	a = 1
	close(done) // send/close happens-before receive
}()
<-done
fmt.Println(a) // guaranteed 1
```

### Mutex

```go
var (
	mu sync.Mutex
	a  int
)
// writer
mu.Lock()
a = 1
mu.Unlock() // unlock happens-before next lock

// reader
mu.Lock()
fmt.Println(a) // sees write
mu.Unlock()
```

### Init before go is visible

```go
a := 1
go func() {
	fmt.Println(a) // sees 1 — happens-before from go statement
}()
```

## Key happens-before edges (interview shortlist)

| Synchronization | Edge |
|-----------------|------|
| `go f()` | Initiation of `go` happens-before start of `f` |
| Channel send → receive | Send happens-before completion of receive |
| `close(ch)` → receive | Close happens-before receive seeing closed |
| `Unlock` → later `Lock` | Unlock happens-before subsequent Lock |
| `Once.Do` | Completion of `f` happens-before return of any `Do` |
| `WaitGroup` | `Done` happens-before `Wait` returns |
| Atomic | Synchronizing atomics establish order (see model docs) |

## Gotchas

| Gotcha | Detail |
|--------|--------|
| Believing “it works on my machine” | Races are Heisenbugs; use `-race` |
| Using `time.Sleep` as sync | Not synchronization |
| Reading map while another writes | Race (and can panic fatally) |
| Double-checked locking without atomics/memory barriers | Easy to get wrong; prefer `Once` |
| Assuming volatile like Java | Go has no volatile; use atomics |

## Trigger Phrase

> “Without happens-before from channels, mutexes, or atomics, a write in one goroutine isn’t guaranteed visible — I’d rather show a race with `-race` than claim timing makes it safe.”

## Exercise

Explain whether this is safe, and fix it if not:

```go
var ready bool
var data string

go func() {
	data = "hello"
	ready = true
}()

for !ready {
}
fmt.Println(data)
```

Discuss: busy loop, missing sync, and a correct version with channel, Mutex, or `atomic.Bool`.
