# Liskov Substitution Principle (LSP)

> Subtypes must be **usable wherever the base type is expected**, without surprising the caller.

## Plain English

If code works with a `Bird`, it should still work when you pass a `Sparrow`. If `Penguin` breaks “fly,” inheritance lied.

Inheritance means: **I honor the parent’s contract** (preconditions, postconditions, exceptions). Not just “shares some fields.”

## Why seniors get asked this

Classic trap: `Square extends Rectangle`. Also: throwing `NotImplementedError` in overrides, or a subclass that rejects valid parent inputs.

## Bad: Square breaks Rectangle’s contract

Callers of `Rectangle` expect: set width and height independently; area = w × h.

### Python

```python
class Rectangle:
    def __init__(self, w: int, h: int):
        self._w, self._h = w, h

    def set_width(self, w: int) -> None:
        self._w = w

    def set_height(self, h: int) -> None:
        self._h = h

    def area(self) -> int:
        return self._w * self._h


class Square(Rectangle):
    def set_width(self, w: int) -> None:
        self._w = self._h = w  # surprises callers

    def set_height(self, h: int) -> None:
        self._w = self._h = h


def print_area_after_resize(r: Rectangle) -> None:
    r.set_width(5)
    r.set_height(4)
    print(r.area())  # expects 20


print_area_after_resize(Rectangle(1, 1))  # 20 ✓
print_area_after_resize(Square(1, 1))     # 16 ✗ — LSP broken
```

### Go

Go has no class inheritance; LSP shows up via **interfaces**. A type that implements an interface but panics / ignores part of the contract is still an LSP smell.

```go
type Shape interface {
    SetWidth(w int)
    SetHeight(h int)
    Area() int
}

type Rectangle struct{ w, h int }

func (r *Rectangle) SetWidth(w int)  { r.w = w }
func (r *Rectangle) SetHeight(h int) { r.h = h }
func (r *Rectangle) Area() int       { return r.w * r.h }

// "Square" that forces equal sides — breaks callers of Shape
type Square struct{ side int }

func (s *Square) SetWidth(w int)  { s.side = w }
func (s *Square) SetHeight(h int) { s.side = h } // ignores independent height
func (s *Square) Area() int       { return s.side * s.side }

func PrintAreaAfterResize(s Shape) {
    s.SetWidth(5)
    s.SetHeight(4)
    fmt.Println(s.Area()) // Rectangle → 20; Square → 16
}
```

## Good: don’t inherit what you can’t honor

Prefer a shared interface with different shapes, or a single `Rectangle` that happens to be square when `w == h`.

### Python

```python
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def area(self) -> int: ...


class Rectangle(Shape):
    def __init__(self, w: int, h: int):
        self._w, self._h = w, h

    def area(self) -> int:
        return self._w * self._h


class Square(Shape):
    def __init__(self, side: int):
        self._side = side

    def area(self) -> int:
        return self._side * self._side
```

No false “Square is a mutable Rectangle.”

### Go

```go
type AreaShape interface {
    Area() int
}

type Rectangle struct{ W, H int }
func (r Rectangle) Area() int { return r.W * r.H }

type Square struct{ Side int }
func (s Square) Area() int { return s.Side * s.Side }
```

## Interview trigger phrase

> “A subtype shouldn’t strengthen preconditions or weaken postconditions — if `Square` can’t honor `Rectangle`, it shouldn’t be a `Rectangle`.”

## Exercise

You have `Bird` with `fly()`. Someone adds `Penguin(Bird)` that raises “can’t fly.”

1. What’s the LSP violation in one sentence?
2. Redesign with an interface (or two): what methods belong on `Bird` vs `FlyingBird`?
3. Write a tiny Python *or* Go sketch of the fixed types.
