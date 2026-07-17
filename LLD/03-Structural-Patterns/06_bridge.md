# Bridge

> Decouple an **abstraction** from its **implementation** so both can vary independently.

## Plain English

`Shape` (circle/square) shouldn’t inherit forever with `VectorCircle`, `RasterCircle`, `VectorSquare`… Instead, Shape *has a* `Renderer`. Add a new shape or a new renderer without multiplying classes.

## Why seniors get asked this

Orthogonal dimensions of change (platform × feature, protocol × message type). Seniors spot the Cartesian product explosion and split it with composition — Bridge is that split named.

## Real-world analogy

A **remote control** (abstraction) works with many **TV brands** (implementations). New remote features don’t require a new TV; new TVs don’t rewrite remotes.

## Example

### Python

```python
from abc import ABC, abstractmethod


class Renderer(ABC):
    @abstractmethod
    def draw_circle(self, x: int, y: int, r: int) -> None: ...


class VectorRenderer(Renderer):
    def draw_circle(self, x: int, y: int, r: int) -> None:
        print(f"Vector circle ({x},{y}) r={r}")


class RasterRenderer(Renderer):
    def draw_circle(self, x: int, y: int, r: int) -> None:
        print(f"Raster pixels circle ({x},{y}) r={r}")


class Shape(ABC):
    def __init__(self, renderer: Renderer) -> None:
        self._renderer = renderer

    @abstractmethod
    def draw(self) -> None: ...


class Circle(Shape):
    def __init__(self, renderer: Renderer, x: int, y: int, r: int) -> None:
        super().__init__(renderer)
        self._x, self._y, self._r = x, y, r

    def draw(self) -> None:
        self._renderer.draw_circle(self._x, self._y, self._r)


Circle(VectorRenderer(), 0, 0, 5).draw()
Circle(RasterRenderer(), 0, 0, 5).draw()
```

### Go

```go
type Renderer interface {
    DrawCircle(x, y, r int)
}

type VectorRenderer struct{}
func (VectorRenderer) DrawCircle(x, y, r int) {
    fmt.Printf("Vector circle (%d,%d) r=%d\n", x, y, r)
}

type RasterRenderer struct{}
func (RasterRenderer) DrawCircle(x, y, r int) {
    fmt.Printf("Raster pixels circle (%d,%d) r=%d\n", x, y, r)
}

type Circle struct {
    R Renderer
    X, Y, Radius int
}

func (c Circle) Draw() { c.R.DrawCircle(c.X, c.Y, c.Radius) }
```

## When to use

- Two independent axes of variation (abstraction × implementation).
- You want to share one implementation hierarchy across multiple abstractions.
- Inheritance explosion: `N shapes × M renderers` subclasses.

## When not to use / pitfalls

- Only one implementation forever → Bridge is ceremony.
- Easy to confuse with **Strategy** (swap algorithm) — Bridge is specifically splitting two hierarchies that would otherwise multiply.
- Over-abstracting tiny apps; in interviews, draw the two axes on the board first.
- Indirection cost: more types to navigate.

## Interview trigger phrase

> “Shape and Renderer change independently — I’d Bridge them with composition instead of VectorCircle/RasterSquare subclasses.”

## Exercise

`Notification` can be `Alert` or `Digest`, delivered via `Email` or `SMS`.

1. Sketch Bridge so you don’t create four subclasses.
2. Where is the “abstraction” vs “implementor”?
3. How is this different from Strategy for “pick SMS vs Email”?
