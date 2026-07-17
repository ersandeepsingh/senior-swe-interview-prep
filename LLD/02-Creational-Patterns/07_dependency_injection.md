# Dependency Injection

> Supply a class’s collaborators **from the outside** (constructor, setter, or container) instead of constructing them internally.

## Plain English

Don’t write `self.repo = PostgresRepo()` inside the service. Accept a `Repo` (ideally an interface) in `__init__` / struct fields. Wiring happens in `main` (or a DI container). That makes tests plug in fakes.

**Related:** Dependency Inversion (DIP) says *depend on abstractions*. DI is *how* you pass the concrete. You can inject concretes without DIP; seniors usually do both at important boundaries.

## Why seniors get asked this

“How do you test this?” “How do you swap implementations?” DI is the practical answer. Machine-coding rewards constructor injection over hidden globals.

## Real-world analogy

A **chef doesn’t grow the vegetables** in the kitchen — ingredients are delivered. Swap farms without rewriting recipes.

## Example

### Python

```python
from abc import ABC, abstractmethod


class UserRepo(ABC):
    @abstractmethod
    def find(self, user_id: str) -> str: ...


class InMemoryUserRepo(UserRepo):
    def __init__(self) -> None:
        self._data = {"u1": "Ada"}

    def find(self, user_id: str) -> str:
        return self._data[user_id]


class UserService:
    def __init__(self, repo: UserRepo) -> None:
        self._repo = repo  # injected

    def greet(self, user_id: str) -> str:
        return f"Hello, {self._repo.find(user_id)}"


# composition root
svc = UserService(InMemoryUserRepo())
print(svc.greet("u1"))
```

### Go

```go
type UserRepo interface {
    Find(userID string) string
}

type InMemoryUserRepo struct {
    data map[string]string
}

func (r InMemoryUserRepo) Find(userID string) string {
    return r.data[userID]
}

type UserService struct {
    Repo UserRepo // injected
}

func (s UserService) Greet(userID string) string {
    return "Hello, " + s.Repo.Find(userID)
}

// main
svc := UserService{Repo: InMemoryUserRepo{data: map[string]string{"u1": "Ada"}}}
fmt.Println(svc.Greet("u1"))
```

## When to use

- Collaborators may change (DB, HTTP client, clock, RNG) or need fakes in tests.
- You want a clear **composition root** (`main`) that wires the graph.
- Avoiding Singleton/globals for services.

## When not to use / pitfalls

- Injecting everything, including pure value helpers → ceremony with no gain.
- Service-locator anti-pattern (`container.Get("X")` everywhere) hides dependencies.
- Constructor with 12 dependencies → the type may have too many responsibilities (SRP).
- Framework magic DI is fine in prod apps; in interviews, **manual constructor injection** is clearer and enough.

## Interview trigger phrase

> “I’d constructor-inject the repository so OrderService doesn’t know Postgres — tests can pass an in-memory fake.”

## Exercise

`CheckoutService` needs a `PaymentGateway`, `Inventory`, and `Notifier`.

1. Show the constructor / struct with three injected deps.
2. How does a unit test charge without hitting a real gateway?
3. One sentence: DI vs DIP — what’s the difference?
