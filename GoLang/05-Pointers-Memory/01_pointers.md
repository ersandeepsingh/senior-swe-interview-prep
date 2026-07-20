# Pointers

> A pointer holds the **address** of a value: type `*T`. `&v` takes an address; `*p` dereferences. Go has **no pointer arithmetic** (that’s `unsafe`/`uintptr` territory). The zero value of a pointer is `nil`.

## Plain English

Pointers let functions mutate the caller’s data and avoid copying large structs. Method receivers and optional values commonly use them.

Dereferencing a nil pointer panics. Prefer returning pointers to structs from constructors (`NewX() *X`) when the type is mutable or large; prefer values for small immutable data.

Unlike C, you can’t do `p++` to walk memory. Slices replace most “pointer + offset” patterns.

## Interviewer Angle

- Why no pointer arithmetic?
- `&` on map elements / function returns — addressability?
- Nil pointer vs empty struct pointer?
- When prefer value over pointer?

## Go Examples

```go
x := 10
p := &x
*p = 20
fmt.Println(x) // 20

var q *int
// *q = 1 // panic
q = new(int)
*q = 1
```

```go
type User struct{ Name string }

func bump(u *User) {
	u.Name = strings.ToUpper(u.Name)
}

u := User{Name: "ada"}
bump(&u)
```

```go
// Sugar: Go auto-dereferences struct fields
func (u *User) Set(name string) { u.Name = name } // not (*u).Name
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Returning `&local` — actually OK in Go | Escapes to heap — see escape analysis |
| Taking address of range loop var (old) | Shared storage bugs |
| Unnecessary pointers everywhere | GC pressure, nil checks |

## Trigger Phrase

> “Pointers are addresses with no arithmetic — I use them to share and mutate, check for nil before dereference, and let slices cover contiguous memory patterns.”

## Exercise

Write `func Swap(a, b *int)` and explain why `func Swap(a, b int)` cannot swap the caller’s variables.
