# nil Interface vs nil Pointer

> A **nil interface** has neither type nor value. A **nil pointer** (or nil slice/map/chan/func) stored *inside* an interface makes the interface **non-nil**, because the type word is set. This is the classic “why isn’t my `error` nil?” bug.

## Plain English

```go
var err error          // nil interface
var p *MyError = nil
err = p                // interface holds (*MyError, nil)
if err != nil { ... }  // TRUE — surprise
```

Always return an untyped nil interface for “no error”: `return nil`, not `return p` when `p` might be nil. Or return `error(nil)` explicitly. Helpers should have return type `error` and do `return nil`.

Same trap for any interface: `io.Reader`, custom interfaces, etc.

## Interviewer Angle

- Walk through (type, value) for the trap
- How do you return a nil error safely from a function that uses `*MyError`?
- How do you detect typed nil if you must? (assertion / reflect)
- Why is this so common with `error`?

## Go Examples

```go
type MyError struct{ Msg string }

func (e *MyError) Error() string { return e.Msg }

func boom(fail bool) error {
	var p *MyError
	if fail {
		p = &MyError{Msg: "fail"}
	}
	return p // BAD when fail==false — returns non-nil error
}

func boomFixed(fail bool) error {
	if fail {
		return &MyError{Msg: "fail"}
	}
	return nil // good — true nil interface
}
```

```go
// Detecting typed nil (rare — usually redesign)
func isNilErr(err error) bool {
	if err == nil {
		return true
	}
	v := reflect.ValueOf(err)
	return v.Kind() == reflect.Ptr && v.IsNil()
}
```

## Bad vs Good

```go
// Bad
func f() error {
	var err *MyError
	return err
}

// Good
func f() error {
	return nil
}
```

## Trigger Phrase

> “A nil concrete pointer in an interface is not a nil interface — the type word is set. I always `return nil` for success, never a nil typed pointer as `error`.”

## Exercise

Predict the output, then fix `Load` so success yields a true nil `error`:

```go
func Load(ok bool) error {
	var err *os.PathError
	if !ok {
		err = &os.PathError{Op: "load", Err: errors.New("nope")}
	}
	return err
}
func main() {
	err := Load(true)
	fmt.Println(err == nil)
}
```
