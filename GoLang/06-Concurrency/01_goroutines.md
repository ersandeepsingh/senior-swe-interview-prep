# Goroutines

> A **goroutine** is a lightweight, independently scheduled function invocation started with `go f()`. Thousands (often millions) can run on a small set of OS threads via the Go runtime scheduler (GMP: G=goroutine, M=OS thread, P=processor/context).

## Plain English

Think of a goroutine as a cheap “green thread.” You say `go doWork()`, and the runtime parks, resumes, and multiplexes that work onto real OS threads. You don’t manage threads yourself; you manage *when work starts* and *how it stops*.

Goroutines are concurrent (interleaved), not necessarily parallel. Parallelism needs multiple cores and `GOMAXPROCS` > 1 (default is number of CPUs).

## Interviewer Angle

- What does `go` actually do? (starts a new G; does not wait)
- How are goroutines scheduled? (work-stealing, M:N on Ps)
- Are they preemptive? (yes since Go 1.14 for most loops; async preemption)
- Cost vs OS threads? (stack starts ~2KB and grows; threads are MBs + kernel)
- Difference: concurrency vs parallelism?

## Go Examples

```go
package main

import (
	"fmt"
	"time"
)

func say(msg string) {
	for i := 0; i < 3; i++ {
		fmt.Println(msg, i)
		time.Sleep(50 * time.Millisecond)
	}
}

func main() {
	go say("goroutine") // returns immediately; main may exit before this finishes
	say("main")

	// Bad interview habit: time.Sleep to "wait" for goroutines.
	// Prefer WaitGroup, channel, or context (see later topics).
	time.Sleep(200 * time.Millisecond)
}
```

```go
// Anonymous goroutine — capture carefully (pre-1.22 loop bug).
for _, v := range items {
	v := v // copy; needed before Go 1.22
	go func() {
		process(v)
	}()
}
```

Go 1.22+ per-iteration loop variables largely fixed the classic capture bug, but interviewers still ask about it.

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| `main` returns → process exits | All goroutines die; unfinished work is lost |
| Fire-and-forget with no join | Leaks, races, flaky tests |
| Assuming FIFO / fairness | Scheduler does not guarantee order |
| Blocking forever in a goroutine | Can pin an M (e.g. cgo, syscalls) or stall pipelines |
| Expecting parallel CPU with 1 P | Concurrency ≠ parallelism |

## Trigger Phrase

> “A goroutine is a lightweight concurrent function the runtime multiplexes onto OS threads — `go` starts it but doesn’t wait; I always have an explicit exit and join strategy.”

## Exercise

Write a program that starts 10 goroutines, each printing its ID, and exits only after all have finished — **without** using `time.Sleep`. (Hint: `sync.WaitGroup` or a done channel.)
