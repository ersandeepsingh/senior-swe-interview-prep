# Pass by Value

> **Everything in Go is passed by value** — arguments are copied into the callee. For pointers, the pointer bits are copied (both point to the same data). For slices, maps, and channels, the **header** is copied, so the callee shares the underlying structure (for slices: backing array; for maps/chans: the same runtime object).

## Plain English

`func f(u User)` gets a full struct copy. `func f(u *User)` gets a copy of the pointer — mutating `*u` affects the caller.

Slices: `func f(s []int)` can change `s[i]` and the caller sees it; reassigning `s = append(s, ...)` updates only the callee’s header unless you return the new slice or pass `*[]int`.

Maps: mutations (`m[k]=v`) are visible to the caller; `m = make(...)` inside rebinds only the local header.

This is why people say “reference types” colloquially — but the language mechanism is still copy-of-header.

## Interviewer Angle

- Are maps passed by reference? (precise answer: header by value, shared map)
- Why must `append`’s result be assigned?
- How do you let a function grow a slice for the caller?
- Cost of passing large structs?

## Go Examples

```go
func tryReplace(s []int) {
	s[0] = 99          // visible to caller
	s = append(s, 1)   // may reallocate — caller header unchanged
}

func grow(s *[]int) {
	*s = append(*s, 1) // updates caller’s header
}

func growRet(s []int) []int {
	return append(s, 1)
}
```

```go
func clearMap(m map[string]int) {
	for k := range m {
		delete(m, k) // visible
	}
	m = nil // caller’s map variable unchanged
}
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Expecting `append` inside func to update caller | Need return or `*[]T` |
| Passing huge structs by value in hot paths | Copies — use pointer |
| Confusing “reference type” with Java references | Headers are still values |

## Trigger Phrase

> “Everything is passed by value — including slice/map headers. Shared backing explains mutation visibility; header rebinding explains why `append` must be returned.”

## Exercise

Write three versions of a function that appends an element for the caller: (1) wrong in-place header, (2) return new slice, (3) `*[]int`. Show caller code for each.
