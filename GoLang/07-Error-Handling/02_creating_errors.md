# Creating Errors

> Create errors with **`errors.New("...")`**, **`fmt.Errorf("...%v...", ...)`**, or custom types. Prefer stable messages for humans/logs; use wrapping (`%w`) when the caller may need to inspect the cause (see wrapping topic).

## Plain English

`errors.New` builds a simple error with a static string. `fmt.Errorf` formats a message (and can wrap). Don’t use panics to signal ordinary failure — return an error.

## Interviewer Angle

- `errors.New` vs `fmt.Errorf`?
- Should error strings be capitalized / punctuated? (idiom: lowercase, no trailing punctuation — so they compose)
- Allocating errors in hot paths?
- Sentinel package-level vars?

## Go Examples

```go
import (
	"errors"
	"fmt"
)

var ErrNotFound = errors.New("not found")

func find(id string) error {
	if id == "" {
		return errors.New("id must not be empty")
	}
	return fmt.Errorf("user %s: %w", id, ErrNotFound)
}
```

```go
// Opaque formatting without wrapping (caller can't unwrap cause)
return fmt.Errorf("decode config: %v", err)

// Wrapping (caller can errors.Is / As)
return fmt.Errorf("decode config: %w", err)
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| Capitalized error strings | Break composition: `"File not found"` vs `"open: file not found"` |
| Dynamic `errors.New` each time for sentinel compare | New pointer each call → `==` fails; use package var |
| Including secrets in errors | Logs may leak PII/tokens |
| `%v` when you meant `%w` | Loses unwrap chain |

## Trigger Phrase

> “I create errors with `errors.New` or `fmt.Errorf`, keep messages lowercase for composition, and use `%w` when callers need to inspect the cause.”

## Exercise

Write `ParsePort(s string) (int, error)` that returns clear errors for empty input, non-integers, and out-of-range ports (1–65535). Use a package-level sentinel for out-of-range and wrap it with the bad value in the message.
