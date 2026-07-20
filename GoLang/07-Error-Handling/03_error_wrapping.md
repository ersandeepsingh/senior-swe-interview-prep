# Error Wrapping

> **Wrapping** attaches context while preserving the underlying error: `fmt.Errorf("...: %w", err)`. Inspect chains with **`errors.Is`** (sentinel match along the chain), **`errors.As`** (find first matching type), and **`errors.Unwrap`**. Go 1.13+ wrapping is the standard interview answer.

## Plain English

As an error bubbles up, each layer adds “what was I doing?” without erasing “what originally went wrong?” Callers at the top can still ask “was this a `NotFound`?” via `errors.Is`, even if the message is `serve request: load user: not found`.

## Interviewer Angle

- `%w` vs `%v`?
- `Is` vs `As`?
- Multiple wraps / trees? (`errors.Join` in Go 1.20+)
- Should you wrap at every layer?
- Breaking changes when switching from `%v` to `%w`?

## Go Examples

```go
func loadUser(id string) (*User, error) {
	u, err := db.Get(id)
	if err != nil {
		return nil, fmt.Errorf("load user %s: %w", id, err)
	}
	return u, nil
}

func handle(id string) error {
	_, err := loadUser(id)
	if errors.Is(err, sql.ErrNoRows) {
		return ErrNotFound
	}
	if err != nil {
		return fmt.Errorf("handle: %w", err)
	}
	return nil
}
```

```go
var pathErr *os.PathError
if errors.As(err, &pathErr) {
	fmt.Println("path:", pathErr.Path)
}
```

```go
// Join multiple errors (Go 1.20+)
return errors.Join(err1, err2)

// Is/As walk Join trees as well
```

```go
// Custom types can implement Is / Unwrap
func (e *MyError) Unwrap() error { return e.err }
func (e *MyError) Is(target error) bool {
	return target == ErrNotFound || e.err == target
}
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| String matching `err.Error()` | Brittle; use Is/As |
| Wrapping with `%v` then expecting Is | Won’t find cause |
| Double-wrapping into useless noise | Add context that aids ops/debug |
| Comparing with `==` on wrapped errors | Fails; use `errors.Is` |
| Losing type by returning `errors.New(err.Error())` | Destroys chain |

## Trigger Phrase

> “I wrap with `%w` for context and use `errors.Is`/`As` to inspect causes — never string-match `Error()`.”

## Exercise

Given three layers (`handler` → `service` → `repo`), implement wrapping so the handler can detect `ErrNotFound` from the repo through two wraps, and extract a custom `*ValidationError` via `errors.As` when present.
