# Dependency Injection — Constructors, Not Frameworks

> Pass dependencies explicitly via **constructors**; no required DI container — interfaces + wiring in `main` suffice.

## Plain English

Instead of globals or service locators, construct types with what they need: `NewService(store Store, clock Clock)`. In tests, pass fakes. In prod, `main` builds the graph once. That’s DI in Go.

## Why interviewers ask

They want testable design without Spring-like magic. Constructor injection is the idiom.

## Example

```go
type Clock interface{ Now() time.Time }

type Store interface {
    Save(ctx context.Context, o Order) error
}

type Service struct {
    store Store
    clock Clock
    log   *slog.Logger
}

func NewService(store Store, clock Clock, log *slog.Logger) *Service {
    if log == nil {
        log = slog.Default()
    }
    return &Service{store: store, clock: clock, log: log}
}

func (s *Service) Place(ctx context.Context, o Order) error {
    o.CreatedAt = s.clock.Now()
    if err := s.store.Save(ctx, o); err != nil {
        return fmt.Errorf("save order: %w", err)
    }
    return nil
}

// main wiring
func main() {
    db := openDB()
    svc := NewService(PostgresStore{db}, realClock{}, slog.Default())
    _ = svc
}
```

## Patterns

| Pattern | Use |
|---------|-----|
| Constructor injection | Default choice |
| Functional options | Optional config (see next topic) |
| Interface in consumer | Test seams |
| Fx / Wire | Large graphs only if team already uses them |

## Pitfalls

- Package-level mutable globals (`var DB *sql.DB`) — hard to test, hidden coupling.
- DIY service locator maps (`container.Get("UserRepo")`).
- Passing `*App` god objects into everything.
- Over-interfacing: concrete `*slog.Logger` is fine to pass.

## Interview trigger phrase

> “I’d wire dependencies in `main` through constructors, depend on small interfaces at the edges I need to fake, and skip a DI framework unless the graph is huge.”

## Exercise

Take a handler that uses global `db` and `http.DefaultClient`. Refactor to constructor-injected `Store` and `*http.Client` with timeouts — show the `main` wiring.
