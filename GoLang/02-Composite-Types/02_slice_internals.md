# Slice Internals

> A slice is a small header: **pointer** to an element of a backing array, **length** (usable elements), and **capacity** (elements from that pointer to the end of the backing array). `append` may write in place if `len < cap`, or allocate a larger array, copy, and return a new header.

## Plain English

Draw it:

```
slice header          backing array
┌──────────┐          ┌─────────────────────┐
│ ptr  ────┼─────────▶│ e0 e1 e2 e3 _  _  _ │
│ len = 3  │          └─────────────────────┘
│ cap = 7  │
└──────────┘
```

`s[i]` uses the pointer + i. `append(s, x)`: if capacity allows, write at `s[len]` and return header with `len+1`. If not, allocate (growth factor ~2x for small, then ~1.25x historically — exact policy can change), copy old elements, append, return new header.

`s = append(s, x)` matters: you must keep the returned header. Discarding it loses growth (and can confuse aliasing).

## Interviewer Angle

- What’s in a slice header?
- When does `append` allocate?
- Why must you assign `append`’s result?
- What is `s[low:high:max]` full slice expression?
- `copy` vs `append`?

## Go Examples

```go
s := make([]int, 3, 5) // len=3, cap=5; elements zeroed
fmt.Println(len(s), cap(s)) // 3 5

s = append(s, 10, 20) // fits in cap → same backing
s = append(s, 30)     // exceeds cap → new backing likely

t := s[1:3] // len=2, cap=cap(s)-1 (from new ptr to end)
```

```go
// Full slice expression: control capacity
a := []int{0, 1, 2, 3, 4}
u := a[1:3:3] // len=2, cap=2 — append to u won't overwrite a[3]
```

```go
dst := make([]int, 2)
n := copy(dst, []int{1, 2, 3}) // n=2; copies min(len(dst), len(src))
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Ignoring `append` return | Silent data loss / stale header |
| Assuming growth factor forever | Implementation detail — don’t hardcode |
| `reslice` with large cap | Later append can overwrite unrelated elements |

## Trigger Phrase

> “A slice is ptr+len+cap over a backing array. `append` reuses capacity or reallocates; I always keep the returned header and draw the header when reasoning about bugs.”

## Exercise

Start with `s := make([]int, 0, 2)`. Perform a series of appends, and after each step state whether the backing array address could change. Then show how `s = s[:0]` reuses capacity without allocating.
