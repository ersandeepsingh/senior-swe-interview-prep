# Flyweight

> Share **intrinsic (immutable) state** across many objects so you use far less memory; keep **extrinsic state** outside.

## Plain English

Rendering 100,000 tree sprites: don’t store the same mesh/texture on every instance. Share one `TreeType` (species, texture) and store only per-instance position/health outside. Glyphs in a text editor work the same way.

## Why seniors get asked this

Games, particle systems, text rendering — seniors mention memory and the intrinsic/extrinsic split, not just “caching.”

## Real-world analogy

A **rubber stamp**: one stamp design (shared), many impressions at different positions on the page (extrinsic).

## Example

### Python

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class TreeType:  # intrinsic — shared
    name: str
    color: str
    texture: str

    def draw(self, x: int, y: int) -> None:
        print(f"{self.name}/{self.color} at ({x},{y})")


class TreeFactory:
    _types: dict[tuple[str, str, str], TreeType] = {}

    @classmethod
    def get(cls, name: str, color: str, texture: str) -> TreeType:
        key = (name, color, texture)
        if key not in cls._types:
            cls._types[key] = TreeType(name, color, texture)
        return cls._types[key]


@dataclass
class Tree:  # extrinsic per instance
    x: int
    y: int
    type: TreeType

    def draw(self) -> None:
        self.type.draw(self.x, self.y)


shared = TreeFactory.get("Oak", "green", "oak.png")
forest = [Tree(i, i * 2, shared) for i in range(3)]
for t in forest:
    t.draw()
print("shared types:", len(TreeFactory._types))  # 1
```

### Go

```go
type TreeType struct { // intrinsic
    Name, Color, Texture string
}

func (t TreeType) Draw(x, y int) {
    fmt.Printf("%s/%s at (%d,%d)\n", t.Name, t.Color, x, y)
}

var types = map[string]*TreeType{}

func GetTreeType(name, color, texture string) *TreeType {
    key := name + "|" + color + "|" + texture
    if t, ok := types[key]; ok {
        return t
    }
    t := &TreeType{name, color, texture}
    types[key] = t
    return t
}

type Tree struct { // extrinsic
    X, Y int
    Type *TreeType
}

func (t Tree) Draw() { t.Type.Draw(t.X, t.Y) }
```

## When to use

- Huge numbers of similar objects; intrinsic data dominates memory.
- Intrinsic state is immutable and safely shareable.
- Factory/registry can intern shared flyweights.

## When not to use / pitfalls

- Few objects → complexity without savings.
- Putting **mutable** per-instance data into the shared flyweight → cross-talk bugs.
- Extrinsic state must be passed in or stored externally — easy to forget and “optimize” wrongly.
- Thread safety of the factory cache if concurrent.
- Don’t confuse with object **pool** (reuse lifecycle) vs flyweight (share immutable data).

## Interview trigger phrase

> “I’d flyweight the glyph/typeface data and keep cursor positions extrinsic so we don’t duplicate textures.”

## Exercise

A game has 50,000 bullets that share the same sprite and damage table, but differ in position/velocity.

1. What is intrinsic vs extrinsic?
2. Sketch a factory that interns bullet types.
3. When would an object pool be a better fit than Flyweight?
