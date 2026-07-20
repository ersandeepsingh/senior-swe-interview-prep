# Type Inference

> **Type inference** lets the compiler deduce type arguments from ordinary arguments (and sometimes return context), so you can write `Map(nums, f)` instead of `Map[int, string](nums, f)`. Inference has limits — ambiguous or insufficient information requires explicit type args.

## Plain English

If Go can see from the values you passed what `T` must be, you don’t spell it. When a type parameter only appears in the result, or relationships are too complex, you instantiate explicitly.

## Interviewer Angle

- When does inference succeed/fail?
- Partial instantiation?
- Inference from untyped constants?
- Explicit args still allowed always?

## Go Examples

```go
func Map[T, U any](in []T, f func(T) U) []U { /* ... */ }

nums := []int{1, 2, 3}
// inferred T=int, U=string
strs := Map(nums, func(n int) string { return strconv.Itoa(n) })
```

```go
func Zero[T any]() T {
	var t T
	return t
}

// Cannot infer — T only appears in result
// _ = Zero()
_ = Zero[int]() // explicit
```

```go
func Compact[S ~[]E, E comparable](s S) S { /* like slices.Compact */ }

var xs []string
xs = Compact(xs) // infers S and E
```

```go
// Untyped constant inference
func Max[T ~int | ~float64](a, b T) T {
	if a > b {
		return a
	}
	return b
}

_ = Max(1, 2)     // T becomes int
_ = Max(1.5, 2.0) // float64
// Max(1, 2.0) — may need explicit types depending on version/rules
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| Expecting inference from return only | Often fails — pass explicit `[T]` |
| Complex mutual constraints | Compiler may reject; simplify signature |
| Interface argument → concrete `T` | May infer the interface type, not the dynamic type |
| Readability | Explicit types can clarify APIs in public code |

## Trigger Phrase

> “Inference fills type args from parameters when possible — if `T` only appears in results or the call is ambiguous, I instantiate explicitly.”

## Exercise

Given:

```go
func Pair[T any](a, b T) (T, T) { return a, b }
```

Which calls compile? Fix the failures with explicit type args or signature changes:

```go
Pair(1, 2)
Pair(1, 2.0)
Pair[int](1, 2)
Pair("a", "b")
```
