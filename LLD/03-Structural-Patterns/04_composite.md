# Composite

> Compose objects into **tree structures** and treat individual leaves and whole composites **uniformly**.

## Plain English

A file and a folder both support `size()` / `print()`. A folder’s size is the sum of children. Clients call the same API whether the node is a leaf or a branch.

## Why seniors get asked this

File systems, org charts, UI component trees, nested menus — classic LLD. Interviewers watch recursion + uniform interface.

## Real-world analogy

A **box of gifts**: some items are single presents; some are boxes containing more boxes. “Total weight” works the same way for both.

## Example

### Python

```python
from abc import ABC, abstractmethod


class FSNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

    @abstractmethod
    def name(self) -> str: ...


class File(FSNode):
    def __init__(self, name: str, bytes_: int) -> None:
        self._name, self._bytes = name, bytes_

    def size(self) -> int:
        return self._bytes

    def name(self) -> str:
        return self._name


class Folder(FSNode):
    def __init__(self, name: str) -> None:
        self._name = name
        self._children: list[FSNode] = []

    def add(self, node: FSNode) -> None:
        self._children.append(node)

    def size(self) -> int:
        return sum(c.size() for c in self._children)

    def name(self) -> str:
        return self._name


root = Folder("root")
root.add(File("a.txt", 10))
docs = Folder("docs")
docs.add(File("b.pdf", 40))
root.add(docs)
print(root.size())  # 50
```

### Go

```go
type FSNode interface {
    Size() int
    Name() string
}

type File struct {
    name string
    bytes int
}
func (f File) Size() int    { return f.bytes }
func (f File) Name() string { return f.name }

type Folder struct {
    name     string
    children []FSNode
}
func (f *Folder) Add(n FSNode) { f.children = append(f.children, n) }
func (f Folder) Size() int {
    total := 0
    for _, c := range f.children {
        total += c.Size()
    }
    return total
}
func (f Folder) Name() string { return f.name }
```

## When to use

- Part-whole hierarchies where clients ignore leaf vs composite.
- Recursive operations: size, render, validate, search.
- UI trees / nested permissions / expression trees (sometimes with Visitor).

## When not to use / pitfalls

- Flat lists don’t need Composite.
- Forcing *every* method onto the common interface can violate ISP (`add` on `File` is awkward — often only composites expose mutators).
- Deep trees + unbounded recursion → stack risks; mention iterative traversal for huge trees.
- Identity/parent pointers get messy; keep ownership clear.

## Interview trigger phrase

> “Files and folders share one FSNode interface so size() recurses uniformly — Composite.”

## Exercise

Model a **UI**: `Button` (leaf) and `Panel` (can contain children). Both implement `draw()`.

1. Sketch types and how a panel draws children.
2. Should `Button` have `add(child)`? Why/why not?
3. Name one machine-coding problem where Composite is the load-bearing pattern.
