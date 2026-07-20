# Custom Error Types

> A **custom error type** is a user-defined type (usually a struct) that implements `Error() string`, optionally `Unwrap() error`, and sometimes `Is(error) bool`. Use fields for structured data callers need via `errors.As`.

## Plain English

When a string isn’t enough — you need a status code, a field name, or whether to retry — define a type. Keep it small and document which types are part of your public API.

## Interviewer Angle

- Value vs pointer receiver for `Error()`?
- Why implement `Unwrap`?
- Pointer vs value when using `errors.As`? (usually `As` into `**T` / `*T` matching what you returned)
- Temporary / Timeout interfaces (`net.Error`)?
- Opaque error structs (unexported fields) vs exported?

## Go Examples

```go
type HTTPError struct {
	Code int
	Op   string
	Err  error
}

func (e *HTTPError) Error() string {
	if e.Err != nil {
		return fmt.Sprintf("%s: status %d: %v", e.Op, e.Code, e.Err)
	}
	return fmt.Sprintf("%s: status %d", e.Op, e.Code)
}

func (e *HTTPError) Unwrap() error { return e.Err }

func (e *HTTPError) Is(target error) bool {
	t, ok := target.(*HTTPError)
	if !ok {
		return false
	}
	return e.Code == t.Code
}
```

```go
func Get(ctx context.Context, url string) error {
	res, err := // ...
	if err != nil {
		return &HTTPError{Op: "GET " + url, Err: err}
	}
	if res.StatusCode >= 400 {
		return &HTTPError{Code: res.StatusCode, Op: "GET " + url}
	}
	return nil
}

var he *HTTPError
if errors.As(err, &he) && he.Code == 404 {
	// handle not found
}
```

```go
// Marker methods for behavior
func (e *HTTPError) Temporary() bool {
	return e.Code == 429 || e.Code >= 500
}
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| Returning `HTTPError` by value but `As` into `*HTTPError` | Mismatch — be consistent (prefer pointers) |
| Exporting every field | Locks API; prefer accessors if needed |
| Forgetting Unwrap | Breaks `errors.Is` to causes |
| Huge hierarchy of error types | Prefer few types + sentinels |
| Implementing only `Error()` with no structure | Then just use `fmt.Errorf` |

## Trigger Phrase

> “Custom error types carry fields for `errors.As`; I add `Unwrap` so wrapping still works and keep the public error surface small.”

## Exercise

Define `RetryableError` with an underlying cause and `RetryAfter time.Duration`. Implement `Unwrap`, write a helper `func RetryAfter(err error) (time.Duration, bool)`, and show a client loop that backs off only when appropriate.
