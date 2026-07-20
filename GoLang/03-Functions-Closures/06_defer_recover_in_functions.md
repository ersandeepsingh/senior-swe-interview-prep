# `defer` / `recover` in Functions

> `recover` stops a **panic** and returns the panic value — but only when called **directly** from a deferred function. Use it at boundaries (goroutine entry, HTTP middleware) to turn panics into errors/logs, not as everyday control flow.

## Plain English

`panic` unwinds the stack, running deferred calls. If a deferred call invokes `recover()`, the panic stops and that function can resume returning normally. If nothing recovers, the program crashes (all goroutines terminate for unrecovered panics on a goroutine — that goroutine dies; if it’s `main`, the process exits).

Idiom:

```go
defer func() {
	if r := recover(); r != nil {
		// log, convert to error, etc.
	}
}()
```

`recover()` outside a deferred call returns nil and does nothing useful.

## Interviewer Angle

- Where must `recover` live?
- Panic vs error — when is panic OK? (truly unrecoverable programmer bugs; not expected I/O failures)
- Recovering in a library vs at process edge?
- Does recover restore the program to a clean state? (you must still clean up)

## Go Examples

```go
func safeRun(fn func()) (err error) {
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("panic: %v", r)
		}
	}()
	fn()
	return nil
}
```

```go
// Goroutine boundary — never let a worker panic kill silently without logging
go func() {
	defer func() {
		if r := recover(); r != nil {
			log.Printf("worker panic: %v", r)
		}
	}()
	work()
}()
```

```go
// Wrong: recover not in defer
func bad() {
	recover() // no-op
	panic("x")
}
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Using panic for expected errors | Unidiomatic; hard to handle |
| Recovering and continuing with corrupted state | Masks bugs |
| Recover only in helper not deferred | Doesn’t catch |
| Forgetting re-panic when you can’t handle | Swallowing fatal conditions |

## Trigger Phrase

> “`recover` only works inside `defer`. I use panic for truly exceptional bugs, recover at boundaries to log and isolate, and return `error` for expected failures.”

## Exercise

Implement middleware-style `func Protect(h http.Handler) http.Handler` that recovers panics, logs the value, and responds `500` — without recovering panics that happen in a separate goroutine started by the handler (explain why).
