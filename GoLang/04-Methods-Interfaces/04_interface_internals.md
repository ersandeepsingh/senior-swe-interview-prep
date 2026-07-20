# Interface Internals

> An interface value is a pair: **(dynamic type, dynamic value)** — often described as a type descriptor plus a pointer/data word. Method calls dispatch through the type’s itable. Two interface values compare equal if both are nil, or both have equal dynamic type and equal dynamic value.

## Plain English

When you assign a concrete value to an interface, Go stores what it is and the data (copying small values or pointing as needed). Calling a method looks up the concrete implementation and invokes it — dynamic dispatch.

This model explains the famous trap: an interface can hold a typed nil pointer. The interface’s type word is non-nil, so the interface value itself is **not** nil — even though the pointer inside is nil.

`reflect.TypeOf` / `fmt.Printf("%T")` show the dynamic type.

## Interviewer Angle

- What’s stored in an interface?
- Why is typed-nil ≠ nil interface?
- Cost of interface call vs direct call?
- Interface equality rules?

## Go Examples

```go
var r io.Reader
fmt.Println(r == nil) // true — type and value both unset

f, _ := os.Open("/etc/hosts")
r = f                 // (type=*os.File, value=pointer)
fmt.Printf("%T\n", r) // *os.File
r.Read(make([]byte, 8))
```

```go
var p *os.File = nil
var r io.Reader = p
fmt.Println(p == nil) // true
fmt.Println(r == nil) // false — interface has type *os.File
```

```go
// Equality
type ID int
var a any = ID(1)
var b any = ID(1)
var c any = 1
fmt.Println(a == b) // true
fmt.Println(a == c) // false — different dynamic types
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Assuming interface nil check catches typed nil | Classic production bug |
| Boxing large values repeatedly | Copies / allocs — design carefully |
| Comparing interfaces holding incomparable types | Panic if dynamic values aren’t comparable |

## Trigger Phrase

> “An interface is a (type, value) pair; dispatch uses the dynamic type. That’s why a nil concrete pointer inside a non-nil interface fails `== nil` checks.”

## Exercise

Draw the (type, value) contents for:

```go
var err error
err = nil
var p *MyError = nil
err = p
```

Explain what `if err != nil` does in each state.
