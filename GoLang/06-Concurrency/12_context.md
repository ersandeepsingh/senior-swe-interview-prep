# context.Context

> `context.Context` carries **deadlines**, **cancellation signals**, and request-scoped **values** across API boundaries and goroutines. The empty root is `context.Background()`; derive with `WithCancel`, `WithTimeout`, `WithDeadline`, `WithValue`. Canceling a parent cancels children.

## Plain English

Context is how Go threads “please stop” and “this request dies at T+2s” through a call stack. You pass `ctx` as the first parameter. When the client disconnects or the deadline hits, `ctx.Done()` closes; workers should return promptly with `ctx.Err()` (`Canceled` or `DeadlineExceeded`).

Values are for request-scoped metadata (trace IDs), **not** for optional parameters or dependency injection.

## Interviewer Angle

- Why is `ctx` the first argument?
- Background vs TODO?
- WithValue — when yes / when no?
- Does canceling free resources automatically? (only if code checks `Done`)
- Context across goroutines — derived cancel?

## Go Examples

```go
func Handler(w http.ResponseWriter, r *http.Request) {
	ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
	defer cancel()

	result, err := fetch(ctx, r.URL.Query().Get("id"))
	if err != nil {
		http.Error(w, err.Error(), statusFor(err))
		return
	}
	_ = json.NewEncoder(w).Encode(result)
}

func fetch(ctx context.Context, id string) (Data, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, urlFor(id), nil)
	if err != nil {
		return Data{}, err
	}
	res, err := http.DefaultClient.Do(req)
	if err != nil {
		return Data{}, err
	}
	defer res.Body.Close()
	return decode(res.Body)
}
```

```go
ctx, cancel := context.WithCancel(context.Background())
defer cancel()

go worker(ctx)

// later, on shutdown:
cancel()
```

```go
// Select on cancellation
select {
case <-ctx.Done():
	return ctx.Err()
case job := <-jobs:
	return process(ctx, job)
}
```

```go
// Values: use private key type to avoid collisions
type ctxKey int
const traceKey ctxKey = 1

ctx = context.WithValue(ctx, traceKey, traceID)
id, _ := ctx.Value(traceKey).(string)
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| Storing Context in a struct long-term | Prefer pass as param; struct fields go stale |
| WithValue for optional deps | Hides dependencies; hard to test |
| Forgetting `defer cancel()` | Leaks timer goroutines from WithTimeout |
| Ignoring `ctx` in leaf calls | Cancellation becomes a lie |
| Using TODO in production paths | Fine temporarily; replace with real ctx |

## Trigger Phrase

> “Context propagates cancel and deadlines — first arg everywhere, `defer cancel()`, check `Done`, and reserve `WithValue` for request metadata like trace IDs.”

## Exercise

Design graceful shutdown for an HTTP server: on `SIGINT`, cancel a root context, stop accepting new work, let in-flight handlers finish (or hit timeout), and ensure worker pool goroutines exit. Sketch the `ctx` tree.
