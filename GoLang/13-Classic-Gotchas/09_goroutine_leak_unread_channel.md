# Goroutine Leak from Unread Channel

> A goroutine blocked forever on send/receive is a **leak** — it holds stack/memory and can pin referenced objects; always ensure an exit path (receive, close, or context).

## Plain English

If you start a worker that sends on a channel and nobody receives (or receives only sometimes), the worker blocks forever. Unlike deadlocks that freeze the whole program, leaks often leave the main path “working” while ghost goroutines accumulate under load.

## Why interviewers ask 🔴⭐

Production memory growth + goroutine pprof spikes. Pair with context cancellation answers.

## Broken

```go
func broken(ctx context.Context) <-chan int {
    out := make(chan int)
    go func() {
        // expensive work
        v := 42
        out <- v // blocks forever if caller never receives
    }()
    return out
}

func user() {
    ctx, cancel := context.WithTimeout(context.Background(), time.Millisecond)
    defer cancel()
    ch := broken(ctx)
    select {
    case <-ctx.Done():
        return // abandoned receive — sender goroutine LEAKS
    case <-ch:
    }
}
```

## Fixed

```go
func fixed(ctx context.Context) <-chan int {
    out := make(chan int, 1) // buffer helps if caller cancels after send readiness
    go func() {
        v := 42
        select {
        case out <- v:
        case <-ctx.Done():
            // exit without leak
        }
    }()
    return out
}

// Or: don't return channels from libs — accept a dest / callback with ctx
func compute(ctx context.Context) (int, error) {
    // ...
    select {
    case <-ctx.Done():
        return 0, ctx.Err()
    default:
        return 42, nil
    }
}
```

Buffered size 1 is a common pattern so a single send can complete even if the receiver already left — but still honor `ctx.Done()` for work you can abort *before* send.

## Detect

```bash
go tool pprof http://localhost:6060/debug/pprof/goroutine
# look for stuck channel operations growing over time
```

## Pitfalls

- Leaking on receive side too: `for v := range ch` when `ch` never closed.
- Fan-in without waiting / canceling producers.
- Timeouts that abandon workers without signaling them.

## Interview trigger phrase

> “I’d give every goroutine an exit path — usually `ctx.Done()` in a select with send/receive — and confirm with goroutine profiles.”

## Exercise

Fix a worker pool where jobs are sent to `jobs` but on shutdown the dispatcher stops sending and returns without closing `jobs` or canceling workers. What’s the leak, and what’s the shutdown order?
