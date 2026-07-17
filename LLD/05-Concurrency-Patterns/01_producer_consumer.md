# Producer–Consumer

> **Decouple** producers and consumers with a **bounded buffer** (queue). Producers block when full; consumers block when empty.

## Plain English

One side makes work; the other does work. They don’t need to run at the same speed — the queue in the middle absorbs bursts. If the queue is **bounded**, a fast producer can’t blow up memory; it waits (backpressure).

## Simple analogy

A restaurant kitchen pass: chefs (producers) plate dishes onto a shelf; waiters (consumers) take them. A small shelf forces chefs to slow down when waiters fall behind.

## Why seniors get asked this

Job queues, log pipelines, BookMyShow seat events, notification dispatch — interviewers want bounded queues, graceful shutdown, and “what if the consumer dies?”

## Good: bounded queue with blocking

### Python

```python
import queue
import threading
import time


def producer(q: queue.Queue[str], stop: threading.Event) -> None:
    for i in range(5):
        if stop.is_set():
            return
        q.put(f"job-{i}")  # blocks when queue is full
        time.sleep(0.01)
    q.put(None)  # poison pill — signals consumer to exit


def consumer(q: queue.Queue[str]) -> None:
    while True:
        item = q.get()  # blocks when empty
        if item is None:
            q.task_done()
            return
        print(f"handled {item}")
        q.task_done()


def main() -> None:
    work: queue.Queue[str] = queue.Queue(maxsize=3)  # bounded
    stop = threading.Event()
    t_prod = threading.Thread(target=producer, args=(work, stop))
    t_cons = threading.Thread(target=consumer, args=(work,))
    t_prod.start()
    t_cons.start()
    t_prod.join()
    work.join()  # wait until all items processed
    t_cons.join()


if __name__ == "__main__":
    main()
```

### Go

```go
package main

import (
    "context"
    "fmt"
    "sync"
)

func main() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    jobs := make(chan string, 3) // bounded buffer
    var wg sync.WaitGroup

    wg.Add(1)
    go func() {
        defer wg.Done()
        defer close(jobs)
        for i := 0; i < 5; i++ {
            select {
            case <-ctx.Done():
                return
            case jobs <- fmt.Sprintf("job-%d", i): // blocks when buffer full
            }
        }
    }()

    wg.Add(1)
    go func() {
        defer wg.Done()
        for job := range jobs {
            fmt.Println("handled", job)
        }
    }()

    wg.Wait()
}
```

## Concurrency safety

| Concern | What to watch |
|---------|----------------|
| **Race** | Don’t share a plain `list` between threads without a lock — use `queue.Queue` or a channel. |
| **Deadlock** | Producer and consumer both waiting on each other with a full/empty queue and no progress — usually a logic bug (e.g. all consumers exited). |
| **Backpressure** | Unbounded queues hide overload until OOM. Bounded queues push slowness upstream. |

**Python GIL:** threads can still race on shared mutable state outside the queue. `queue.Queue` is thread-safe; a raw `list.append` from two threads is not.

## When to use / not use

**Use:** different production and consumption rates; fan-in/fan-out pipelines; job brokers; separating I/O from CPU work.

**Don’t use:** trivial single-threaded scripts; when you need strict ordering with one consumer anyway (a simple loop may suffice); when distributed durability is required (use a real message broker).

## Pitfalls

- Unbounded queue → memory blow-up under load.
- No shutdown signal → hung threads on exit.
- Multiple consumers + poison pill → need one pill per consumer or use `context` cancellation.
- Forgetting `task_done()` / `join()` in Python when tracking completion.

## Interview trigger phrase

> “I’d decouple them with a **bounded blocking queue** so producers back off under load, and I’d add a clear shutdown path.”

## Exercise

Design an in-memory **email dispatch** system: API handlers enqueue `(user_id, template)`; 3 worker threads send email (mock with `print`).

1. What is `maxsize` and why pick 100 vs unbounded?
2. How do you stop workers cleanly on process shutdown?
3. What happens if sending is slower than enqueue for 10 minutes?
