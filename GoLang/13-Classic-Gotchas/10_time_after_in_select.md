# `time.After` in `select` Loops

> Each `time.After(d)` creates a **new timer** that lives until it fires. Inside a hot `select` loop, abandoned timers **leak** until expiry — use `time.NewTimer` and `Reset`/`Stop` instead.

## Plain English

`time.After` is fine for one-shot timeouts. In a loop that iterates often (or a long-lived `for { select { ... } }`), calling `time.After` every iteration allocates timers you may never wait on. Under load → memory + timer queue growth.

## Why interviewers ask 🔴

Subtle production leak. Distinguishes “used timeouts” from “understands the runtime.”

## Broken

```go
func broken(ctx context.Context, in <-chan Job) {
    for {
        select {
        case <-ctx.Done():
            return
        case job := <-in:
            handle(job)
        case <-time.After(time.Second): // NEW timer every iteration!
            // idle housekeeping
            heartbeat()
        }
    }
}
```

If `in` is busy, the `time.After` case rarely wins — but timers still sit around until they fire.

## Fixed

```go
func fixed(ctx context.Context, in <-chan Job) {
    idle := time.NewTimer(time.Second)
    defer idle.Stop()

    for {
        select {
        case <-ctx.Done():
            return
        case job := <-in:
            if !idle.Stop() {
                select {
                case <-idle.C: // drain if already fired
                default:
                }
            }
            handle(job)
            idle.Reset(time.Second)
        case <-idle.C:
            heartbeat()
            idle.Reset(time.Second)
        }
    }
}
```

Simpler alternative when you only need a context deadline: `context.WithTimeout` / `WithDeadline` per request, not per loop tick.

For “wait up to D for one receive”:

```go
timer := time.NewTimer(d)
defer timer.Stop()
select {
case v := <-ch:
    _ = v
case <-timer.C:
}
```

## Pitfalls

- Forgetting to drain `timer.C` after `Stop` returns false — next `Reset` can spuriously fire.
- Using `time.After` in tests in tight loops — flakes + leaks in long test runs.
- Preferring tickers when a single timer Reset is enough (and forgetting `ticker.Stop()`).

## Interview trigger phrase

> “I’d avoid `time.After` in loops — reuse `time.NewTimer` with `Stop`/`Reset`, and drain the channel when Stop loses the race.”

## Exercise

Rewrite a rate-limiter loop that does `case <-time.After(interval)` on every iteration to use a single `Ticker`. What do you defer, and what happens if you leave the ticker running after return?
