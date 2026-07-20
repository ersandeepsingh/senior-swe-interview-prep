# sync.Cond

> `sync.Cond` is a **condition variable**: goroutines wait for a condition to become true, and other goroutines signal when the condition may have changed. It always wraps a `Locker` (usually `*Mutex` or `*RWMutex`). Prefer channels/`context` unless you need fine-grained shared-state waiting.

## Plain English

Sometimes you hold a mutex and need to wait until “queue not empty” or “space available.” Busy-looping under the lock is wasteful. `Cond` lets you `Wait()` (atomically unlock + sleep) until `Signal`/`Broadcast` wakes you; then you re-check the condition (spurious wakeups / races).

Rare in modern Go APIs — channels often replace Cond — but seniors should know it for classic monitor-style designs and interview depth.

## Interviewer Angle

- Why re-check the condition in a loop after `Wait`?
- `Signal` vs `Broadcast`?
- Cond vs channel of struct{}?
- What does `Wait` do to the lock? (Unlock, park, re-Lock on wake)

## Go Examples

```go
type Queue struct {
	mu    sync.Mutex
	cond  *sync.Cond
	items []int
}

func NewQueue() *Queue {
	q := &Queue{}
	q.cond = sync.NewCond(&q.mu)
	return q
}

func (q *Queue) Push(v int) {
	q.mu.Lock()
	q.items = append(q.items, v)
	q.mu.Unlock()
	q.cond.Signal() // wake one waiter
}

func (q *Queue) Pop() int {
	q.mu.Lock()
	defer q.mu.Unlock()
	for len(q.items) == 0 { // loop: condition may still be false
		q.cond.Wait() // unlocks mu while waiting; re-locks before return
	}
	v := q.items[0]
	q.items = q.items[1:]
	return v
}
```

```go
// Broadcast when many waiters must re-evaluate (e.g. close/shutdown).
func (q *Queue) Close() {
	q.mu.Lock()
	q.closed = true
	q.mu.Unlock()
	q.cond.Broadcast()
}
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| `if` instead of `for` around `Wait` | Spurious wakeups / stolen signal → bug |
| Calling `Wait` without holding the lock | Undefined / panic |
| Forgetting Broadcast on shutdown | Waiters hang forever |
| Preferring Cond by default | Channels/`errgroup`/`context` are clearer for most Go code |
| Copying Cond | Don’t |

## Trigger Phrase

> “`Cond` is a monitor-style wait/signal on shared state — always `Wait` in a `for` loop under the lock; I’d reach for channels first unless I’m implementing a classic bounded buffer.”

## Exercise

Implement a bounded buffer (capacity N) with `Put`/`Get` using `sync.Cond` (two conditions or one Cond + Broadcast). Then sketch the same API with channels and compare readability and cancellation story.
