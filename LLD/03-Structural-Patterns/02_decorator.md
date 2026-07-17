# Decorator

> Attach **additional behavior** to an object dynamically by wrapping it, keeping the same interface — without exploding subclasses.

## Plain English

Start with plain coffee; wrap with milk, then sugar. Each wrapper implements the same interface and delegates, adding cost/description. Same idea for streams: compress, encrypt, buffer — stack wrappers.

## Why seniors get asked this

“Add logging / retries / caching around this client” without editing the core class. Interviewers contrast Decorator with deep inheritance trees (`MilkSugarWhipCoffee`).

## Real-world analogy

**Gift wrapping**: the gift is the same object; each layer of wrapping adds presentation without changing what’s inside.

## Example

### Python

```python
from abc import ABC, abstractmethod


class Coffee(ABC):
    @abstractmethod
    def cost(self) -> int: ...

    @abstractmethod
    def desc(self) -> str: ...


class SimpleCoffee(Coffee):
    def cost(self) -> int:
        return 50

    def desc(self) -> str:
        return "coffee"


class Milk(Coffee):
    def __init__(self, inner: Coffee) -> None:
        self._inner = inner

    def cost(self) -> int:
        return self._inner.cost() + 10

    def desc(self) -> str:
        return self._inner.desc() + " + milk"


class Sugar(Coffee):
    def __init__(self, inner: Coffee) -> None:
        self._inner = inner

    def cost(self) -> int:
        return self._inner.cost() + 5

    def desc(self) -> str:
        return self._inner.desc() + " + sugar"


order: Coffee = Sugar(Milk(SimpleCoffee()))
print(order.desc(), order.cost())  # coffee + milk + sugar 65
```

### Go

```go
type Coffee interface {
    Cost() int
    Desc() string
}

type SimpleCoffee struct{}
func (SimpleCoffee) Cost() int    { return 50 }
func (SimpleCoffee) Desc() string { return "coffee" }

type Milk struct{ Inner Coffee }
func (m Milk) Cost() int    { return m.Inner.Cost() + 10 }
func (m Milk) Desc() string { return m.Inner.Desc() + " + milk" }

type Sugar struct{ Inner Coffee }
func (s Sugar) Cost() int    { return s.Inner.Cost() + 5 }
func (s Sugar) Desc() string { return s.Inner.Desc() + " + sugar" }

order := Sugar{Inner: Milk{Inner: SimpleCoffee{}}}
fmt.Println(order.Desc(), order.Cost())
```

## When to use

- Cross-cutting extras: logging, metrics, retries, auth around the same interface.
- Combinations of options would explode if modeled as subclasses.
- You want to compose behavior at runtime / wiring time.

## When not to use / pitfalls

- One fixed enhancement forever → just edit the class or subclass once.
- Order of wrapping can matter (encrypt-then-compress vs reverse) — document it.
- Debugging deep wrapper stacks is harder; keep wrappers thin.
- Don’t confuse with **Proxy** (access control / lazy) or **Adapter** (different interface).

## Interview trigger phrase

> “I’d decorate the HTTP client with retry and logging wrappers so the core client stays unaware.”

## Exercise

You have `DataSource.read() -> bytes`. Product wants optional **compression** and **encryption**.

1. Stack both decorators around a file source.
2. Does wrap order matter? Give one sentence.
3. When would a single `Options` struct beat Decorator?
