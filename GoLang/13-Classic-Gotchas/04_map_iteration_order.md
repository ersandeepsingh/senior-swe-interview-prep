# Map Iteration Order

> Ranging over a map visits keys in **randomized** order — intentionally — so you don’t depend on unstable hash iteration.

## Plain English

`for k, v := range m` order is not sorted, not insertion order, and can change between runs. Go randomizes starting position to catch order-dependent bugs early.

## Why interviewers ask 🟡⭐

Flaky tests and “why did my golden output change?” — answer: map range.

## Broken

```go
func broken(m map[string]int) string {
    var b strings.Builder
    for k, v := range m { // non-deterministic concatenation
        b.WriteString(fmt.Sprintf("%s=%d;", k, v))
    }
    return b.String()
}

func TestBroken(t *testing.T) {
    got := broken(map[string]int{"a": 1, "b": 2})
    if got != "a=1;b=2;" { // flakes!
        t.Fatalf("got %q", got)
    }
}
```

## Fixed

```go
func fixed(m map[string]int) string {
    keys := make([]string, 0, len(m))
    for k := range m {
        keys = append(keys, k)
    }
    slices.Sort(keys)
    var b strings.Builder
    for _, k := range keys {
        b.WriteString(fmt.Sprintf("%s=%d;", k, m[k]))
    }
    return b.String()
}
```

Or use `maps.Keys` + `slices.Sort` (Go 1.23+ iterators / 1.21+ maps package patterns).

## Pitfalls

- Serializing maps to JSON objects — key order in `encoding/json` is sorted by key for maps, but don’t assume range order elsewhere.
- Hash-dependent algorithms that assumed stable order across process runs.
- Concurrent map iteration + write → fatal race (separate gotcha; use sync or immutable copy).

## Interview trigger phrase

> “Map range is deliberately randomized; for stable output I’d collect keys, sort, then iterate.”

## Exercise

Write a function that returns the top-3 keys by value descending with deterministic tie-breaking by key name.
