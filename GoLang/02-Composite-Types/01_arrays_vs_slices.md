# Arrays vs Slices

> An **array** has fixed length that is part of its type (`[3]int`). A **slice** is a dynamic view (`[]int`) over an underlying array — length can grow via `append` up to (and beyond, via reallocation) capacity. Arrays are values; slices are descriptors that behave like references to shared backing storage.

## Plain English

Almost all Go code uses slices. Arrays show up when size is truly fixed (crypto digests, small buffers) or as the backing store you rarely name.

Assigning an array copies every element. Assigning a slice copies only the slice header (pointer, len, cap) — both still point at the same backing array until a reallocation happens.

`[3]int` and `[4]int` are different types. `[]int` is one type regardless of length.

## Interviewer Angle

- Is `[3]int` assignable to `[]int`? (not directly — slice it: `a[:]`)
- What gets copied on assignment?
- Why are arrays rare in APIs?
- `len`/`cap` on array vs slice?

## Go Examples

```go
var a [3]int = [3]int{1, 2, 3} // length in the type
b := a                         // full copy
b[0] = 99
fmt.Println(a[0]) // 1 — a unchanged

s := []int{1, 2, 3} // slice literal (backing array allocated for you)
t := s              // header copy — shared backing
t[0] = 99
fmt.Println(s[0]) // 99 — both see the change
```

```go
a := [3]int{1, 2, 3}
s := a[:] // slice over array; len=3, cap=3
s = append(s, 4) // may allocate new backing; a unchanged if reallocated
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Passing large arrays to functions | Copies the whole array — use slice or `*[N]T` |
| Thinking slices are reference types like Java lists | The *header* is passed by value; backing is shared |
| Using arrays in JSON/APIs casually | Length becomes part of the contract |

## Trigger Phrase

> “Arrays are fixed-size values; slices are headers over a backing array. I almost always use slices, and I remember assignment copies the header, not the elements.”

## Exercise

Write two functions — `sumArray(a [3]int)` and `sumSlice(s []int)` — mutate an element inside each, and explain what the caller observes after the call.
