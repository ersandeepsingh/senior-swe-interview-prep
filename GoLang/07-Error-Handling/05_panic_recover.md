# panic / recover

> **`panic`** aborts the normal call stack; deferred functions still run. **`recover`**, called inside a deferred function, catches a panic and resumes normal execution in that goroutine. Use panic for programmer bugs / impossible states; use errors for expected failures. Never use panic as a substitute for `return err`.

## Plain English

Panic is Go’s “this should never happen — stop the world (for this goroutine).” Recover is a safety net, typically at goroutine or HTTP handler boundaries so one bad request doesn’t crash the process. Recover only works in the same goroutine that panicked.

## Interviewer Angle

- When is panic acceptable?
- Where do you put recover?
- Does recover work across goroutines? (no)
- What happens to other goroutines if one panics unrecovered? (process can crash)
- Panic vs error for library APIs?

## Go Examples

```go
func mustCompile(expr string) *regexp.Regexp {
	re, err := regexp.Compile(expr)
	if err != nil {
		panic(err) // OK for immutable init with known-good patterns
	}
	return re
}
```

```go
func SafeHandler(h http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if rec := recover(); rec != nil {
				log.Printf("panic: %v\n%s", rec, debug.Stack())
				http.Error(w, "internal error", 500)
			}
		}()
		h.ServeHTTP(w, r)
	})
}
```

```go
// recover only in deferred call
func parse() (err error) {
	defer func() {
		if rec := recover(); rec != nil {
			err = fmt.Errorf("panic: %v", rec)
		}
	}()
	dangerous()
	return nil
}
```

```go
go func() {
	defer func() { recover() }() // must be IN this goroutine
	mightPanic()
}()
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| `recover()` outside `defer` | Always nil — useless |
| Swallowing panic without log | Hides bugs |
| Panicking in libraries for ordinary errors | Forces callers into recover |
| Assuming process continues after unrecovered panic | Usually fatal |
| Recover then continuing corrupt state | Better fail the request/unit of work |

## Trigger Phrase

> “Panic for truly exceptional bugs, recover at trust boundaries like HTTP handlers — expected failures stay as returned errors.”

## Exercise

Implement a worker pool where a panicking job must not kill the process: recover inside the worker, convert to an error on a results channel, and keep other workers running. Explain why recover on the main goroutine alone is insufficient.
