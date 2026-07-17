# Visitor

> Add **new operations** on a structure of objects without changing the classes of the elements — by double-dispatching through `accept(visitor)`.

## Plain English

You have an AST or a catalog of item types. Instead of stuffing `exportJSON`, `tax`, `prettyPrint` into every node class, put each operation in a Visitor. Elements call `visitor.visitConcrete(self)`.

## Why seniors get asked this

Compilers/ASTs, document object models, tax/price over heterogeneous items. Interviewers check you know the trade-off: easy to add operations, hard to add new element types.

## Real-world analogy

A **building inspector** visits rooms: each room type accepts the inspector; the inspector’s checklist (operation) lives with the inspector, not hard-coded into every room forever.

## Example

### Python

```python
from abc import ABC, abstractmethod


class Item(ABC):
    @abstractmethod
    def accept(self, v: "Visitor") -> None: ...


class Book(Item):
    def __init__(self, price: int) -> None:
        self.price = price

    def accept(self, v: "Visitor") -> None:
        v.visit_book(self)


class Fruit(Item):
    def __init__(self, price: int, weight: int) -> None:
        self.price, self.weight = price, weight

    def accept(self, v: "Visitor") -> None:
        v.visit_fruit(self)


class Visitor(ABC):
    @abstractmethod
    def visit_book(self, b: Book) -> None: ...

    @abstractmethod
    def visit_fruit(self, f: Fruit) -> None: ...


class TaxVisitor(Visitor):
    def __init__(self) -> None:
        self.total = 0

    def visit_book(self, b: Book) -> None:
        self.total += int(b.price * 0.05)

    def visit_fruit(self, f: Fruit) -> None:
        self.total += int(f.price * f.weight * 0.1)


cart: list[Item] = [Book(200), Fruit(40, 2)]
tax = TaxVisitor()
for item in cart:
    item.accept(tax)
print(tax.total)
```

### Go

```go
type Visitor interface {
    VisitBook(*Book)
    VisitFruit(*Fruit)
}

type Item interface{ Accept(Visitor) }

type Book struct{ Price int }
func (b *Book) Accept(v Visitor) { v.VisitBook(b) }

type Fruit struct{ Price, Weight int }
func (f *Fruit) Accept(v Visitor) { v.VisitFruit(f) }

type TaxVisitor struct{ Total int }

func (t *TaxVisitor) VisitBook(b *Book) {
    t.Total += int(float64(b.Price) * 0.05)
}
func (t *TaxVisitor) VisitFruit(f *Fruit) {
    t.Total += int(float64(f.Price*f.Weight) * 0.1)
}
```

## When to use

- Object structure is stable; you frequently add *operations*.
- Related behavior should live together (all tax rules in one visitor).
- ASTs / heterogeneous graphs need many passes (typecheck, emit, format).

## When not to use / pitfalls

- Adding new element types forces updating **every** visitor — painful.
- Overkill for one operation on two types — use a simple interface method.
- Breaks encapsulation if visitors need many private fields — may indicate wrong design.
- In Go/Python, type switches sometimes replace classic Visitor; say the trade-off.

## Interview trigger phrase

> “Element types are stable but operations grow — I’d use Visitor so tax/export don’t bloat every node class.”

## Exercise

AST nodes: `Number`, `Add`, `Multiply`. Add an `EvalVisitor` and a `PrintVisitor`.

1. What methods does `Visitor` need?
2. What hurts if you later add `Divide`?
3. When prefer methods on the nodes instead?
