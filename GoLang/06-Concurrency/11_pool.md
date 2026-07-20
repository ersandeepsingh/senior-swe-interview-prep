# sync.Pool

> `sync.Pool` is a concurrent pool of temporary objects that can be reused to reduce allocation and GC pressure. Objects may be removed automatically between GCs — **never** store critical state only in a Pool. Get may return a new object via `New` if empty.

## Plain English

Pool = “borrow a scratch buffer, use it, put it back.” Under load, you avoid allocating a fresh `[]byte` or struct every request. The runtime can throw pooled items away when GC runs, so treat Get as “maybe recycled, maybe new,” and always reset objects before reuse.

## Interviewer Angle

- When is Pool appropriate? (hot path allocs, similar-sized temps)
- Why can’t Pool be a free cache of important data? (GC may drop items)
- Get/Put contract? (caller owns after Get; must not use after Put)
- Pool vs your own channel of buffers?
- Interaction with GC / GOGC?

## Go Examples

```go
var bufPool = sync.Pool{
	New: func() any {
		b := make([]byte, 0, 4096)
		return &b
	},
}

func handle(w io.Writer, data []byte) error {
	bp := bufPool.Get().(*[]byte)
	buf := (*bp)[:0]
	defer func() {
		// Avoid retaining huge buffers forever.
		if cap(buf) > 64*1024 {
			return // drop on floor; don't Put oversized
		}
		*bp = buf
		bufPool.Put(bp)
	}()

	buf = append(buf, data...)
	_, err := w.Write(buf)
	return err
}
```

```go
// encoding/json and fmt use pools internally for similar reasons.
// Don't Put nil; don't Put an object still referenced elsewhere.
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| Assuming Put items survive GC | They may not |
| Putting oversized buffers | Retains huge caps; size-check before Put |
| Using without reset | Stale data leaks across requests (security bug) |
| Pool for connection pools | Wrong — use dedicated lifecycle management |
| Contended Pool as silver bullet | Profile first; sometimes a per-P design or just allocate |

## Trigger Phrase

> “`sync.Pool` recycles throwaway objects to cut GC — Get may allocate, GC may drop items, and I always reset and size-cap before Put.”

## Exercise

Optimize a handler that allocates a `bytes.Buffer` per request using `sync.Pool`. Show reset/`Truncate(0)` on Get, and a policy that discards buffers whose `Cap()` exceeds a threshold so memory doesn’t ratchet up after rare large requests.
