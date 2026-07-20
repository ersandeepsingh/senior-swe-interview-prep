# Buffered vs Unbuffered Channel Deadlocks

> Send/receive **block** until the other side is ready (unbuffered) or until buffer space/data exists (buffered). Wrong assumptions → deadlock (`all goroutines are asleep`).

## Plain English

Unbuffered: handshake — send waits for receive. Buffered(N): send succeeds until N items are queued; then it blocks like unbuffered. Receiving from empty buffer blocks. Classic deadlock: same goroutine sends on unbuffered (or full) channel and never reaches the receive.

## Why interviewers ask 🔴⭐

Concurrency make-or-break. Runtime prints the deadlock error — explain *why*.

## Broken (same goroutine, unbuffered)

```go
func broken() {
    ch := make(chan int) // unbuffered
    ch <- 1              // blocks forever — no receiver
    <-ch
}
```

## Broken (buffer full)

```go
func brokenFull() {
    ch := make(chan int, 1)
    ch <- 1
    ch <- 2 // blocks — buffer full, no receiver
}
```

## Fixed

```go
func fixed() {
    ch := make(chan int)
    go func() { ch <- 1 }() // sender in another goroutine
    fmt.Println(<-ch)
}

func fixedBuffered() {
    ch := make(chan int, 1)
    ch <- 1          // ok — room in buffer
    fmt.Println(<-ch)
}
```

## Nil channel

```go
var ch chan int // nil
// ch <- 1  // blocks forever
// <-ch     // blocks forever
// useful in select to disable a case
```

## Pitfalls

- Assuming buffer size “makes it async forever” — only until full.
- Forgetting to `close` when ranging (different bug: leak/block on receive).
- Both sides waiting on opposite channels (lock-order style deadlock).
- Using unbuffered where a small buffer would absorb bursts (or vice versa — buffer hiding slow consumers until OOM of pending work elsewhere).

## Interview trigger phrase

> “Unbuffered needs a partner; buffered blocks when full — I’d never send and receive on the same goroutine without enough buffer, and I’d design ownership clearly.”

## Exercise

Will this deadlock? Explain.

```go
ch := make(chan int, 2)
ch <- 1
ch <- 2
go func() { fmt.Println(<-ch); fmt.Println(<-ch) }()
time.Sleep(time.Millisecond)
```

Then change buffer to `0` and explain again.
