# Empty Interface / `any`

> `interface{}` (alias **`any`** since Go 1.18) has zero methods, so every type satisfies it. It holds any value but erases static type information — you need assertions, reflection, or generics to recover type safety.

## Plain English

Use `any` for truly heterogeneous containers (`map[string]any` for JSON objects), printf-style APIs, or before generics existed. Prefer generics or concrete types when you know the shape.

`any` is not Java’s `Object` with a shared hierarchy — it’s just “no method constraints.” There’s no auto boxing of primitives beyond storing them as dynamic values.

## Interviewer Angle

- `any` vs generics — when each?
- Why avoid `any` in public APIs?
- JSON and `map[string]any` trade-offs?
- Performance of boxing?

## Go Examples

```go
var v any
v = 7
v = "hi"
v = []int{1, 2}

switch x := v.(type) {
case int:
	fmt.Println("int", x)
case string:
	fmt.Println("string", x)
}
```

```go
// Prefer generics when possible
func Head[T any](s []T) (T, bool) {
	var zero T
	if len(s) == 0 {
		return zero, false
	}
	return s[0], true
}
```

## Bad vs Good

```go
// Bad: any everywhere
func Process(data any) any { /* assertions hell */ }

// Good: concrete or generic
func Process(data User) (Result, error)
func ProcessSlice[T any](data []T) error
```

## Trigger Phrase

> “`any` means no methods — it holds everything but throws away type safety. I use it for heterogeneous data; otherwise I prefer concrete types or generics.”

## Exercise

Replace an API `func Max(vals []any) any` that only handles `int` with a generic `func Max[T cmp.Ordered](vals []T) (T, error)`.
