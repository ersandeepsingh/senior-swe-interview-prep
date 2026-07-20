# `time` — Durations, Timers & Formatting

> Represent instants (`time.Time`) and spans (`time.Duration`); schedule with timers/tickers; format with the **reference time** layout.

## Plain English

Wall clock = `time.Time`. Elapsed span = `time.Duration` (nanoseconds under the hood, typed int64). Sleep/wait = `time.Sleep`, `time.After`, `time.NewTimer`, `time.NewTicker`. Formatting uses a mnemonic layout based on `Mon Jan 2 15:04:05 MST 2006` — not `YYYY-MM-DD` placeholders.

## Why interviewers ask

Timeouts, TTL caches, cron-ish tickers, and the classic “`time.After` in a loop leaks” gotcha. Reference-date layouts confuse everyone once.

## Reference layout (memorize)

```text
Mon Jan 2 15:04:05 MST 2006
1  2   3  4  5  6  -7   2006 = year
```

Common layouts:

```go
time.RFC3339                    // 2006-01-02T15:04:05Z07:00
"2006-01-02"                    // date only
"15:04:05"                      // time only
"2006-01-02 15:04:05"           // local-ish dump
```

## Examples

```go
package main

import (
    "fmt"
    "time"
)

func main() {
    now := time.Now().UTC()
    later := now.Add(2 * time.Hour)
    fmt.Println(later.Sub(now)) // 2h0m0s

    t, err := time.Parse(time.RFC3339, "2026-07-20T10:00:00Z")
    if err != nil {
        panic(err)
    }
    fmt.Println(t.Format("2006-01-02"))

    // Prefer NewTimer when you may Stop/Reset
    timer := time.NewTimer(100 * time.Millisecond)
    defer timer.Stop()
    select {
    case <-timer.C:
        fmt.Println("fired")
    case <-time.After(time.Second): // fine for one-shot select
        fmt.Println("fallback")
    }

    ticker := time.NewTicker(50 * time.Millisecond)
    defer ticker.Stop()
    for i := 0; i < 3; i++ {
        <-ticker.C
        fmt.Println("tick", i)
    }
}
```

## Monotonic clock

`time.Since` / `time.Until` / measuring latency uses the monotonic reading embedded in `Time` — immune to wall-clock jumps for durations. Prefer `time.Since(start)` over subtracting wall clocks manually for benchmarks.

## Pitfalls

- Using `time.After` inside a tight `select` loop → timer channel leak until fire (see Classic Gotchas).
- Forgetting `ticker.Stop()` / `timer.Stop()`.
- Comparing times from different locations without normalizing (`Equal` vs wall equality).
- Parsing without location: `time.Parse` uses UTC for numeric zones; `ParseInLocation` for local civil times.
- Storing `time.Time` in maps as keys with monotonic bits — strip with `t.Round(0)` if needed for equality as map keys (rare).

## Interview trigger phrase

> “I’d use `Duration` for timeouts, `NewTimer`/`NewTicker` with `Stop`, format via the 2006 reference layout, and never park `time.After` in a hot loop.”

## Exercise

Write a function `WaitUntil(ctx context.Context, deadline time.Time) error` that returns when the deadline hits or ctx cancels — without leaking timers on cancel.
