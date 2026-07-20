# Idiomatic Go — Simplicity, Small Interfaces, Composition

> Write clear Go: **small interfaces**, composition over inheritance, make the zero value useful, accept interfaces / return structs.

## Plain English

Idiomatic Go prefers boring code that fits the stdlib style. Interfaces are discovered at the consumer (often 1–3 methods). Embedding composes behavior. Packages are focused. Concurrency is structured with clear ownership of data.

## Why interviewers ask 🟡⭐

They watch whether you design like the standard library or like a Java transplant (heavy frameworks, large interfaces, inheritance trees).

## Signature habits

```go
// Accept interfaces, return concrete types
func NewServer(store BlobStore, logger *slog.Logger) *Server { /* ... */ }

// Small interface at consumer
type BlobStore interface {
    Get(ctx context.Context, key string) ([]byte, error)
    Put(ctx context.Context, key string, val []byte) error
}

// Useful zero value
type Counter struct{ n atomic.Int64 }

func (c *Counter) Inc() { c.n.Add(1) }

// Errors are values; early return
func (s *Server) Handle(ctx context.Context, id string) error {
    b, err := s.store.Get(ctx, id)
    if err != nil {
        return fmt.Errorf("get %s: %w", id, err)
    }
    return s.process(b)
}
```

## Composition via embedding

```go
type Reader interface{ Read([]byte) (int, error) }
type Writer interface{ Write([]byte) (int, error) }
type ReadWriter interface {
    Reader
    Writer
}
```

Prefer embedding for interfaces and carefully for structs (promoted methods can surprise).

## Cultural checklist

| Do | Don’t |
|----|-------|
| `gofmt` everything | Fight the formatter |
| Short, clear names | `AbstractManagerFactoryImpl` |
| Few methods per interface | God interfaces |
| Explicit error handling | Hidden panics / exceptions |
| Copy small values | Premature pointer everywhere |

## Pitfalls

- Defining huge provider-side interfaces “for mocking everything.”
- Package names that stutter (`json.JSONDecoder`).
- Clever channel architectures where a mutex would be clearer (and vice versa).
- Ignoring the zero value — forcing awkward constructors for everything.

## Interview trigger phrase

> “I’d keep interfaces small and consumer-defined, return concrete types, compose with embedding, and optimize for readability over abstraction count.”

## Exercise

Refactor a `UserService` that takes a concrete `*sql.DB` and global logger into idiomatic constructor injection with a 2-method store interface — without a DI framework.
