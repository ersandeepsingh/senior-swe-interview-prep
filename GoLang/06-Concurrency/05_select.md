# select

> `select` waits on multiple channel operations and runs **one** ready case. If several are ready, Go chooses **uniformly at random**. A `default` makes `select` non-blocking. Empty `select {}` blocks forever.

## Plain English

`select` is a multiplexer for channels — like `switch`, but cases are channel sends/receives that compete on readiness. Use it for timeouts, cancellation, non-blocking try-send/try-receive, and multi-channel orchestration.

## Interviewer Angle

- What if two cases are ready? (pseudo-random choice — not FIFO priority)
- Role of `default`?
- How do you implement timeout? (`time.After` / timer)
- How do you cancel a blocked operation? (`<-ctx.Done()`)
- Why is `time.After` in a loop dangerous?

## Go Examples

```go
select {
case v := <-a:
	fmt.Println("from a", v)
case b <- x:
	fmt.Println("sent to b")
case <-time.After(100 * time.Millisecond):
	fmt.Println("timeout")
case <-ctx.Done():
	return ctx.Err()
}
```

```go
// Non-blocking try-receive
select {
case v := <-ch:
	use(v)
default:
	// nothing ready
}
```

```go
// Prefer NewTimer in loops to avoid timer leaks.
func loop(ctx context.Context, ch <-chan Event) error {
	t := time.NewTimer(time.Second)
	defer t.Stop()
	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case e, ok := <-ch:
			if !ok {
				return nil
			}
			handle(e)
			if !t.Stop() {
				select {
				case <-t.C:
				default:
				}
			}
			t.Reset(time.Second)
		case <-t.C:
			onIdle()
			t.Reset(time.Second)
		}
	}
}
```

```go
// Nil channel to dynamically disable a case
var merge <-chan int
if enabled {
	merge = upstream
}
select {
case v := <-merge: // if merge is nil, this case is never chosen
	...
case <-ctx.Done():
	return
}
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| Assuming case order = priority | False; random among ready |
| `time.After` every iteration | Creates a new timer each time; GC/leak under load |
| Forgetting to drain timer after `Stop` | Spurious wake on next `select` |
| `default` busy-spin | Can burn CPU; prefer blocking or backoff |
| Send + receive in one select without care | Can livelock with another peer’s select |

## Trigger Phrase

> “`select` multiplexes channel ops; if multiple are ready Go picks at random — I use `ctx.Done()` and careful timers, not `time.After` in hot loops.”

## Exercise

Write `FetchWithTimeout(ctx, url, d)` that starts an HTTP GET in a goroutine and returns either the body, `context` error, or timeout — using `select`, without leaking the HTTP goroutine on cancel/timeout. (Discuss trade-offs if the HTTP call can’t be aborted mid-flight without `http.Request.WithContext`.)
