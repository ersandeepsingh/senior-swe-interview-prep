# `iota` Patterns

> `iota` is a const-block counter that starts at `0` and increments by one per const spec. Reset to `0` in each new `const (` block. Use it for enums, bit flags, and derived expressions.

## Plain English

Inside a parenthesized `const` group, `iota` is 0 for the first line, 1 for the second, and so on. You can write expressions with `iota` (`1 << iota`) and blank identifiers to skip values (`_`). If you omit the expression on later lines, they reuse the previous expression (with the new `iota`).

This is Go’s idiomatic “enum” — not a separate language feature. Typed constants (`type Status int`) give you a distinct type for APIs.

## Interviewer Angle

- Where does `iota` reset?
- How do bit-flag enums work with `iota`?
- How do you skip a value?
- Can `iota` appear outside `const`? (no — it’s only special in const declarations)
- Typed vs untyped constant enums — method sets?

## Go Examples

```go
type Status int

const (
	StatusUnknown Status = iota // 0
	StatusActive                // 1
	StatusDisabled              // 2
)
```

```go
// Bit flags
const (
	Read Permission = 1 << iota // 1 (1<<0)
	Write                       // 2 (1<<1)
	Execute                     // 4 (1<<2)
)

func (p Permission) Has(flag Permission) bool {
	return p&flag != 0
}
```

```go
// Skip and custom expressions
const (
	_ = iota // skip 0
	KB = 1 << (10 * iota) // iota=1 → 1<<10
	MB                    // iota=2 → 1<<20
	GB                    // iota=3 → 1<<30
)
```

```go
// Mid-block reset pattern: start a new const block instead of fighting iota
const (
	A = iota // 0
	B        // 1
)
const (
	C = iota // 0 again
	D        // 1
)
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Assuming `iota` continues across blocks | Each `const (` resets |
| Forgetting type on first line only | Later lines still get the type via repetition rules — but be explicit for clarity |
| Using iota for non-sequential wire protocols | Prefer explicit values when the number is part of an external API |
| No built-in String() | Add `String()` or `go:generate stringer` yourself |

## Trigger Phrase

> “`iota` is a const-block counter — I use it for typed enums and `1 << iota` flags, skip with `_`, and reset by starting a new const group.”

## Exercise

Define a typed `Day` enum Mon–Sun starting at 1 (not 0), plus a `Weekend` bitset using `Saturday | Sunday` style flags. Write a `IsWeekend(d Day) bool` helper.
