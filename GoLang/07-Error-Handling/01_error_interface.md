# error Interface

> In Go, **`error`** is a built-in interface: `type error interface { Error() string }`. Errors are ordinary values — usually returned as the last result — and callers check them explicitly. There is no exception-driven control flow for expected failures.

## Plain English

Anything with an `Error() string` method is an error. The zero value of an `error` variable is `nil`, meaning success. You write `if err != nil` constantly; that’s intentional — failures are visible in the control flow.

## Interviewer Angle

- Is `error` special to the compiler? (built-in interface; special only by convention)
- Why last return value?
- `nil` error vs empty string error?
- Why not exceptions?
- Interface nil trap with typed nil errors? (critical — see gotchas)

## Go Examples

```go
package main

import (
	"fmt"
	"os"
)

func readConfig(path string) ([]byte, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err // propagate
	}
	return data, nil
}

func main() {
	_, err := readConfig("missing.json")
	if err != nil {
		fmt.Println("failed:", err.Error()) // or fmt.Println(err)
		return
	}
}
```

```go
// Any type with Error() string satisfies error.
type MyError struct{ msg string }

func (e MyError) Error() string { return e.msg }

var _ error = MyError{} // compile-time check
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| Typed nil stored in `error` | `var p *MyError; return p` → `err != nil` is **true** |
| Comparing errors with `==` casually | Prefer `errors.Is` for wrapped/sentinel |
| Using errors for normal branching excessively | Still OK when failure is expected (e.g. `io.EOF`) |
| Ignoring `err` with `_` | Bug factory — linters catch some |

```go
func bad() error {
	var e *MyError = nil
	return e // returns non-nil error interface holding (*MyError, nil)
}
```

## Trigger Phrase

> “`error` is just an interface with `Error() string` — failures are values I return and check, and I’m careful never to return a typed nil pointer as an error.”

## Exercise

Show two functions that both “return nil,” one correctly (`return nil`) and one incorrectly (`var err *MyErr; return err`). Write a caller that demonstrates `err != nil` differs, and fix the buggy function.
