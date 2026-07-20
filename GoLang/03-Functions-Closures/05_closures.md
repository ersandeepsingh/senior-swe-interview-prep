# Closures

> A closure is a function value that **references variables from its outer scope**. Those variables are captured by reference (the same storage), so the closure sees later mutations. The classic trap is capturing a loop variable — fixed for `for` loops in Go 1.22+, but still an interview staple.

## Plain English

When an inner function uses an outer local, that local lives as long as the closure does (may escape to the heap). All closures that capture the same variable share it.

Pre–Go 1.22: the loop variable was reused each iteration, so `go func() { fmt.Println(v) }` often printed the final `v`. Fix: `v := v` inside the loop, or pass as an argument `go func(v int){...}(v)`.

Go 1.22+: each iteration has its own loop variable — the accidental shared capture is gone for `for` loops. Interviewers still expect you to know the old bug and the safe patterns.

## Interviewer Angle

- Does a closure capture by value or reference?
- Explain the loop capture bug and the fix
- What changed in Go 1.22?
- Escape analysis implication of returning a closure?

## Go Examples

```go
func counter() func() int {
	n := 0
	return func() int {
		n++ // same n each call
		return n
	}
}
c := counter()
fmt.Println(c(), c()) // 1 2
```

```go
// Classic bug pattern (pre-1.22); still teach the safe forms
var fns []func()
for _, v := range []int{1, 2, 3} {
	v := v // defensive copy — good habit in interviews
	fns = append(fns, func() { fmt.Println(v) })
}
for _, fn := range fns {
	fn() // 1 2 3
}

// Argument capture — always clear
for _, v := range []int{1, 2, 3} {
	go func(id int) {
		fmt.Println(id)
	}(v)
}
```

## Bad vs Good

```go
// Bad (historical): all goroutines see final i
for i := 0; i < 3; i++ {
	go func() { fmt.Println(i) }()
}

// Good
for i := 0; i < 3; i++ {
	go func(i int) { fmt.Println(i) }(i)
}
```

## Trigger Phrase

> “Closures capture variables by reference. For loops I either rely on Go 1.22 per-iteration vars or — in interviews — pass values as arguments so capture intent is obvious.”

## Exercise

Write a function that returns three closures each printing a unique index `0..2`. Show both the argument-passing style and the `v := v` style. Explain what an interviewer using Go 1.21 would see without the fix.
