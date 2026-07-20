# Maps

> A map is an unordered hash table: `map[K]V`. Create with `make` or a literal. Lookup uses **comma-ok** to distinguish missing keys from zero values. Delete with `delete`. Iteration order is **randomized** — never rely on it.

## Plain English

Maps are reference-like: assigning a map copies the header; both refer to the same table. The zero value is `nil` — reads on nil maps return zero values, but writes panic.

Keys must be comparable (`==` allowed): integers, strings, pointers, structs of comparable fields — not slices, maps, or functions.

```go
v, ok := m[k] // ok=false if k not present
```

## Interviewer Angle

- How do you tell “missing” from “zero value stored”?
- Why is iteration order random?
- Can map keys be structs? (yes if all fields comparable)
- Nil map read vs write?
- Growing maps — amortized cost?

## Go Examples

```go
m := make(map[string]int)
m["a"] = 1
m["b"] = 2

v, ok := m["a"] // 1, true
v, ok = m["z"]  // 0, false

delete(m, "a")

for k, v := range m { // order not specified
	fmt.Println(k, v)
}

// Literal
ages := map[string]int{"ada": 36, "grace": 85}
```

```go
// Set idiom
seen := make(map[string]struct{})
seen["x"] = struct{}{}
if _, ok := seen["x"]; ok { /* present */ }
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Relying on range order | Flaky tests / subtle bugs |
| Writing to nil map | Panic |
| Using slice as key | Compile error — not comparable |

## Trigger Phrase

> “Maps are unordered hash tables; I always use comma-ok for lookups, never depend on range order, and I `make` before the first write.”

## Exercise

Implement `func Frequency(words []string) map[string]int` and a test that does **not** assert iteration order of the map — only contents.
