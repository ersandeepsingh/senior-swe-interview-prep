# `switch` Power Features

> Go’s `switch` is an expression matcher **and** a cleaner `if/else` chain. Cases can list multiple values, omit the expression (case conditions are bools), and switch on dynamic types with a **type switch**. No automatic fallthrough.

## Plain English

Basic form: `switch x { case 1, 2: ... default: ... }`. Cases are equalities against `x`.

Expression-less form: `switch { case n < 0: ... case n == 0: ... }` — each case is a boolean condition. Prefer this over nested `if/else` ladders.

Type switch: `switch v := x.(type)` lets you branch on the concrete type stored in an interface. Inside each case, `v` has that concrete type.

## Interviewer Angle

- Show a type switch vs type assertion — when each?
- What does `fallthrough` do, and when is it appropriate?
- Can cases be expressions, not just constants? (yes — evaluated top to bottom)
- Expression-less switch vs `if/else` — readability trade-off?

## Go Examples

```go
switch day {
case "sat", "sun":
	fmt.Println("weekend")
case "mon", "tue", "wed", "thu", "fri":
	fmt.Println("weekday")
default:
	fmt.Println("unknown")
}
```

```go
// Expression-less — like if/else chain
switch {
case score >= 90:
	grade = "A"
case score >= 80:
	grade = "B"
default:
	grade = "C"
}
```

```go
// Type switch
func describe(x any) string {
	switch v := x.(type) {
	case nil:
		return "nil"
	case int:
		return fmt.Sprintf("int %d", v)
	case string:
		return fmt.Sprintf("string %q", v)
	case []byte:
		return fmt.Sprintf("bytes len=%d", len(v))
	default:
		return fmt.Sprintf("other %T", v)
	}
}
```

```go
// fallthrough — executes *next case body* without re-checking its condition
switch n {
case 1:
	fmt.Println("one")
	fallthrough
case 2:
	fmt.Println("two or fell from one")
}
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| `fallthrough` ignores next case condition | Easy to misuse — rare in idiomatic Go |
| Type switch only on interfaces | `switch x.(type)` requires `x` to be interface-typed |
| Missing `default` in type switch | Unhandled types silently do nothing |
| Case order matters for expression-less | First matching case wins |

## Trigger Phrase

> “I use `switch` for equalities, expression-less `switch` for condition ladders, and type switches to unpack interfaces — cases don’t fall through unless I write `fallthrough`.”

## Exercise

Write a function `func Normalize(v any) (string, error)` that accepts `string`, `[]byte`, or `fmt.Stringer`, returns a string form, and errors on anything else — implemented with a type switch.
