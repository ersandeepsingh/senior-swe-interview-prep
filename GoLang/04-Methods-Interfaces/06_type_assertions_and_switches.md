# Type Assertions & Type Switches

> A **type assertion** `x.(T)` extracts the concrete value from an interface. With comma-ok: `v, ok := x.(T)` — `ok` is false if the dynamic type isn’t `T` (no panic). A **type switch** branches on the dynamic type cleanly.

## Plain English

When you have an `any` or other interface and need the real value, assert. Single-type assertion panics on mismatch if you omit `ok`. Prefer comma-ok or a type switch when the type is uncertain.

Asserting to an interface type checks whether the dynamic value implements that interface.

## Interviewer Angle

- Panic vs comma-ok forms?
- Assertion to interface vs concrete type?
- Type switch vs assertion chain?
- What if dynamic value is nil pointer of type T?

## Go Examples

```go
var i any = "hello"
s := i.(string)        // panics if wrong
s, ok := i.(string)    // ok=false if wrong — safe
n, ok := i.(int)       // false, n=0
```

```go
func handle(err error) {
	if ne, ok := err.(net.Error); ok && ne.Timeout() {
		// retry
	}
}
```

```go
switch v := i.(type) {
case int:
	fmt.Println(v + 1)
case string:
	fmt.Println(len(v))
case error:
	fmt.Println(v.Error())
default:
	fmt.Printf("unexpected %T\n", v)
}
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Assertion without `ok` | Panic in production |
| Asserting wrong pointer/value type | `*T` vs `T` are different |
| Using assertions instead of redesign | Smell — maybe the API should be generic/typed |

## Trigger Phrase

> “I extract from interfaces with comma-ok assertions or type switches — the panic form is only for cases I’m certain about.”

## Exercise

Write `func AsString(v any) (string, bool)` that accepts `string`, `[]byte`, and `fmt.Stringer`, using a type switch, without panicking.
