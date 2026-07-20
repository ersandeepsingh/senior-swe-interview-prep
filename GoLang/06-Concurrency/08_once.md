# sync.Once

> `sync.Once` guarantees that a function runs **at most once**, even when called concurrently from many goroutines. Later callers block until the first successful run finishes, then return immediately. Used for lazy, thread-safe initialization.

## Plain English

`Once` is “initialize exactly one time, safely.” The first caller runs your `Do(f)`; everyone else waits for that to finish, then skips `f`. If `f` panics, `Once` still counts as done — subsequent `Do` calls won’t retry.

## Interviewer Angle

- Once vs Mutex + boolean flag?
- What if `Do` panics? (considered done; no retry)
- Singleton pattern in Go?
- Once vs `init()` / package-level init?
- Resetting Once? (you don’t — design for one-shot; or use a new Once)

## Go Examples

```go
var (
	instance *DB
	once     sync.Once
)

func GetDB() *DB {
	once.Do(func() {
		instance = connect() // expensive
	})
	return instance
}
```

```go
// Close exactly once (common for shared resources).
type Conn struct {
	once sync.Once
	c    net.Conn
}

func (c *Conn) Close() error {
	var err error
	c.once.Do(func() {
		err = c.c.Close()
	})
	return err
}
```

```go
// Panic inside Do still marks Once as complete.
var once sync.Once
once.Do(func() { panic("boom") }) // recovers elsewhere or crashes
once.Do(func() { fmt.Println("never runs") })
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| Assuming retry after failure | No retry; handle errors inside `Do` carefully |
| Slow `Do` blocks all waiters | Keep init bounded; or async-init with care |
| Storing Once in copied struct | Same copy problem as Mutex |
| Using Once for “run N times” | Wrong tool — use counter/semaphore |
| Deadlock: `Do` calling something that calls `Do` on same Once | Self-wait forever |

## Trigger Phrase

> “`sync.Once` is for one-shot safe init — first caller runs, others wait, and a panic still counts as done so I handle failures inside `Do`.”

## Exercise

Build a lazy HTTP client singleton shared by the process. Show how you’d surface a connection-setup error to the first caller without leaving later callers with a nil client (hint: store `(*Client, error)` under Once, or use a different pattern if retry is required).
