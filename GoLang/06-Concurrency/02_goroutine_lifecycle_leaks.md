# Goroutine Lifecycle & Leaks

> A goroutine **lives** from `go` until its function returns. A **leak** is a goroutine that never returns — usually blocked on a channel, mutex, `select`, network, or waiting for a signal that never comes — retaining stack and referenced heap forever.

## Plain English

Every goroutine you start is a promise that something will eventually finish. If that promise breaks (nobody receives, nobody cancels, nobody closes), the goroutine sits forever. In long-running services, leaks show up as rising goroutine counts in `pprof` and growing memory.

Healthy lifecycle: start → do work (optionally listen for cancel) → exit path always reachable → someone waits/joins if needed.

## Interviewer Angle

- How do you detect leaks? (`runtime.NumGoroutine`, `pprof` goroutine profile, leak tests)
- Common leak patterns? (blocked send, unread receive, `time.After` in loops, missing `ctx` cancel)
- How do you design exit? (close channel, `context` cancel, done channel)
- Who owns cancellation vs who owns waiting?

## Go Examples

### Leak: sender blocked forever

```go
func leak() {
	ch := make(chan int)
	go func() {
		ch <- 1 // blocks forever — no receiver
	}()
	// function returns; goroutine still blocked → leak
}
```

### Fix: buffered send, or ensure receive, or use select + cancel

```go
func noLeak(ctx context.Context) {
	ch := make(chan int, 1) // buffer 1: send can complete without live receiver
	go func() {
		select {
		case ch <- 1:
		case <-ctx.Done():
			return
		}
	}()
}
```

### Leak: worker waiting on jobs that never close

```go
func startWorker(jobs <-chan Job) {
	go func() {
		for job := range jobs { // exits only when jobs is closed
			handle(job)
		}
	}()
}
// If jobs is never closed and never receives, worker may idle forever
// (range on open idle chan blocks — intentional park, still a "leak" if abandoned).
```

### Always pair start with cancel

```go
ctx, cancel := context.WithCancel(context.Background())
defer cancel() // critical: cancel even on early return

go worker(ctx)
// ...
```

## Gotchas

| Gotcha | Fix |
|--------|-----|
| Unbuffered send with no guaranteed receiver | Buffer, `select`+default/cancel, or ensure receive |
| Parent returns without canceling children | `defer cancel()`; pass `ctx` down |
| `time.After` inside a hot `select` loop | Use `time.NewTimer` and `Stop`/`Reset` |
| HTTP handler starts goroutine, request ends | Tie work to `r.Context()` |
| Tests that ignore leftover goroutines | Assert `NumGoroutine` or use leak helpers |

## Trigger Phrase

> “A leak is a goroutine with no reachable exit — I design every `go` with a cancel path and verify with goroutine profiles that counts return to baseline.”

## Exercise

Given a function that starts a background poller reading from a channel forever, refactor it so: (1) it stops on `context` cancel, (2) it does not leak if the parent returns early, (3) you can unit-test that goroutine count returns to start after cancel.
