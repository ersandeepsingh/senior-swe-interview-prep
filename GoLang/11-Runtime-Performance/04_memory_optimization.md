# Memory Optimization — Alignment, Allocs & `sync.Pool`

> Shrink footprint and GC work via **field alignment**, fewer allocations, reuse (`sync.Pool`), and smarter data layouts.

## Plain English

Two structs with the same fields can have different sizes because of **padding** for alignment. Allocation churn creates GC work. `sync.Pool` caches temporary objects per-P (cleared between GCs) for short-lived reuse — great for buffers, bad for anything needing strong lifetime guarantees.

## Why interviewers ask 🔴

They want you to reason about cache lines, padding, and whether `Pool` is appropriate — not just recite “use a pool.”

## Struct alignment

```go
// Bad order — more padding
type Bad struct {
    a bool    // 1
    // 7 bytes padding
    b int64   // 8
    c bool    // 1
    // 7 bytes padding
} // often 24 bytes

// Better — pack smaller fields together
type Good struct {
    b int64
    a bool
    c bool
} // often 16 bytes
```

Check with `unsafe.Sizeof`, `align` tools, or `fieldalignment` analyzer.

## Reduce allocations

```go
// Reuse buffer
var buf []byte
buf = append(buf[:0], data...) // keep capacity

// Pool for temporary buffers
var bufPool = sync.Pool{
    New: func() any { return make([]byte, 0, 4096) },
}

func handle() {
    b := bufPool.Get().([]byte)
    b = b[:0]
    defer bufPool.Put(b)
    // use b = append(b, ...)
}
```

## Other levers

- Preallocate slices: `make([]T, 0, n)` when `n` known.
- Avoid `string` ↔ `[]byte` conversions in hot loops (copies).
- Prefer `[]T` of structs over `[]*T` when pointers aren’t needed (fewer objects, better locality) — trade-offs for mutability/identity.
- Intern / dedupe rare for strings only with clear ownership.

## Pitfalls

- `sync.Pool` is **not** a free list with pin guarantees — objects can vanish anytime (GC). Don’t store critical state only in a Pool.
- Pool thrash under low alloc pressure can look like a wash — measure.
- Over-packing structs for 8 bytes at readability cost without proof.
- Growing a shared slice without sync → races.

## Interview trigger phrase

> “I’d reorder fields for alignment, preallocate and reuse buffers, use `sync.Pool` only for ephemeral scratch, and prove wins with `-benchmem` and heap profiles.”

## Exercise

You allocate a `bytes.Buffer` per request. Redesign with a `sync.Pool`. What do you put in `New`, what do you reset before `Put`, and what must you never keep after the request ends?
