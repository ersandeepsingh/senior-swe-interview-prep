# `defer` in a Loop

> `defer` runs when the **function** returns, not when the loop iteration ends — deferred calls **pile up** until exit.

## Plain English

`defer f.Close()` inside `for` schedules a close for each iteration but doesn’t run them until the surrounding function returns. Holding thousands of files/locks until then → resource exhaustion. Also LIFO order among all deferred calls.

## Why interviewers ask 🟡⭐

Common bug in “process all files” snippets. Fix with a function scope or explicit close.

## Broken

```go
func broken(paths []string) error {
    for _, p := range paths {
        f, err := os.Open(p)
        if err != nil {
            return err
        }
        defer f.Close() // closes only when broken() returns — all files stay open!
        _, _ = io.ReadAll(f)
    }
    return nil
}
```

## Fixed

```go
func fixed(paths []string) error {
    for _, p := range paths {
        if err := readOne(p); err != nil {
            return err
        }
    }
    return nil
}

func readOne(p string) error {
    f, err := os.Open(p)
    if err != nil {
        return err
    }
    defer f.Close() // runs at end of each readOne call
    _, err = io.ReadAll(f)
    return err
}

// Or inline with a closure:
func fixedClosure(paths []string) error {
    for _, p := range paths {
        err := func() error {
            f, err := os.Open(p)
            if err != nil {
                return err
            }
            defer f.Close()
            _, err = io.ReadAll(f)
            return err
        }()
        if err != nil {
            return err
        }
    }
    return nil
}
```

## Pitfalls

- `defer mu.Unlock()` in a loop that locks each time — can deadlock yourself if unlocks don’t run until end.
- Relying on defer for per-iteration metrics flush.
- Forgetting defers still run on `return` / `panic` in that function — good for cleanup when scoped correctly.

## Interview trigger phrase

> “Defer binds to the function, not the loop — I’d wrap each iteration in a function so Close runs immediately.”

## Exercise

Rewrite a loop that `Lock`s a mutex per item and `defer Unlock`s into a safe version, and explain the deadlock you’d get if the unlocks were deferred on the outer function.
