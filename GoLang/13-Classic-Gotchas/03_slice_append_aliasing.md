# Slice `append` Aliasing

> Slices share a **backing array**. `append` may reuse capacity and **overwrite** elements still visible through another slice.

## Plain English

A slice is `(ptr, len, cap)`. Slicing `a[1:3]` shares storage with `a`. If you `append` to a slice that still has capacity, new elements write into the same array — surprising mutations of “copies” that weren’t copies.

## Why interviewers ask 🔴⭐

Core memory model for slices. Shows up in coding + internals rounds.

## Broken

```go
func broken() {
    a := []int{1, 2, 3, 4}
    b := a[:2]          // len=2 cap=4 — shares array with a
    b = append(b, 99)   // writes into index 2 of same array!
    fmt.Println(a)      // [1 2 99 4] — a changed!
    fmt.Println(b)      // [1 2 99]
}
```

## Fixed

```go
func fixed() {
    a := []int{1, 2, 3, 4}
    b := a[:2:2] // full slice expression: len=2 cap=2 — force append to allocate
    b = append(b, 99)
    fmt.Println(a) // [1 2 3 4]
    fmt.Println(b) // [1 2 99]
}

// Or explicit copy:
func fixedCopy(a []int) []int {
    b := make([]int, len(a))
    copy(b, a)
    return b
}
```

## Pitfalls

- Returning a subslice of an internal buffer — caller append can corrupt your cache; copy or full-slice.
- `append(s[:0], …)` reuse patterns are powerful but easy to race if shared across goroutines.
- Assuming `append` always allocates — it only does when `len+n > cap`.

## Interview trigger phrase

> “I’d remember append reuses capacity; to detach, I’d use a full slice `s[i:j:j]` or `copy` into a new backing array.”

## Exercise

Explain what prints:

```go
s := []int{0, 1, 2, 3}
t := append(s[:2], 8, 9)
fmt.Println(s, t)
```

Then fix it so `s` stays `{0,1,2,3}`.
