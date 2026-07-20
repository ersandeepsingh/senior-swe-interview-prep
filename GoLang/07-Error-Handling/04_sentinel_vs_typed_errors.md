# Sentinel vs Typed Errors

> A **sentinel error** is a predeclared package-level value (`var ErrNotFound = errors.New("...")`) compared with `errors.Is`. A **typed error** is a struct implementing `error` (often with fields) inspected with `errors.As`. Choose sentinels for simple stable conditions; types when callers need extra data or behavior.

## Plain English

Sentinel = named constant error: “not found,” “EOF,” “deadline exceeded.” Typed = rich object: HTTP status, field name that failed validation, retryable flag. Both are valid; mixing without a policy confuses API users.

## Interviewer Angle

- Examples from stdlib? (`io.EOF`, `sql.ErrNoRows`, `context.Canceled`)
- When is a type better than a sentinel?
- Exporting sentinels — API compatibility?
- Opaque errors vs inspectable errors (Dave Cheney / Go blog guidance)?
- Should callers depend on `Error()` text? (no)

## Go Examples

### Sentinel

```go
package user

import "errors"

var ErrNotFound = errors.New("user: not found")

func Find(id string) (*User, error) {
	// ...
	return nil, ErrNotFound
}

// caller
if errors.Is(err, user.ErrNotFound) {
	// 404
}
```

### Typed

```go
type ValidationError struct {
	Field string
	Msg   string
}

func (e *ValidationError) Error() string {
	return fmt.Sprintf("%s: %s", e.Field, e.Msg)
}

func Parse(email string) error {
	if !strings.Contains(email, "@") {
		return &ValidationError{Field: "email", Msg: "invalid format"}
	}
	return nil
}

var ve *ValidationError
if errors.As(err, &ve) {
	fmt.Println(ve.Field)
}
```

### Hybrid

```go
// Sentinel for class of error; type for details
var ErrInvalid = errors.New("invalid")

type InvalidError struct {
	Field string
	err   error // ErrInvalid
}

func (e *InvalidError) Error() string { return e.Field + ": invalid" }
func (e *InvalidError) Unwrap() error { return e.err }
```

## Decision guide

| Prefer **sentinel** when… | Prefer **typed** when… |
|---------------------------|------------------------|
| Binary condition (found / not) | Need fields (path, code, retry) |
| Stdlib-style simple API | Mapping to HTTP/gRPC status codes |
| Equality via `Is` is enough | Behavior methods (`Temporary()`) |

## Gotchas

| Gotcha | Detail |
|--------|--------|
| New sentinel per call | Breaks `Is` |
| Exporting too many sentinels | Becomes a rigid public API |
| Large type hierarchies | Over-engineering; keep it small |
| Matching `err == ErrX` after wrap | Use `errors.Is` |

## Trigger Phrase

> “Sentinels for simple stable conditions with `errors.Is`; typed errors when callers need fields via `errors.As` — never depend on the string text.”

## Exercise

Design errors for a file storage API: not found, permission denied, and checksum mismatch (include expected vs actual). Decide sentinel vs type for each and show the caller-side `Is`/`As` handling for an HTTP layer.
