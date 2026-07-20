# Stack vs Heap

> **Stack** frames hold function locals that don’t outlive the call — fast alloc/free with the frame. **Heap** holds values that may outlive the function (shared, returned by pointer, captured by goroutines, etc.) and are managed by the **garbage collector**. You don’t choose explicitly — the compiler does via escape analysis.

## Plain English

Stack allocation is cheap (bump a pointer). Heap allocation is more expensive and creates GC work. Go grows goroutine stacks as needed (starting small).

Interviewers don’t want “I malloc” stories — they want: *locals stay on the stack unless they escape; escaping values go to the heap; pointers and interfaces can cause escapes.*

Both are “memory”; the distinction is lifetime and who reclaims it.

## Interviewer Angle

- Who decides stack vs heap?
- Why are heap allocs costly?
- Goroutine stack vs OS thread stack?
- Does `new` always heap-allocate? (not necessarily — can stack if it doesn’t escape)

## Go Examples

```go
func stackish() int {
	x := 42 // likely stack
	return x // returned by value — x need not escape
}

func heapish() *int {
	x := 42
	return &x // x escapes → heap
}
```

```go
// Interface boxing may allocate
func asAny(x int) any { return x } // int may be heap-boxed
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Assuming `new`/`make` ⇒ always heap | Escape analysis decides |
| Assuming Go has manual free | GC owns heap |
| Huge stack frames | Possible, but large objects often escape anyway |

## Trigger Phrase

> “Stack is for short-lived non-escaping locals; heap is for values that outlive the frame and are GC-managed. The compiler chooses via escape analysis — not me.”

## Exercise

For each variable, guess stack vs heap, then verify with `go build -gcflags='-m'`:

```go
func f() *User {
	u := User{Name: "a"}
	return &u
}
func g() User {
	u := User{Name: "a"}
	return u
}
```
