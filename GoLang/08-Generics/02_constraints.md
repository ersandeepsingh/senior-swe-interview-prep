# Constraints

> A **constraint** restricts which types may instantiate a type parameter. The interface constraint form lists allowed types/methods: `any` (no restriction), `comparable` (built-in for `==`), approximation elements `~T`, and unions. The `golang.org/x/exp/constraints` (and later `slices`/`cmp`) packages provide common numeric constraints.

## Plain English

Constraints answer: “what can `T` do?” If you need `T` to support `<`, you can’t use bare `any` — you need an ordered constraint. If you need map keys, you need `comparable`. Constraints are interfaces (with special type-element syntax).

## Interviewer Angle

- What is `comparable`?
- What does `~` mean? (underlying type)
- Interface with methods as constraint?
- Why can’t you use operators on unconstrained `T`?
- `constraints.Ordered` pattern?

## Go Examples

```go
// any — unrestricted (alias of interface{})
func Ptr[T any](v T) *T { return &v }

// comparable — required for map keys / ==
func Contains[T comparable](s []T, v T) bool {
	for _, x := range s {
		if x == v {
			return true
		}
	}
	return false
}
```

```go
// Method-set constraint
type Stringer interface {
	String() string
}

func Join[T Stringer](xs []T, sep string) string {
	parts := make([]string, len(xs))
	for i, x := range xs {
		parts[i] = x.String()
	}
	return strings.Join(parts, sep)
}
```

```go
// Union + approximation
type Number interface {
	~int | ~int64 | ~float64
}

func Sum[T Number](xs []T) T {
	var total T
	for _, x := range xs {
		total += x
	}
	return total
}

// ~int means any type whose underlying type is int
type MyInt int
// Sum([]MyInt{1, 2}) works because of ~
```

```go
// Ordered (illustrative — prefer cmp/slices helpers in modern Go)
type Ordered interface {
	~int | ~int8 | ~int16 | ~int32 | ~int64 |
		~uint | ~uint8 | ~uint16 | ~uint32 | ~uint64 | ~uintptr |
		~float32 | ~float64 | ~string
}

func Min[T Ordered](a, b T) T {
	if a < b {
		return a
	}
	return b
}
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| Using `any` then operators | Compile error — constrain properly |
| Forgetting `~` | Named types like `type MyInt int` won’t match `int` alone |
| `comparable` and interfaces | Interfaces are comparable only in limited ways; structs with slices aren’t |
| Huge constraint unions | Prefer std helpers (`cmp.Ordered`, `slices`) |
| Constraints vs runtime interface | Constraints erased at compile-time instantiation |

## Trigger Phrase

> “Constraints declare what `T` can do — `comparable` for equality, `~` for underlying types, and method sets when behavior matters more than operators.”

## Exercise

Write a generic `Clamp[T /* your constraint */](v, lo, hi T) T`. Explain why `any` fails, implement the constraint, and show it works for both `int` and `type Age int`.
