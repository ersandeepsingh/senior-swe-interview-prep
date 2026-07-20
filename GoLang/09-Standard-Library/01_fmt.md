# `fmt` — Formatting & Printing

> Format values into strings (or stdout) with **verbs**; implement `fmt.Stringer` for custom display.

## Plain English

`fmt` is how Go turns values into text: `Printf`/`Sprintf` for formatting, `Print`/`Println` for simple output, `Scan` family for reading. Verbs like `%v`, `%+v`, `%#v`, `%T`, `%w` (errors) are interview-frequent.

## Why interviewers ask

They want to know you can debug structs (`%+v`), distinguish string vs Go-syntax (`%s` vs `%q` vs `%#v`), and know that `String()` is called by `%v` for types that implement `Stringer`.

## Core verbs

| Verb | Meaning |
|------|---------|
| `%v` | default format |
| `%+v` | struct with field names |
| `%#v` | Go-syntax representation |
| `%T` | type of value |
| `%s` / `%q` | string / quoted string |
| `%d` / `%x` / `%f` | int / hex / float |
| `%p` | pointer address |
| `%w` | wrap error (`fmt.Errorf`) |

## Examples

```go
package main

import "fmt"

type User struct {
    Name string
    Age  int
}

func (u User) String() string {
    return fmt.Sprintf("%s (%d)", u.Name, u.Age)
}

func main() {
    u := User{Name: "Ada", Age: 36}
    fmt.Printf("%v\n", u)   // Ada (36) — uses Stringer
    fmt.Printf("%+v\n", u)  // {Name:Ada Age:36} — still uses Stringer for %v family on Stringer types in some cases;
                            // for raw fields use %#v or don't implement Stringer when debugging
    fmt.Printf("%#v\n", u)  // main.User{Name:"Ada", Age:36}
    fmt.Printf("%T\n", u)   // main.User

    err := fmt.Errorf("open %s: %w", "cfg.yaml", fmt.Errorf("permission denied"))
    fmt.Println(err)
}
```

**Note:** If a type has `String()`, `%v` and `%s` use it. Use `%#v` when you need the raw struct dump during debugging.

## `Sprintf` vs `Printf`

```go
msg := fmt.Sprintf("user=%s id=%d", "ada", 42) // returns string
fmt.Printf("user=%s id=%d\n", "ada", 42)       // writes to stdout
```

## Pitfalls

- Forgetting `\n` on `Printf` (or using `Println` when you meant formatted output).
- Passing the wrong number of args → `%!(EXTRA ...)` / `%!d(MISSING)` in the output (runtime, not compile error).
- Using `+` string concat in hot loops instead of `strings.Builder` / `fmt.Appendf` (Go 1.19+).
- Wrapping errors with `%v` instead of `%w` — loses `errors.Is` / `As` chain.

## Interview trigger phrase

> “I’d use `%+v` or `%#v` to dump state, implement `Stringer` for human-readable logs, and always wrap with `%w` when building error chains.”

## Exercise

Given `type Money struct { Cents int64; Currency string }`, implement `String()` so it prints like `USD 12.34`, then show `Printf` lines for `%v`, `%#v`, and `%T`.
