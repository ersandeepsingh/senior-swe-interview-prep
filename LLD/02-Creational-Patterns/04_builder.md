# Builder

> Construct a complex object **step by step**, separating construction from the final representation.

## Plain English

Objects with many optional fields get ugly constructors (`Pizza(size, cheese, pepperoni, olives, …)`). Builder lets you set only what you need, in a readable chain, then `build()` once with validation.

## Why seniors get asked this

`HttpRequest`, query objects, game characters with optional gear — interviewers like fluent builders that stay immutable at the end and fail fast on invalid combos.

## Real-world analogy

Ordering a **custom sandwich**: bread → protein → toppings → sauce, then “make it” — you don’t pass twenty args to the cashier in one breath.

## Example

### Python

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Pizza:
    size: str
    cheese: bool
    pepperoni: bool
    olives: bool


class PizzaBuilder:
    def __init__(self) -> None:
        self._size = "M"
        self._cheese = False
        self._pepperoni = False
        self._olives = False

    def size(self, size: str) -> "PizzaBuilder":
        self._size = size
        return self

    def add_cheese(self) -> "PizzaBuilder":
        self._cheese = True
        return self

    def add_pepperoni(self) -> "PizzaBuilder":
        self._pepperoni = True
        return self

    def add_olives(self) -> "PizzaBuilder":
        self._olives = True
        return self

    def build(self) -> Pizza:
        if self._size not in {"S", "M", "L"}:
            raise ValueError("bad size")
        return Pizza(self._size, self._cheese, self._pepperoni, self._olives)


pizza = PizzaBuilder().size("L").add_cheese().add_olives().build()
```

### Go

```go
type Pizza struct {
    Size      string
    Cheese    bool
    Pepperoni bool
    Olives    bool
}

type PizzaBuilder struct {
    size      string
    cheese    bool
    pepperoni bool
    olives    bool
}

func NewPizzaBuilder() *PizzaBuilder {
    return &PizzaBuilder{size: "M"}
}

func (b *PizzaBuilder) Size(s string) *PizzaBuilder { b.size = s; return b }
func (b *PizzaBuilder) AddCheese() *PizzaBuilder    { b.cheese = true; return b }
func (b *PizzaBuilder) AddPepperoni() *PizzaBuilder { b.pepperoni = true; return b }
func (b *PizzaBuilder) AddOlives() *PizzaBuilder    { b.olives = true; return b }

func (b *PizzaBuilder) Build() (Pizza, error) {
    if b.size != "S" && b.size != "M" && b.size != "L" {
        return Pizza{}, fmt.Errorf("bad size")
    }
    return Pizza{b.size, b.cheese, b.pepperoni, b.olives}, nil
}
```

## When to use

- Many optional / defaulted fields; telescoping constructors hurt readability.
- Construction needs validation or multi-step assembly before the object is usable.
- You want an immutable finished object (build once, then freeze).

## When not to use / pitfalls

- 2–3 required fields → a normal constructor / struct literal is clearer.
- Mutable builder reused after `build()` without reset → subtle bugs; document one-shot use.
- Don’t confuse with **Factory** (which *type*) vs Builder (which *configuration of one type*).
- In Go, functional options (`WithTimeout(...)`) are often preferred over classic builders — say that trade-off.

## Interview trigger phrase

> “This type has too many optional parts — I’d use a Builder (or functional options) so construction stays readable and validated.”

## Exercise

Model an **HTTP request**: method, URL (required), headers, query params, body, timeout (optional).

1. Sketch a builder API for the happy path with two headers and a timeout.
2. Where do you validate “URL required”?
3. Name one alternative to Builder in Go.
