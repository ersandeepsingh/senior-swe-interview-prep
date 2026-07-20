# `testing` Package — Table-Driven Tests & Subtests

> Write tests as `TestXxx(t *testing.T)`; prefer **table-driven** cases and `t.Run` for clear failures.

## Plain English

Go’s test runner discovers `Test*` functions in `*_test.go`. Table-driven style: one slice of cases, one loop, shared assertions. Subtests (`t.Run`) give named failures and let you control parallelism with `t.Parallel()`.

## Why interviewers ask ⭐

They watch whether you test behavior in tables, name cases well, and use `t.Helper()` / `t.Cleanup` like a professional — not one giant script test.

## Example

```go
package calc

import "testing"

func TestAdd(t *testing.T) {
    tests := []struct {
        name string
        a, b int
        want int
    }{
        {"positive", 2, 3, 5},
        {"zero", 0, 0, 0},
        {"negative", -1, 1, 0},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)
            if got != tt.want {
                t.Fatalf("Add(%d,%d)=%d want %d", tt.a, tt.b, got, tt.want)
            }
        })
    }
}

func TestFile(t *testing.T) {
    f := createTemp(t) // uses t.Helper + t.Cleanup inside
    _ = f
}

func createTemp(t *testing.T) *os.File {
    t.Helper()
    f, err := os.CreateTemp("", "test-*")
    if err != nil {
        t.Fatal(err)
    }
    t.Cleanup(func() { _ = os.Remove(f.Name()); _ = f.Close() })
    return f
}
```

## External vs internal test packages

```text
package calc       // white-box: can access unexported
package calc_test  // black-box: only exported API — often preferred for public packages
```

## Useful `T` methods

| Method | Use |
|--------|-----|
| `Fatal` / `Fatalf` | fail and abort this test |
| `Error` / `Errorf` | fail but continue |
| `Run` | subtest |
| `Parallel` | run alongside other parallel tests |
| `Cleanup` | defer-like teardown (LIFO) |
| `Helper` | mark helper so failures point at caller |
| `Skip` | skip when env/feature unavailable |
| `TempDir` | per-test temp directory |

## Pitfalls

- Loop variable capture in old Go when launching goroutines in tests (fixed 1.22+ for `for` vars; still careful with closures).
- Calling `t.Parallel()` incorrectly with shared mutable state across cases.
- Huge fixtures in every test — use `t.TempDir` and builders.
- Asserting on log strings instead of returned errors/values.

## Interview trigger phrase

> “I’d write table-driven subtests with clear names, use `t.Cleanup`/`TempDir`, and black-box test the exported API unless I’m covering internals.”

## Exercise

Write table-driven tests for `ParseDuration("10s")` covering valid, empty, and invalid input — including a subtest that expects an error with `errors.Is`.
