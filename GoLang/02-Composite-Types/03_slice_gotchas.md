# Slice Gotchas

> Most slice bugs come from **shared backing arrays**: reslicing or appending with spare capacity mutates memory that another slice still sees. Sub-slices are views, not deep copies.

## Plain English

`b := a[1:3]` does not copy elements. If `cap(b) > len(b)`, `append(b, x)` can overwrite `a`’s later elements. If you’ve handed a sub-slice to another package, that package’s `append` can corrupt your data unless you clipped capacity or copied.

Nil vs empty: `var s []int` is nil (`s == nil`); `s := []int{}` or `make([]int, 0)` is empty but non-nil. Both have `len == 0`; JSON marshals them differently (`null` vs `[]`).

## Interviewer Angle

- Classic append-aliasing bug — walk through it
- How do you take a safe sub-slice to return? (`append([]T(nil), s...)` or `slices.Clone`, or full slice expr)
- Nil vs empty slice in JSON / DB drivers?
- Does ranging a nil slice panic? (no)

## Go Examples

### Gotcha: append overwrites sibling slice

```go
a := []int{1, 2, 3, 4}
b := a[:2]          // len=2, cap=4 — shares backing
b = append(b, 99)   // writes into a[2]
fmt.Println(a)      // [1 2 99 4] — surprise
```

### Fix: clip capacity or copy

```go
b := a[:2:2]                    // cap=2; append must allocate
// or
b = append([]int(nil), a[:2]...) // defensive copy
```

### Gotcha: modifying range variable

```go
s := []int{1, 2, 3}
for _, v := range s {
	v = 0 // changes copy only
}
// s still [1 2 3]
for i := range s {
	s[i] = 0 // correct
}
```

## Bad vs Good

```go
// Bad: return internal slice — caller can append into your buffer
func (c *Cache) Keys() []string { return c.keys }

// Good: return a copy (or clip + document immutability)
func (c *Cache) Keys() []string {
	return append([]string(nil), c.keys...)
}
```

## Trigger Phrase

> “Sub-slices share a backing array — if capacity remains, `append` can mutate the original. I clip capacity or copy when sharing slices across boundaries.”

## Exercise

Predict printed values, then fix `takeFirst` so the caller’s append cannot corrupt `src`:

```go
func takeFirst(src []int) []int { return src[:1] }

func main() {
	src := []int{1, 2, 3}
	out := takeFirst(src)
	out = append(out, 9)
	fmt.Println(src, out)
}
```
