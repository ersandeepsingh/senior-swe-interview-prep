# Test Doubles — Interfaces, Fakes & `httptest`

> Depend on **small interfaces**; in tests, swap in fakes/stubs/mocks — and use **`httptest`** for HTTP handlers/clients.

## Plain English

A test double stands in for a real dependency (DB, email, HTTP). In Go you usually define a narrow interface at the consumer, then provide a real impl in prod and a fake in tests. `net/http/httptest` gives you `ResponseRecorder` and `NewRequest` without opening ports; `httptest.NewServer` spins a real local server for client tests.

## Why interviewers ask ⭐

“How do you test this handler without hitting Stripe?” — answer: interface seams + fakes, not a mocking framework religion.

## Interface + fake

```go
type UserStore interface {
    Find(ctx context.Context, id string) (User, error)
}

type Service struct {
    Store UserStore
}

func (s Service) Email(ctx context.Context, id string) (string, error) {
    u, err := s.Store.Find(ctx, id)
    if err != nil {
        return "", err
    }
    return u.Email, nil
}

// test fake
type memStore map[string]User

func (m memStore) Find(_ context.Context, id string) (User, error) {
    u, ok := m[id]
    if !ok {
        return User{}, ErrNotFound
    }
    return u, nil
}

func TestEmail(t *testing.T) {
    svc := Service{Store: memStore{"1": {Email: "a@b.com"}}}
    got, err := svc.Email(context.Background(), "1")
    if err != nil || got != "a@b.com" {
        t.Fatalf("got %q err %v", got, err)
    }
}
```

## `httptest` for handlers

```go
func TestHelloHandler(t *testing.T) {
    req := httptest.NewRequest(http.MethodGet, "/hello", nil)
    rr := httptest.NewRecorder()
    hello(rr, req)
    if rr.Code != http.StatusOK {
        t.Fatalf("status %d", rr.Code)
    }
    if !strings.Contains(rr.Body.String(), "hello") {
        t.Fatalf("body %s", rr.Body.String())
    }
}
```

## `httptest.Server` for clients

```go
func TestClient(t *testing.T) {
    srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        _, _ = w.Write([]byte(`{"ok":true}`))
    }))
    t.Cleanup(srv.Close)

    res, err := http.Get(srv.URL)
    // assert...
    _ = res
    _ = err
}
```

## Double vocabulary (keep it light)

| Kind | Behavior |
|------|----------|
| Stub | returns canned data |
| Fake | working simplified impl (in-memory DB) |
| Mock | asserts interactions were called (use sparingly) |
| Spy | records calls for assertions |

Prefer fakes over interaction-heavy mocks when possible — less brittle.

## Pitfalls

- Interfaces defined on the provider (“enterprise Java”) instead of the consumer.
- Over-mocking → tests lock onto call order, not behavior.
- Real network in unit tests — flaky CI.
- Forgetting `srv.Close()` / `t.Cleanup`.

## Interview trigger phrase

> “I’d put a small interface on the consumer, inject a fake store in tests, and use `httptest` for handlers and `httptest.Server` for client code.”

## Exercise

Given a `Notifier` that POSTs JSON to a webhook, write a test using `httptest.NewServer` that asserts method, path, and body — and a failure case when the server returns 500.
