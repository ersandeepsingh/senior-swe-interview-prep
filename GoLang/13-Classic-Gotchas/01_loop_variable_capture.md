# Loop Variable Capture in Goroutines/Closures

> Closures capture **variables**, not values. Pre-Go 1.22, the loop variable was reused — all goroutines saw the final value. Go 1.22+ creates a fresh per-iteration variable.

## Plain English

The #1 Go gotcha historically: `for i := range n { go func() { use(i) }() }` — every goroutine might print the same last `i`. Since Go 1.22, each iteration has its own `i`, but interviewers still ask (legacy code + “explain why”).

## Why interviewers ask 🔴⭐

Shows you understand closures and Go’s history. Always know the explicit `go func(i int)` pattern — it works on all versions.

## Broken (pre-1.22 semantics / still a useful demo)

```go
func broken() {
    var wg sync.WaitGroup
    for i := 0; i < 3; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            fmt.Println(i) // often 3,3,3 before Go 1.22
        }()
    }
    wg.Wait()
}
```

Same class of bug with `for _, v := range items { go func() { use(v) }() }`.

## Fixed

```go
func fixed() {
    var wg sync.WaitGroup
    for i := 0; i < 3; i++ {
        wg.Add(1)
        go func(i int) { // pass by value — shadow intentionally
            defer wg.Done()
            fmt.Println(i) // 0,1,2 (any order)
        }(i)
    }
    wg.Wait()
}

// Also fine on Go 1.22+ without the param — but be explicit in interviews:
// go func() { defer wg.Done(); fmt.Println(i) }()
```

Alternative: `i := i` inside the loop (pre-1.22 idiom).

## Pitfalls

- Assuming “we’re on 1.22+ so I never think about it” — libraries still support older Go.
- Capturing `t *testing.T` loop vars incorrectly in parallel subtests (use `tt := tt` / `t.Run` carefully).
- Range over mutex-protected maps launching goroutines that use the key/value later without copying.

## Interview trigger phrase

> “Closures capture the variable; I’d pass the iteration value as an argument — and I know Go 1.22 fixed per-iteration loop vars.”

## Exercise

Write a test that fails on the broken pattern under Go 1.21 mentally, then show three correct fixes (`param`, `i := i`, and 1.22+ behavior).
