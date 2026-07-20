# Escape Analysis & Allocation

> The compiler decides whether a value can live on the **stack** or must **escape** to the **heap**; fewer escapes → less GC pressure.

## Plain English

Stack allocation is cheap and dies with the goroutine frame. If a value’s lifetime might outlive the stack frame (returned pointer, stored in interface/heap object, shared to unknown code), it **escapes** → heap alloc. Escape analysis is compile-time, conservative.

## Why interviewers ask 🔴⭐

“Why is this allocating?” — seniors read `go build -gcflags="-m"` and design APIs that don’t force escapes.

## See decisions

```bash
go build -gcflags="-m -m" ./pkg 2>&1 | less
# foo passes to sink → escapes to heap
# moved to heap: x
# inlining call to ...
```

## Examples

```go
// Likely stack: nothing takes address beyond frame
func sum(a, b int) int {
    x := a + b
    return x
}

// Escapes: pointer to local returned
func newInt() *int {
    x := 42
    return &x // x moved to heap
}

// Often escapes: stored in interface
func asAny(x int) any {
    return x // may allocate (boxed)
}

// Slice backing store usually heap (size unknown / large)
func makeBuf(n int) []byte {
    return make([]byte, n)
}
```

## Design tips to reduce escapes

- Prefer returning values over pointers when small and immutable-enough.
- Accept `[]byte` buffers from the caller (`AppendJSON(buf []byte) []byte`) instead of always allocating inside.
- Careful with closures capturing large vars — they can keep objects alive / force heap.
- Avoid converting hot-path numbers to `any` / interfaces.

## Pitfalls

- Premature micro-optimizing for escape without profiles.
- Assuming “small struct → always stack” — taking address, interfaces, or concurrency can change that.
- Believing escape analysis is the same across Go versions — verify with `-m`.
- Confusing stack growth (goroutine stacks grow/shrink) with heap escape.

## Interview trigger phrase

> “I’d check escapes with `-gcflags=-m`, keep hot values on the stack when safe, and design APIs that reuse caller buffers so fewer objects hit the heap.”

## Exercise

Predict which of these escape, then verify with `-gcflags="-m"`:

```go
func A() *User { u := User{Name: "a"}; return &u }
func B() User  { u := User{Name: "a"}; return u }
func C() any   { u := User{Name: "a"}; return u }
```
