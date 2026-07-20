# Type Conversion vs Casting

> Go has **no implicit numeric promotion** and no C-style casting. You convert explicitly with `T(v)`. The conversion must be legal for the types involved; unsafe reinterpretation of bits belongs to `unsafe`, not everyday casts.

## Plain English

In C/Java you often get silent widening (`int` + `float`). In Go, `int` and `int64` are different types — you write `int64(n)`. That verbosity is intentional: conversions can truncate or change meaning, so they should be visible.

Conversion creates a new value of the target type (when defined). It does **not** mean “treat these bits as another type” except for a few related cases (e.g. `string` ↔ `[]byte` copies). Pointer type punning needs `unsafe.Pointer`.

## Interviewer Angle

- Why no implicit conversion? (safety, clarity)
- What happens converting `float64` → `int`? (truncates toward zero)
- Can you convert between named types with the same underlying type? (yes: `type Celsius float64`; `Celsius(f)`)
- `string(65)` vs `string([]byte{65})`?
- Difference between conversion and type assertion? (assertion is for interfaces)

## Go Examples

```go
var i int = 42
var f float64 = float64(i) // explicit
var u uint = uint(i)

// Truncation
f = 3.9
i = int(f) // 3 — toward zero, not rounding

// Named types share underlying type → convertible
type UserID int64
var id UserID = UserID(99)
var raw int64 = int64(id)
```

```go
// string conversions
s := string([]byte{'G', 'o'}) // "Go" — copies bytes as UTF-8
s2 := string(rune(0x4E16))    // "世"
// string(65) is "A" because 65 is convertible via rune rules — prefer clarity:
s3 := string(rune(65))
```

## Bad vs Good

```go
// Bad: silent overflow risk ignored
var big int64 = 3_000_000_000
var n int32 = int32(big) // wraps on overflow — legal but dangerous

// Good: check bounds before converting, or stay in int64
if big > math.MaxInt32 || big < math.MinInt32 {
	return fmt.Errorf("out of range: %d", big)
}
n = int32(big)
```

```go
// Bad: confusing conversion with assertion
var x any = "hello"
// s := string(x) // compile error
s := x.(string)  // type assertion — correct for interfaces
```

## Trigger Phrase

> “Go never promotes types for me — every conversion is explicit `T(v)`, and I treat truncation/overflow as my responsibility. Assertions are for interfaces; conversions are for compatible concrete types.”

## Exercise

Explain what each line does (compile error, runtime panic, or value):

```go
var a int = 7
var b int64 = a
var c int64 = int64(a)
var d any = a
var e int = d.(int)
var f string = string([]byte{65, 66})
```
