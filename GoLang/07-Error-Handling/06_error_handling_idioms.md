# Error Handling Idioms

> Idiomatic Go: **check errors immediately**, **return early**, **wrap with context**, **don’t ignore**, and **handle at the right layer** (translate to user-facing responses at the edge). Prefer flat code over nested `if err == nil` pyramids.

## Plain English

Happy path stays left-aligned; errors bounce out early. Each layer adds context useful for logs/debug. The top (HTTP/CLI) maps errors to status codes/messages. Don’t log *and* return the same error at every layer (duplicate noise) — pick a policy.

## Interviewer Angle

- Show early-return style vs nested style.
- Where do you log vs return?
- How do you avoid error-handling boilerplate fatigue?
- `Must*` helpers — when OK?
- Handling in goroutines?

## Go Examples

### Early return (good)

```go
func CopyFile(src, dst string) error {
	in, err := os.Open(src)
	if err != nil {
		return fmt.Errorf("open src: %w", err)
	}
	defer in.Close()

	out, err := os.Create(dst)
	if err != nil {
		return fmt.Errorf("create dst: %w", err)
	}
	defer out.Close()

	if _, err := io.Copy(out, in); err != nil {
		return fmt.Errorf("copy: %w", err)
	}
	if err := out.Close(); err != nil {
		return fmt.Errorf("close dst: %w", err)
	}
	return nil
}
```

### Don’t ignore

```go
// bad
_ = w.Close()

// better
if err := w.Close(); err != nil {
	return err
}

// defer close with named return / careful pattern
defer func() {
	if cerr := f.Close(); err == nil {
		err = cerr
	}
}()
```

### Edge translates

```go
func writeAPI(w http.ResponseWriter, err error) {
	switch {
	case errors.Is(err, ErrNotFound):
		http.Error(w, "not found", 404)
	case errors.As(err, new(*ValidationError)):
		http.Error(w, err.Error(), 400)
	default:
		log.Printf("internal: %+v", err)
		http.Error(w, "internal error", 500)
	}
}
```

### errgroup for concurrent work

```go
g, ctx := errgroup.WithContext(ctx)
g.Go(func() error { return taskA(ctx) })
g.Go(func() error { return taskB(ctx) })
return g.Wait()
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| Logging at every layer | Duplicate storms; log once at edge or with sampling |
| Returning `err` without context | Hard to diagnose in prod |
| Giant switch on strings | Use Is/As |
| `if err != nil { return nil }` | Silent swallow |
| Checking only in tests | Production paths still need handling |

## Trigger Phrase

> “Early return on `err`, wrap with `%w` for context, translate at the edge, and don’t log the same error five times on the way up.”

## Exercise

Refactor this nested code into idiomatic early returns, add wrapping, and show how an HTTP handler maps `ErrUnauthorized` vs unknown errors. Keep a single log for unexpected failures.
