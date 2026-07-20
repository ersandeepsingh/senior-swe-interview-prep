# Accept Interfaces, Return Structs

> Idiomatic Go APIs **depend on interfaces** (what you need) but **return concrete types** (what you provide). That keeps callers flexible for injection/testing while keeping your package free to evolve fields and extra methods without bloating the returned interface.

## Plain English

```go
// Good shape
func NewServer(store UserStore) *Server  // accept interface, return *Server
```

Callers pass any `UserStore`. You return `*Server` so callers see useful methods and you can add methods later without breaking interface contracts you never promised.

Returning interfaces is sometimes OK (e.g. `io.Reader` from a factory hiding the concrete buffer), but default to concrete returns. Don’t return interfaces just to “hide” the struct — unexported fields already hide internals.

## Interviewer Angle

- Why not always return interfaces?
- Where are interfaces defined? (consumer)
- Testing with fakes/mocks?
- When *should* you return an interface?

## Go Examples

```go
// store.go — concrete
type PostgresStore struct{ db *sql.DB }

func (p *PostgresStore) Save(u User) error { /* ... */ return nil }

// api.go — consumer defines what it needs
type UserStore interface {
	Save(u User) error
}

type Server struct {
	store UserStore
}

func NewServer(store UserStore) *Server {
	return &Server{store: store}
}

func (s *Server) Create(u User) error {
	return s.store.Save(u)
}
```

```go
// Test injects fake
type fakeStore struct{ saved []User }

func (f *fakeStore) Save(u User) error {
	f.saved = append(f.saved, u)
	return nil
}
```

## Bad vs Good

```go
// Bad: accept concrete, hard to test
func NewServer(store *PostgresStore) *Server

// Bad: return fat interface from New
func NewServer() UserServer // huge interface — every method becomes API surface

// Good
func NewServer(store UserStore) *Server
```

## Trigger Phrase

> “Accept interfaces at boundaries for flexibility; return concrete structs so I don’t freeze a wide API. Interfaces live with the consumer.”

## Exercise

Refactor a function `func Backup(db *sql.DB)` that calls `Query`/`Close` into one that accepts the smallest interface needed (hint: look at what methods you actually call), and return a concrete `BackupResult` struct.
