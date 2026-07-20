# Multiple Return Values

> Go functions can return several values. The idiomatic pattern is `(result, error)` — the caller **must** handle `error` explicitly; there is no exception-based control flow for ordinary failures.

## Plain English

Returning `(T, error)` keeps failure visible in the type signature. By convention, if `err != nil`, other results are unreliable (often zero values) unless documented otherwise (e.g. partial writes: `n, err := w.Write(b)`).

You can return more than two values (`value, ok, err`) but keep it rare — prefer a small result struct if arity grows.

Blank identifier `_` discards a return you intentionally ignore — never ignore `error` without a reason.

## Interviewer Angle

- Why `(T, error)` instead of exceptions?
- Is it safe to use the value when `err != nil`?
- `panic` vs error return — when each?
- Named vs unnamed multi-returns?

## Go Examples

```go
func ParsePort(s string) (int, error) {
	n, err := strconv.Atoi(s)
	if err != nil {
		return 0, fmt.Errorf("parse port: %w", err)
	}
	if n < 1 || n > 65535 {
		return 0, fmt.Errorf("port out of range: %d", n)
	}
	return n, nil
}

port, err := ParsePort(input)
if err != nil {
	return err
}
// use port
```

```go
// comma-ok is also multi-return
v, ok := m[k]
ch, ok := x.(chan int)
```

## Bad vs Good

```go
// Bad
data, _ := os.ReadFile(path) // silent failure

// Good
data, err := os.ReadFile(path)
if err != nil {
	return fmt.Errorf("read config: %w", err)
}
```

## Trigger Phrase

> “Errors are values — I return `(T, error)`, check `err` before using `T`, and wrap with context instead of ignoring failures.”

## Exercise

Write `func Div(a, b int) (int, error)` and a caller that distinguishes divide-by-zero from other errors using a sentinel or custom type.
