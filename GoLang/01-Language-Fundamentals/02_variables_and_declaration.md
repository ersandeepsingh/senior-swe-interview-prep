# Variables & Declaration

> Declare with `var` (explicit type or inferred) or `:=` (short declaration). Uninitialized variables get their type’s **zero value**. `const` holds compile-time constants; `iota` generates related constants in a `const` block.

## Plain English

Go never leaves you with “undefined.” If you declare `var n int`, `n` is `0`. Same idea for `""`, `false`, `nil` for pointers/slices/maps/chans/interfaces/funcs.

Prefer `:=` inside functions for brevity. Use `var` at package scope (no `:=` there) or when you want the zero value without an explicit assignment. Constants are immutable and must be known at compile time (numbers, strings, bools — not general runtime values).

## Interviewer Angle

- Difference between `var x int` and `x := 0`?
- What is a zero value and why does Go have them?
- Can `:=` redeclare a variable? (yes, in multi-assignment, if at least one name is new — in the same block)
- `const` vs `var` — can a const be a slice? (no)
- When is `iota` useful?

## Go Examples

```go
package main

import "fmt"

var GlobalCounter int // package-level; zero = 0

const MaxRetries = 3

func main() {
	var a int          // 0
	var b string       // ""
	var c *int         // nil
	d := 42            // short declare; type inferred as int
	e, f := "hi", true // multi declare

	// Redeclare with := : at least one new variable on the left
	e, g := "bye", 1.5 // e is reassigned; g is new

	fmt.Println(a, b, c, d, e, f, g, GlobalCounter, MaxRetries)
}
```

```go
const (
	StatusPending = iota // 0
	StatusActive         // 1
	StatusClosed         // 2
)
```

## Bad vs Good

```go
// Bad: unnecessary zero then overwrite noise
var users []User
users = []User{}

// Good: either leave zero (nil slice) or make intentionally
users := make([]User, 0, 8) // empty but non-nil, with capacity
```

```go
// Bad: shadowing outer err accidentally in a nested scope
err := doA()
if err != nil { /* ... */ }
if err := doB(); err != nil { // new err shadows — outer err unchanged
	return err
}
// outer err still from doA
```

## Trigger Phrase

> “Uninitialized variables are zeroed, not undefined. I use `:=` for locals, `var` when I want the zero value or package scope, and `const`/`iota` for related compile-time values.”

## Exercise

Write a function that declares: a package-level config string (exported), a local map with zero value, and a const block of three log levels with `iota`. Explain what happens if you write to the zero map vs after `make`.
