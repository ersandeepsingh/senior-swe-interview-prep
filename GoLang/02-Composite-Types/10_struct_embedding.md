# Struct Embedding

> Embedding a type as an anonymous field **promotes** its exported fields and methods onto the outer struct. This is composition (has-a / reuse), not inheritance. If two embedded types promote the same name, the outer type must disambiguate — the compiler won’t guess at the call site if it’s ambiguous.

## Plain English

```go
type Engine struct{ Power int }
type Car struct {
	Engine // embedded
	Name   string
}
```

`car.Power` is sugar for `car.Engine.Power`. Methods on `Engine` are promoted and callable on `Car` — but the receiver is still the embedded field (important for interface satisfaction and pointer/value method sets).

Embedding is how Go gets “is-a-ish” reuse without classes. Prefer embedding for orthogonal capabilities (`sync.Mutex`, `io.Reader` wrappers); prefer named fields when the relationship isn’t “part of me.”

## Interviewer Angle

- Is embedding inheritance? (no — composition)
- How does method promotion interact with pointer receivers?
- Ambiguous selectors — what happens?
- Does embedding promote unexported fields to other packages? (name promotion still respects export of the field itself; outer package can’t access inner unexported fields)
- Embedding a pointer vs value?

## Go Examples

```go
type Logger struct{}

func (l Logger) Log(msg string) { fmt.Println(msg) }

type Server struct {
	Logger // promoted Log method
	Addr   string
}

s := Server{Addr: ":8080"}
s.Log("up") // promoted
```

```go
type A struct{ N int }
type B struct{ N int }
type C struct {
	A
	B
}
var c C
// c.N // compile error: ambiguous
c.A.N = 1 // explicit
```

```go
type Mutex = sync.Mutex // don't embed Mutex by value across copy boundaries carelessly
type SafeCounter struct {
	mu sync.Mutex // named field often clearer than embedding Mutex
	n  int
}
```

## Bad vs Good

```go
// Bad: embedding sync.Mutex and letting the struct be copied
type Counter struct {
	sync.Mutex
	n int
}
c1 := Counter{}
c2 := c1 // copies the mutex — undefined / dangerous

// Good: never copy a mutex; keep it unexported as named field; pass *Counter
type Counter struct {
	mu sync.Mutex
	n  int
}
```

## Trigger Phrase

> “Embedding promotes fields and methods for composition — it’s not inheritance. I disambiguate collisions explicitly and I’m careful embedding types that shouldn’t be copied, like mutexes.”

## Exercise

Embed a `Reader` struct with method `Read() string` inside `File`, add a `Read()` method on `File` that overrides promotion, and show how to still call the inner `Read`. Then satisfy an interface that requires `Read()` with `*File`.
