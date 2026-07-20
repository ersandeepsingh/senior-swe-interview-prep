# Type Parameters

> **Type parameters** let functions and types be parameterized by types: `func F[T any](x T) T`, `type Stack[T any] struct{ ... }`. Instantiation supplies concrete types (`F[int]`, `Stack[string]`) — sometimes inferred. Available since Go 1.18.

## Plain English

Instead of writing `MinInt`, `MinFloat64`, or using `interface{}` and casting, you write one `Min[T]` that works for many types while staying type-safe at compile time. Generic types are like templates for structs/slices you’ll reuse with different element types.

## Interviewer Angle

- Syntax for functions vs types?
- Multiple type params? (`[K comparable, V any]`)
- Methods: can methods introduce new type params? (**no** — only on the receiver type)
- Generics vs `any` + type assert?
- Compilation model? (dictionary/shape stenciling — high level only)

## Go Examples

```go
// Generic function
func Identity[T any](v T) T { return v }

func main() {
	fmt.Println(Identity[int](42))
	fmt.Println(Identity("hi")) // inferred
}
```

```go
// Generic type
type Pair[A, B any] struct {
	First  A
	Second B
}

func NewPair[A, B any](a A, b B) Pair[A, B] {
	return Pair[A, B]{a, b}
}
```

```go
// Methods may use the type's parameters — not new ones
func (p Pair[A, B]) Swap() Pair[B, A] {
	return Pair[B, A]{p.Second, p.First}
}

// Illegal:
// func (p Pair[A, B]) Convert[C any](f func(A) C) ...
```

```go
// Generic slice helper
func Map[T, U any](in []T, f func(T) U) []U {
	out := make([]U, len(in))
	for i, v := range in {
		out[i] = f(v)
	}
	return out
}
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| Methods with their own type params | Not allowed in Go |
| Over-generic APIs | Harder to read; prefer concrete when one type dominates |
| Expecting specialization control | Compiler decides; don’t micro-optimize prematurely |
| Mixing with reflection | Usually pick one style |
| `T` only used once | May be unnecessary abstraction |

## Trigger Phrase

> “Type parameters give compile-time type-safe reuse — on functions and types — but methods can’t add new type params beyond the receiver.”

## Exercise

Write `func Keys[K comparable, V any](m map[K]V) []K` and `func Values[K comparable, V any](m map[K]V) []V`. Instantate with `map[string]int` without explicitly passing type args if possible.
