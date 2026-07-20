# Channels

> A **channel** (`chan T`) is a typed conduit for sending and receiving values between goroutines. Created with `make(chan T)` (unbuffered) or `make(chan T, n)` (buffered). Directional types (`chan<- T`, `<-chan T`) restrict send vs receive at compile time.

## Plain English

Channels are Go’s built-in message queues between goroutines. Unbuffered means “hand-off”: sender and receiver must meet. Buffered means “mailbox of size n”: send succeeds until the buffer is full; receive succeeds until empty.

Channels synchronize *and* transfer data. Closing a channel signals “no more values.”

## Interviewer Angle

- Unbuffered vs buffered — when each?
- What does closing mean? Who should close?
- Can you send on a closed channel? (panic)
- Directional channels — why use them in APIs?
- Nil channel behavior? (send/receive block forever)

## Go Examples

```go
package main

import "fmt"

func main() {
	// Unbuffered: rendezvous
	unbuf := make(chan string)
	go func() {
		unbuf <- "hello" // blocks until someone receives
	}()
	fmt.Println(<-unbuf)

	// Buffered: capacity 2
	buf := make(chan int, 2)
	buf <- 1
	buf <- 2
	// buf <- 3 // would block until a receive frees a slot
	fmt.Println(<-buf, <-buf)
}
```

```go
// Directional types document ownership.
func producer(out chan<- int) {
	for i := 0; i < 3; i++ {
		out <- i
	}
	close(out) // sender closes
}

func consumer(in <-chan int) {
	for v := range in {
		fmt.Println(v)
	}
}

func main() {
	ch := make(chan int)
	go producer(ch)
	consumer(ch)
}
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| Closing a receive-only channel | Compile error — good |
| Multiple closers | Panic if closed twice; only one closer |
| Assuming order across multiple channels | No global order; only per-channel FIFO |
| Large buffers to “fix” races | Hides backpressure; can OOM |
| Returning bare `chan T` from API | Prefer `<-chan` / `chan<-` to encode intent |

## Trigger Phrase

> “Channels move values and synchronize; unbuffered is a rendezvous, buffered is a bounded queue — the sender closes, and directional types make ownership obvious.”

## Exercise

Implement `func Merge(a, b <-chan int) <-chan int` that merges two channels into one until both are closed, then closes the output. No leaks when either input is slow.
