# Comparing Structs, Slices & Maps

> Only **comparable** types work with `==`. Structs are comparable if all fields are; **slices, maps, and functions are not** (except comparing to `nil`).

## Plain English

`==` is for types the language defines as comparable. Slices/maps need `bytes.Equal`, loops, `slices.Equal`, `maps.Equal`, or `reflect.DeepEqual` (slower, careful with nil vs empty).

## Why interviewers ask 🟡

Compile errors and nil/empty distinctions show language fluency.

## Broken

```go
func broken() {
    a := []int{1, 2}
    b := []int{1, 2}
    // if a == b { } // INVALID: slice can only be compared to nil

    m1 := map[string]int{"x": 1}
    m2 := map[string]int{"x": 1}
    // if m1 == m2 { } // INVALID

    type T struct{ S []int }
    // var x, y T; _ = x == y // INVALID — field S not comparable
}
```

## Fixed

```go
func fixed() {
    a, b := []int{1, 2}, []int{1, 2}
    fmt.Println(slices.Equal(a, b)) // true

    m1, m2 := map[string]int{"x": 1}, map[string]int{"x": 1}
    fmt.Println(maps.Equal(m1, m2)) // true

    type Point struct{ X, Y int } // comparable
    fmt.Println(Point{1, 2} == Point{1, 2})

    // Nil vs empty
    var s1 []int
    s2 := []int{}
    fmt.Println(s1 == nil, s2 == nil)     // true, false
    fmt.Println(slices.Equal(s1, s2))     // true — both length 0
    fmt.Println(reflect.DeepEqual(s1, s2)) // false! DeepEqual treats nil≠empty slice
}
```

## Rules of thumb

| Type | `==` |
|------|------|
| Basic types, pointers, channels, interfaces* | yes (*dynamic type comparable) |
| Structs | yes iff all fields comparable |
| Arrays | yes iff element type comparable |
| Slices / maps / funcs | only vs `nil` |

\*Interface equality: comparable dynamic types + equal values; panics if dynamic type is incomparable (e.g. slice inside).

## Pitfalls

- Using `reflect.DeepEqual` in hot paths.
- Surprises with `DeepEqual` nil vs empty slice/map.
- Floating point `==` and NaN.
- Comparing interfaces that hold slices → panic.

## Interview trigger phrase

> “I’d use `==` only for comparable types; for slices/maps I’d use `slices.Equal`/`maps.Equal`, and I’d call out nil vs empty with `DeepEqual`.”

## Exercise

Which of these compile? For those that don’t, write the idiomatic comparison.

```go
[3]int{1,2,3} == [3]int{1,2,3}
[]int{1} == []int{1}
map[int]int{} == nil
struct{ A int; B []byte }{} == struct{ A int; B []byte }{}
```
