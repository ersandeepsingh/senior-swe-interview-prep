# When to Use Generics

> Use generics when you need **algorithms or containers that are identical across types** while preserving static type safety. Prefer **interfaces** when behavior (method sets) varies by type. Prefer **concrete code** when there’s only one type or when generics obscure the design. This trade-off is a senior-level interview favorite.

## Plain English

| Tool | Best for |
|------|----------|
| **Concrete types** | One domain type; clearest code |
| **Interfaces** | Heterogeneous behavior (`io.Reader`, strategy) |
| **Generics** | Same code shape, different data types (`Map`, `Set`, sort) |
| **`any` + assert** | Rare escape hatch; loses safety |

Don’t genericize first. Write concrete, then abstract when duplication or type-erasure pain appears.

## Interviewer Angle

- Generics vs interface{} pre-1.18?
- Why isn’t everything generic?
- Storing mixed types in one collection — generics or interfaces?
- Performance differences? (usually minor; measure)
- API design: exported generic types’ costs?

## Go Examples

### Good generic: type-safe container / algorithm

```go
func Filter[T any](s []T, keep func(T) bool) []T {
	var out []T
	for _, v := range s {
		if keep(v) {
			out = append(out, v)
		}
	}
	return out
}
```

### Prefer interface: heterogeneous behavior

```go
// Many different implementations; callers care about Read, not T
func Copy(dst io.Writer, src io.Reader) (int64, error) {
	return io.Copy(dst, src)
}
```

### Prefer concrete: single domain

```go
func (s *UserService) Activate(id UserID) error { /* ... */ }
// Making UserService[T] buys nothing
```

### Awkward generic: “generic” over interfaces unnecessarily

```go
// Probably worse than just using Stringer
func PrintAll[T fmt.Stringer](xs []T) { /* ... */ }

// Fine: interface slice already works
func PrintAll(xs []fmt.Stringer) { /* ... */ }
```

## Decision guide

| Choose **generics** when… | Choose **interfaces** when… | Choose **concrete** when… |
|---------------------------|-----------------------------|---------------------------|
| Element type varies, code doesn’t | Methods define the contract | One type forever |
| You need `==` / operators via constraints | Runtime polymorphism of mixed values | Clarity > DRY |
| Building a collection library | Plugin/strategy patterns | Early prototype |

## Gotchas

| Gotcha | Detail |
|--------|--------|
| Genericizing for fashion | Harder APIs, little gain |
| Interface + generic redundancy | Pick one abstraction |
| Recreating Java-style heavy hierarchies | Not idiomatic Go |
| Ignoring std `slices` / `maps` / `cmp` | Don’t reinvent |

## Trigger Phrase

> “Generics for same algorithm across types; interfaces for shared behavior; concrete when there’s no real variation — I won’t genericize until duplication hurts.”

## Exercise

You need a cache used for `User`, `Session`, and `[]byte` blobs. Compare three designs: (1) `Cache[T any]`, (2) `Cache` storing `any`, (3) three concrete caches. Pick one for a production service and defend it on type safety, eviction policy sharing, and code clarity.
