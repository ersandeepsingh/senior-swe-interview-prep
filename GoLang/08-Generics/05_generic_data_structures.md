# Generic Data Structures

> Classic interview exercise: implement type-safe **containers** with generics — stack, queue, set, linked list, optional/result — using appropriate constraints (`comparable` for sets/maps). Focus on clear APIs, zero values, and concurrency policy (usually: not safe by default).

## Plain English

A generic data structure is a struct parameterized by element type. The compiler enforces that a `Stack[int]` can’t push a `string`. You still design methods, complexity, and whether callers must synchronize.

## Interviewer Angle

- Zero value usefulness? (`var s Stack[int]` empty)
- Why `comparable` for `Set`?
- Growth strategy for underlying slice?
- Thread safety? (document “not concurrent”; or embed mutex)
- Iterator style in Go? (callback, channel, `range` over slice snapshot, `iter` in newer Go)

## Go Examples

### Stack

```go
type Stack[T any] struct {
	items []T
}

func (s *Stack[T]) Push(v T) {
	s.items = append(s.items, v)
}

func (s *Stack[T]) Pop() (T, bool) {
	var zero T
	if len(s.items) == 0 {
		return zero, false
	}
	i := len(s.items) - 1
	v := s.items[i]
	s.items = s.items[:i]
	return v, true
}

func (s *Stack[T]) Len() int { return len(s.items) }
```

### Set

```go
type Set[T comparable] struct {
	m map[T]struct{}
}

func NewSet[T comparable]() *Set[T] {
	return &Set[T]{m: make(map[T]struct{})}
}

func (s *Set[T]) Add(v T) { s.m[v] = struct{}{} }

func (s *Set[T]) Has(v T) bool {
	_, ok := s.m[v]
	return ok
}

func (s *Set[T]) Remove(v T) { delete(s.m, v) }
```

### Singly linked list

```go
type node[T any] struct {
	val  T
	next *node[T]
}

type List[T any] struct {
	head, tail *node[T]
	len        int
}

func (l *List[T]) Append(v T) {
	n := &node[T]{val: v}
	if l.tail == nil {
		l.head, l.tail = n, n
	} else {
		l.tail.next = n
		l.tail = n
	}
	l.len++
}
```

### Optional

```go
type Option[T any] struct {
	ok  bool
	val T
}

func Some[T any](v T) Option[T] { return Option[T]{ok: true, val: v} }
func None[T any]() Option[T]    { return Option[T]{} }

func (o Option[T]) Get() (T, bool) { return o.val, o.ok }
```

## Gotchas

| Gotcha | Detail |
|--------|--------|
| Forgetting pointer receivers | `Push` on value won’t mutate caller’s stack |
| Set without `comparable` | Won’t compile |
| Returning pointers into internals | Escape / mutation surprises |
| Claiming concurrency-safe | Maps/slices underneath aren’t |
| Overbuilding (full Java collections) | Interview wants clarity, not a library |

## Trigger Phrase

> “I’d implement a generic stack/set with clear zero-value behavior — `comparable` for sets — and document that it’s not concurrency-safe unless I add a mutex.”

## Exercise

Implement `Queue[T any]` with `Enqueue`, `Dequeue`, `Len` using a slice or two stacks. Then write a table-driven test for FIFO order and empty-dequeue behavior. Stretch: add `Set[T comparable]` intersection `func Intersect[T comparable](a, b *Set[T]) *Set[T]`.
