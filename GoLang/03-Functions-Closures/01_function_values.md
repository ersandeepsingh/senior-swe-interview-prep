# Function Values & First-Class Functions

> Functions are values: you can assign them to variables, pass them as arguments, and return them from other functions. Function types are written `func(paramTypes) resultTypes`.

## Plain English

Callbacks, middleware, and strategy-style behavior in Go are just functions (often with closures). There is no separate “delegate” or “lambda type” — anonymous functions are literals of function type.

Nil function values exist: `var f func()` is nil; calling it panics. Check before call if a callback is optional.

## Interviewer Angle

- How do you type a higher-order function?
- Function equality? (only comparable to `nil`)
- Closures vs methods as callbacks?
- When prefer an interface with one method vs a function type? (`http.Handler` vs `HandlerFunc`)

## Go Examples

```go
func apply(n int, fn func(int) int) int {
	return fn(n)
}

double := func(x int) int { return x * 2 }
fmt.Println(apply(5, double)) // 10

// Return a function
func multiplier(k int) func(int) int {
	return func(x int) int { return x * k }
}
times3 := multiplier(3)
fmt.Println(times3(4)) // 12
```

```go
type Transform func(string) string

func pipeline(s string, steps ...Transform) string {
	for _, step := range steps {
		s = step(s)
	}
	return s
}
```

```go
var hook func(string)
if hook != nil {
	hook("event")
}
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Calling nil func | Panic |
| Comparing two funcs with `==` | Illegal except vs nil |
| Capturing loop vars in returned funcs | Classic closure bug (see Closures) |

## Trigger Phrase

> “Functions are first-class values with typed signatures — I pass and return them for callbacks and pipelines, and I treat nil func like a nil pointer: check before call.”

## Exercise

Write `func Compose[T any](f, g func(T) T) func(T) T` (or non-generic equivalent) that returns `f(g(x))`, and demonstrate with two string transforms.
