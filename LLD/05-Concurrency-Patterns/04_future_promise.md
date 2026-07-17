# Future / Promise

> A **placeholder** for a result that will arrive later — submit async work, continue, then **join** (block or callback) when ready.

## Plain English

You order food and get a buzzer (the Future). You don’t stand at the counter; when it vibrates, you pick up the meal (the result). “Promise” is the same idea: a commitment to deliver a value or error later.

## Simple analogy

Restaurant pager: you get a token now; the meal finishes in the kitchen; you exchange the pager for food when it buzzes.

## Why seniors get asked this

Parallel fan-out (fetch 10 URLs), payment + inventory + fraud checks, aggregating microservice calls — seniors discuss timeouts, cancellation, and error propagation.

## Good: fan-out then join

### Python

```python
from concurrent.futures import ThreadPoolExecutor, wait, TimeoutError


def fetch_price(sku: str) -> int:
    # mock I/O
    return hash(sku) % 1000


def quote_cart(skus: list[str], timeout_sec: float = 2.0) -> dict[str, int]:
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fetch_price, sku): sku for sku in skus}
        done, not_done = wait(futures.keys(), timeout=timeout_sec)

        if not_done:
            for fut in not_done:
                fut.cancel()
            raise TimeoutError(f"{len(not_done)} price lookups timed out")

        return {futures[fut]: fut.result() for fut in done}


if __name__ == "__main__":
    print(quote_cart(["A", "B", "C", "D"]))
```

For async I/O-heavy code, `asyncio` tasks are the idiomatic Future-like model in modern Python.

### Go

```go
package main

import (
    "context"
    "fmt"
    "sync"
    "time"
)

func fetchPrice(ctx context.Context, sku string) (int, error) {
    select {
    case <-ctx.Done():
        return 0, ctx.Err()
    case <-time.After(10 * time.Millisecond): // mock I/O
        return len(sku) * 100, nil
    }
}

func quoteCart(ctx context.Context, skus []string) (map[string]int, error) {
    ctx, cancel := context.WithTimeout(ctx, 2*time.Second)
    defer cancel()

    type result struct {
        sku   string
        price int
        err   error
    }

    ch := make(chan result, len(skus))
    var wg sync.WaitGroup
    for _, sku := range skus {
        wg.Add(1)
        go func(s string) {
            defer wg.Done()
            p, err := fetchPrice(ctx, s)
            ch <- result{sku: s, price: p, err: err}
        }(sku)
    }
    go func() {
        wg.Wait()
        close(ch)
    }()

    out := make(map[string]int, len(skus))
    for r := range ch {
        if r.err != nil {
            return nil, r.err
        }
        out[r.sku] = r.price
    }
    return out, nil
}

func main() {
    prices, err := quoteCart(context.Background(), []string{"A", "B", "C"})
    fmt.Println(prices, err)
}
```

## Concurrency safety

| Concern | What to watch |
|---------|----------------|
| **Race** | Aggregating results into a shared map from callbacks without sync — use per-future results then merge, or channels. |
| **Deadlock** | Waiting on `future.result()` inside a thread-pool worker that must run the same task (nested wait on saturated pool). |
| **Cancellation** | Python `Future.cancel()` only works if the task hasn’t started; Go needs `context` passed into the work. |

**Python GIL:** Futures coordinate threads; they don’t fix races in shared mutable state your callbacks touch.

## When to use / not use

**Use:** parallel independent I/O; overlapping latency; “start all, wait for all” (barrier-style join).

**Don’t use:** trivial sequential code; when streaming results as they arrive is enough (use channels/generators); when you need durable workflow orchestration (use a job system).

## Pitfalls

- No timeout → one slow call blocks the whole join.
- Ignoring exceptions until the end — log and fail fast where possible.
- Blocking `result()` on the event loop thread in async Python — use `await` instead.
- Goroutine leak if parent never reads from channel and doesn’t cancel children.

## Interview trigger phrase

> “I’d **fan out** the lookups as Futures, set a **timeout**, cancel stragglers, and merge results — fail the quote if any leg fails.”

## Exercise

Checkout needs **inventory check**, **fraud score**, and **tax quote** in parallel (mock each 200ms).

1. Sketch the Future/async flow and join point.
2. Fraud service is down — partial success or fail entire checkout?
3. How do you enforce a 500ms SLA across all three?
