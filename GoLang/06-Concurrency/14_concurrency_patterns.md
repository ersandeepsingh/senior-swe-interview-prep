# Concurrency Patterns

> Recurring **concurrency patterns** in Go: worker pools, fan-out/fan-in, pipelines, semaphores, rate limiting, and or-done/cancellation wrappers. Interviews often ask you to implement one cleanly with exit paths and no leaks.

## Plain English

Patterns are recipes for structuring goroutines and channels:

| Pattern | Idea |
|---------|------|
| **Worker pool** | Fixed N workers pull from a job channel |
| **Fan-out** | One input → many workers in parallel |
| **Fan-in** | Many producers → one merged channel |
| **Pipeline** | Stage1 → stage2 → stage3 via channels |
| **Semaphore** | Bound concurrency (buffered chan of tokens) |
| **Rate limit** | Token bucket / `golang.org/x/time/rate` |
| **Or-done** | Wrap a channel so cancel stops reading |

## Interviewer Angle

- How do you bound concurrency?
- Who closes which channel?
- How does cancellation propagate?
- Backpressure? (blocking sends / bounded buffers)
- Error handling across workers? (`errgroup`)

## Go Examples

### Worker pool

```go
func RunPool(ctx context.Context, jobs <-chan Job, n int, fn func(context.Context, Job) error) error {
	g, ctx := errgroup.WithContext(ctx)
	for i := 0; i < n; i++ {
		g.Go(func() error {
			for {
				select {
				case <-ctx.Done():
					return ctx.Err()
				case job, ok := <-jobs:
					if !ok {
						return nil
					}
					if err := fn(ctx, job); err != nil {
						return err
					}
				}
			}
		})
	}
	return g.Wait()
}
```

### Fan-in

```go
func Merge(ctx context.Context, channels ...<-chan int) <-chan int {
	out := make(chan int)
	var wg sync.WaitGroup
	for _, ch := range channels {
		wg.Add(1)
		go func(c <-chan int) {
			defer wg.Done()
			for {
				select {
				case <-ctx.Done():
					return
				case v, ok := <-c:
					if !ok {
						return
					}
					select {
					case out <- v:
					case <-ctx.Done():
						return
					}
				}
			}
		}(ch)
	}
	go func() {
		wg.Wait()
		close(out)
	}()
	return out
}
```

### Semaphore (limit 10)

```go
sem := make(chan struct{}, 10)
for _, item := range items {
	sem <- struct{}{}
	go func(it Item) {
		defer func() { <-sem }()
		process(it)
	}(item)
}
// still need WaitGroup to join
```

### Pipeline stage

```go
func square(ctx context.Context, in <-chan int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for v := range in {
			select {
			case <-ctx.Done():
				return
			case out <- v * v:
			}
		}
	}()
	return out
}
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| Closing channels multiple writers own | Only one closer; fan-in needs WaitGroup then close |
| Unbounded fan-out | Exhausts memory/FDs — bound with semaphore/pool |
| Ignoring backpressure | Huge buffers hide overload until OOM |
| Pattern without cancel | Leaks on client disconnect |
| Reinventing errgroup poorly | Use `golang.org/x/sync/errgroup` |

## Trigger Phrase

> “I’d pick a worker pool or semaphore to bound concurrency, fan-in with a single closer after WaitGroup, and thread `ctx` through every stage so cancel can’t leak.”

## Exercise

Build a pipeline: generate numbers → filter primes → square → collect. Cap intermediate concurrency, support cancel, and return the first error. Discuss channel buffer sizes and who closes what.
