# nil Interface ≠ nil

> An interface value is nil only if **both** its type and value are nil. A typed nil pointer stored in an interface is **not** equal to `nil`.

## Plain English

Interfaces are a `(type, value)` pair. `var err error = (*MyError)(nil)` puts a non-nil type with a nil value into `err`. Then `err == nil` is **false**, even though the concrete pointer is nil. This breaks `if err != nil` after functions return typed nils.

## Why interviewers ask 🔴⭐

The classic “why isn’t my error nil?” grill. Tied to interface internals.

## Broken

```go
type MyError struct{ Msg string }

func (e *MyError) Error() string { return e.Msg }

func mightFail(ok bool) error {
    var err *MyError
    if !ok {
        err = &MyError{Msg: "boom"}
    }
    return err // returns typed nil when ok==true — NOT a nil interface!
}

func broken() {
    err := mightFail(true)
    if err != nil {
        // THIS BRANCH RUNS — surprise
        fmt.Println("failed:", err)
    }
}
```

## Fixed

```go
func mightFail(ok bool) error {
    if !ok {
        return &MyError{Msg: "boom"}
    }
    return nil // naked nil → nil interface
}

func fixed() {
    err := mightFail(true)
    if err != nil {
        fmt.Println("failed:", err)
        return
    }
    fmt.Println("ok")
}
```

Inspect:

```go
fmt.Printf("%T %#v\n", err, err)
// *main.MyError (*main.MyError)(nil)  when typed nil was returned
```

## Pitfalls

- Returning `err` from a variable of concrete pointer type after a happy path.
- Wrapping: sometimes people reintroduce typed nils through helpers.
- Same issue with any interface (`io.Reader`, etc.), not just `error`.

## Interview trigger phrase

> “An interface is a type-and-value pair; a typed nil isn’t a nil interface — I’d return a naked `nil` on success.”

## Exercise

Show `fmt.Printf` output for (1) `var e error`, (2) `var p *MyError; e = p`, (3) `e = nil`. Which print `== nil` as true?
