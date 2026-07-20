# Deadlocks & Livelocks

> A **deadlock** is when goroutines wait on each other forever such that none can proceed. A **livelock** is when goroutines keep changing state but still make no useful progress. Go’s runtime detects some deadlocks when **all goroutines are asleep** and panics with `fatal error: all goroutines are asleep - deadlock!` — it does **not** detect every deadlock in a live process with other runnable Gs.

## Plain English

Deadlock = gridlock intersection; everyone waits, nobody moves. Livelock = two people in a hallway both politely stepping aside forever. In Go, channel waits, mutex lock order, and `WaitGroup` mistakes are the usual villains.

## Interviewer Angle

- Four Coffman conditions? (mutual exclusion, hold-and-wait, no preemption, circular wait)
- Why “all goroutines asleep” detection misses some deadlocks?
- Common Go deadlock patterns?
- How do you prevent lock-order deadlocks?
- Livelock vs starvation?

## Go Examples

### Unbuffered channel deadlock (single goroutine)

```go
ch := make(chan int)
ch <- 1 // blocks forever — no other goroutine to receive
```

### Classic lock-order deadlock

```go
var muA, muB sync.Mutex

go func() {
	muA.Lock()
	defer muA.Unlock()
	muB.Lock() // waits for B
	defer muB.Unlock()
}()

go func() {
	muB.Lock()
	defer muB.Unlock()
	muA.Lock() // waits for A → circular wait
	defer muA.Unlock()
}()
```

### WaitGroup deadlock

```go
var wg sync.WaitGroup
wg.Add(1)
wg.Wait() // forgot Done — hangs (may not trip "all asleep" if other Gs run)
```

### Self-deadlock (non-reentrant mutex)

```go
mu.Lock()
mu.Lock() // same goroutine — deadlock
```

### Livelock sketch

```go
// Both sides yield forever on conflict without a backoff winner.
for !tryLockBoth() {
	runtime.Gosched() // keeps running but never completes
}
```

## Prevention checklist

| Strategy | Practice |
|----------|----------|
| Lock ordering | Always acquire locks in a global order (A before B) |
| Timeouts / ctx | `select` with `ctx.Done()` instead of unbounded wait |
| Avoid hold-and-wait | Don’t hold lock A while blocking on channel/I/O that needs A |
| Channels ownership | Clear sender/closer; size buffers intentionally |
| Detection | `-race`, tracing, goroutine dumps (`SIGQUIT` / `pprof`) |

## Gotchas

| Gotcha | Detail |
|--------|--------|
| “Runtime always finds deadlocks” | Only when *no* goroutine is runnable |
| Buffered channel “can’t deadlock” | Full buffer + no receivers still deadlocks |
| Fixing deadlock by enlarging buffer | May hide design bug |
| Ignoring livelock | CPU busy, progress zero — look like a hang under load |
| RWMutex upgrade attempts | RLock then Lock in same G → deadlock |

## Trigger Phrase

> “Deadlocks are circular waits — I enforce lock order, bound waits with context, and remember the runtime only fatals when every goroutine is asleep.”

## Exercise

Diagnose this program: does it deadlock, livelock, race, or exit cleanly? Fix it.

```go
func main() {
	a := make(chan int)
	b := make(chan int)
	go func() {
		a <- 1
		<-b
	}()
	go func() {
		b <- 1
		<-a
	}()
	time.Sleep(time.Second)
}
```

(Hint: both block on send first — classic channel deadlock. Compare with swapping one side to receive-first or using `select`.)
