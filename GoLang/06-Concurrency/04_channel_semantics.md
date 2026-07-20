# Channel Semantics

> Channel operations obey precise **blocking, closing, and nil** rules. Mastering these rules prevents deadlocks, panics, and “why is this hanging?” bugs in interviews and production.

## Plain English

Think of a channel as a pipe with a state machine:

| Operation | Open channel | Closed channel | Nil channel |
|-----------|--------------|----------------|-------------|
| Send `ch <- v` | Blocks if unbuffered (no recv) or buffer full | **panic** | Blocks forever |
| Receive `<-ch` | Blocks if empty | Returns zero value immediately; `ok=false` | Blocks forever |
| Close `close(ch)` | Marks closed; wake receivers | **panic** (close of closed) | **panic** |
| `range ch` | Iterates until closed | Exits loop | Blocks forever |

Comma-ok receive: `v, ok := <-ch` — `ok` is `false` when `v` is the zero value from a closed channel (and no more data in buffer).

## Interviewer Angle

- Walk through send/receive on open, closed, nil.
- Why does send-on-closed panic?
- When does `range` over a channel exit?
- What happens to buffered values after close? (still receivable until drained)
- How do you broadcast “done”? (close a done channel; never send on it after)

## Go Examples

```go
ch := make(chan int, 2)
ch <- 10
ch <- 20
close(ch)

v, ok := <-ch // 10, true
v, ok = <-ch  // 20, true
v, ok = <-ch  // 0, false  — drained + closed
v, ok = <-ch  // 0, false  — still safe; always zero, ok=false
```

```go
// Done channel idiom — close to broadcast.
done := make(chan struct{})
go func() {
	defer close(done)
	work()
}()
<-done // wait
```

```go
// Nil channel disables a select case (see select topic).
var ch chan int // nil
select {
case <-ch: // never ready
default:
	fmt.Println("skipped")
}
```

## Gotchas

| Gotcha | Reality |
|--------|---------|
| “Receive from closed always blocks” | False — returns immediately |
| Closing from receiver | Wrong ownership; can race with sender → panic |
| Checking `len(ch)` for sync | Racy; not a synchronization primitive |
| Forgetting buffer drains after close | Values already in buffer are still there |
| `close` to “interrupt” a send | Sender may already have sent; use `ctx` + `select` |

## Trigger Phrase

> “Send on closed panics, receive on closed returns zero with `ok=false`, nil channels block forever — and only the sender closes.”

## Exercise

Without running code, predict the output / panic / hang for:

```go
ch := make(chan int, 1)
ch <- 1
close(ch)
fmt.Println(<-ch)
ch <- 2
```

Then fix it so the second send never panics and the program always terminates.
