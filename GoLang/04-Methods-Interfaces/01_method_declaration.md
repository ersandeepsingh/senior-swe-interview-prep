# Method Declaration

> A method is a function with a **receiver** argument: `func (t T) Method(...)`. Receivers can be any named type (not a pointer or interface type itself as the defined type — you define methods on `T` or `*T` where `T` is named). Methods live in the same package as the type.

## Plain English

Methods attach behavior to data. Unlike classes, you can define methods on `type ID string` or `type Celsius float64` — not only structs.

You cannot add methods to types defined in another package (`func (s string) MyMethod()` is illegal). Alias types vs defined types: `type MyString string` can have methods; `type MyString = string` cannot add new methods to `string`.

## Interviewer Angle

- Can you put methods on built-in types? (wrap them in a defined type)
- Same package requirement?
- Method vs function — when which?
- Promoted methods via embedding?

## Go Examples

```go
type Counter int

func (c Counter) Add(n Counter) Counter {
	return c + n
}

func (c *Counter) Inc() {
	*c++
}

var n Counter = 1
fmt.Println(n.Add(2)) // 3
n.Inc()
```

```go
type User struct {
	Name string
}

func (u User) Greet() string {
	return "hi " + u.Name
}

// Function equivalent
func GreetUser(u User) string {
	return "hi " + u.Name
}
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Methods on type aliases to foreign types | Not allowed for adding methods |
| Huge method sets on one type | God type — split by responsibility |
| Pointer indirection confusion | See next topic |

## Trigger Phrase

> “Methods are functions with a receiver on a named type in the same package — I can attach behavior to structs or defined primitives, but not to types from other packages.”

## Exercise

Create `type Email string` with method `Valid() bool` (simple contains `@` check) and show why you couldn’t add `Valid` directly to `string`.
