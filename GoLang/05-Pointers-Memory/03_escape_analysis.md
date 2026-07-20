# Escape Analysis

> **Escape analysis** is the compiler pass that decides whether a variable’s lifetime is confined to the current stack frame. If a reference to it can outlive the frame, the variable **escapes** and is allocated on the heap.

## Plain English

Common escape causes:

- Returning `&local`
- Assigning pointer into a heap object / global / interface that outlives the frame
- Sending pointer on a channel
- Capturing variable in a goroutine/closure that outlives the function
- Storing in a slice/map that escapes

Check with:

```bash
go build -gcflags='-m' .
```

Look for messages like `moved to heap`. For deeper detail: `-m -m`.

Optimizing hot paths: reduce unnecessary pointers, avoid boxing into `any` in loops, preallocate slices, reuse buffers (`sync.Pool` when appropriate).

## Interviewer Angle

- How do you prove something escapes?
- Does escape always mean “slow”? (relative — measure)
- Why might a large value not escape but still be costly? (copying)
- Interaction with inlining?

## Go Examples

```go
func noEscape() int {
	x := 10
	return x // stays on stack
}

func escapes() *int {
	x := 10
	return &x // escapes
}

func escapesToInterface() any {
	x := 10
	return x // often heap-boxed as any
}

func mayEscape(out *int) {
	x := 10
	*out = x // x itself may not escape; value copied
}
```

```go
// Closure capture
func counter() func() int {
	n := 0 // escapes — referenced by returned closure
	return func() int { n++; return n }
}
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Premature micro-opts without `-m`/benchmarks | Noise |
| Thinking pointers always escape | Not if confined to frame |
| Ignoring allocs in benchmarks | Use `testing.AllocsPerRun` |

## Trigger Phrase

> “Escape analysis places variables on the heap when references can outlive the frame. I confirm with `-gcflags=-m` and only optimize where profiles show alloc pressure.”

## Exercise

Run escape analysis on a small package containing: return-by-pointer, return-by-value, interface return, and a returned closure. Summarize which locals escape and why.
