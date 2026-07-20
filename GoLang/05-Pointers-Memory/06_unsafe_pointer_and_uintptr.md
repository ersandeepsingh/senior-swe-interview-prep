# `unsafe.Pointer` & `uintptr`

> `unsafe.Pointer` is a pointer type that can convert to/from any pointer type and to/from `uintptr`. **`uintptr` is an integer** holding an address — not a pointer the GC understands. Misuse breaks memory safety; use only when justified (interop, low-level performance, atomic pointer tricks) and follow the `unsafe` rules precisely.

## Plain English

Normal Go: no arbitrary cast between `*T` and `*U`. With `unsafe`:

```go
p := unsafe.Pointer(&t)
u := (*U)(p) // reinterpret — must be valid
```

`uintptr(ptr)` is for arithmetic / syscalls. Critical rule: **don’t store addresses only in `uintptr` across points where GC can move objects** — the GC won’t update uintptrs. Keep a real pointer live, or use documented patterns (`runtime.KeepAlive`, `atomic.Pointer`, etc.).

Most application code never needs `unsafe`. Interview signal: know *why* it’s dangerous and when packages like `reflect` or `sync/atomic` already cover the need.

## Interviewer Angle

- Difference between `unsafe.Pointer` and `uintptr`?
- Why can uintptr dangle?
- Valid conversion patterns? (six rules in unsafe package docs)
- When is unsafe justified vs “clever”?

## Go Examples

```go
import "unsafe"

// Sizeof / Alignof / Offsetof — relatively benign
type Point struct{ X, Y int }
fmt.Println(unsafe.Sizeof(Point{}))
fmt.Println(unsafe.Offsetof(Point{}.Y))
```

```go
// String header inspection (illustrative — prefer safer APIs)
type stringHeader struct {
	Data unsafe.Pointer
	Len  int
}
s := "hi"
hdr := (*stringHeader)(unsafe.Pointer(&s))
fmt.Println(hdr.Len)
```

```go
// DANGEROUS pattern sketch — do not use casually
// u := uintptr(unsafe.Pointer(p))
// // GC may have moved or freed — u is now a raw int
// p2 := unsafe.Pointer(u) // may be invalid
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Holding only uintptr across GC | Use-after-free / corruption |
| Violating alignment | Crashes on some archs |
| Assuming Go objects never move | Stack growth / GC details — follow rules |
| Using unsafe to “skip” type system | Undefined behavior, breaks with compiler upgrades |

## Trigger Phrase

> “`unsafe.Pointer` bridges pointer types; `uintptr` is just an int — the GC won’t track it. I avoid unsafe unless I’m following documented patterns for a measured reason.”

## Exercise

Explain why this is unsafe, and rewrite without `unsafe` if possible:

```go
func FastString(b []byte) string {
	return *(*string)(unsafe.Pointer(&b))
}
```

(Hint: aliasing and mutability — what happens if `b` changes later? What does Go 1.22+ / `unsafe.String` document?)
