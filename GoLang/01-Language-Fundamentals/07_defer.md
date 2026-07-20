# `defer`

> `defer` schedules a function call to run when the surrounding function returns — after return values are set, before the function actually hands control back. Multiple defers run in **LIFO** order. Arguments are evaluated **at defer time**, not at execution time.

## Plain English

Use `defer` for cleanup that must happen on every exit path: `Close()`, unlock mutexes, cancel contexts, restore state. You put the cleanup next to the setup so you don’t forget it in an early `return`.

LIFO means the last deferred call runs first — nested resources unwind correctly (unlock before close, etc.).

Critical nuance: `defer f(x)` evaluates `x` immediately. If you need the value at return time, defer a closure that reads the variable: `defer func() { f(x) }()`.

## Interviewer Angle

- When are deferred args evaluated?
- Order of multiple defers?
- `defer` in a loop — what happens?
- Can `defer` modify named return values? (yes — via closure)
- Defer cost? (small; avoid in tiny hot loops if profiling says so)

## Go Examples

```go
f, err := os.Open(path)
if err != nil {
	return err
}
defer f.Close() // runs on all return paths

data, err := io.ReadAll(f)
return err
```

```go
// LIFO
defer fmt.Println("first deferred — runs last")
defer fmt.Println("second deferred — runs first")
```

```go
// Args evaluated at defer time
func demo() {
	x := 1
	defer fmt.Println(x) // prints 1
	x = 2
}

// Closure sees current value at run time
func demo2() {
	x := 1
	defer func() { fmt.Println(x) }() // prints 2
	x = 2
}
```

```go
// Named result modified by defer
func read() (n int, err error) {
	defer func() {
		if err != nil {
			n = 0 // can amend named returns
		}
	}()
	return 10, errors.New("boom")
}
```

## Bad vs Good

```go
// Bad: defer in loop — all Close calls pile up until function returns
for _, path := range paths {
	f, err := os.Open(path)
	if err != nil {
		return err
	}
	defer f.Close() // holds all files open
}

// Good: wrap per-iteration work in a function
for _, path := range paths {
	if err := process(path); err != nil {
		return err
	}
}
func process(path string) error {
	f, err := os.Open(path)
	if err != nil {
		return err
	}
	defer f.Close()
	return work(f)
}
```

## Trigger Phrase

> “`defer` runs on function exit in LIFO order; arguments are frozen at defer time. I use it for cleanup, and I never `defer` inside a hot loop without wrapping the body in a function.”

## Exercise

Predict the output of this program, then explain how to make the deferred print show the final `x`:

```go
func main() {
	x := "a"
	defer fmt.Println(x)
	x = "b"
	defer func() { fmt.Println(x) }()
	x = "c"
}
```
