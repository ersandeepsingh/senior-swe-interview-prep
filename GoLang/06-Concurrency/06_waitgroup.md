# sync.WaitGroup

> `sync.WaitGroup` waits for a collection of goroutines to finish. `Add(delta)` before starting work, each goroutine calls `Done()` (usually `defer`), and `Wait()` blocks until the counter reaches zero.

## Plain English

A WaitGroup is a counter: “N workers still outstanding.” You bump it when you spawn work, decrement when each finishes, and block until the counter hits zero. It’s the idiomatic join barrier when you don’t need results over a channel.

## Interviewer Angle

- When `Add`? (before `go`, or with correct delta up front)
- Why `defer wg.Done()`?
- Can you copy a WaitGroup? (no — pass pointer)
- WaitGroup vs channel of results?
- What if `Done` more than `Add`? (negative counter → panic)

## Go Examples

```go
package main

import (
	"fmt"
	"sync"
)

func main() {
	var wg sync.WaitGroup
	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			fmt.Println("worker", id)
		}(i)
	}
	wg.Wait()
	fmt.Println("all done")
}
```

```go
// Collect errors with a channel + WaitGroup
func runAll(tasks []func() error) error {
	errCh := make(chan error, len(tasks))
	var wg sync.WaitGroup
	for _, t := range tasks {
		wg.Add(1)
		go func(fn func() error) {
			defer wg.Done()
			errCh <- fn()
		}(t)
	}
	wg.Wait()
	close(errCh)
	for err := range errCh {
		if err != nil {
			return err // or join all errors
		}
	}
	return nil
}
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| `Add` inside the goroutine | Race: `Wait` may see 0 before `Add` |
| Passing `wg` by value | Copies counter; `Done`/`Wait` on different instances |
| Reusing after `Wait` without care | Allowed if counter returned to 0; don’t race `Add`/`Wait` |
| Using WaitGroup for “N results” | Prefer channel or errgroup for values/errors |
| Forgetting `Done` on early return | Always `defer Done()` |

## Trigger Phrase

> “WaitGroup is a join counter — `Add` before `go`, `defer Done()` inside, never copy the WaitGroup, and `Wait` until zero.”

## Exercise

Implement a bounded parallel map: process a slice with at most `limit` concurrent goroutines using WaitGroup (and optionally a semaphore channel). Return the first error and cancel remaining work via `context`.
