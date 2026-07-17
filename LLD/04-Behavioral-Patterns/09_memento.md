# Memento

> Capture and externalize an object’s **internal state** so it can be restored later, without violating encapsulation.

## Plain English

Take a snapshot of an editor document (or game) and store it in a caretaker/history. Restore rolls back. The memento exposes state only to the originator, not to the world.

## Why seniors get asked this

Undo that restores *data*, save points, transactional rollback of in-memory objects. Contrast with Command-based undo.

## Real-world analogy

A **save point in a game**: you restore the world state without the save file knowing how to play the game.

## Example

### Python

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Memento:
    text: str
    cursor: int


class Editor:
    def __init__(self) -> None:
        self.text = ""
        self.cursor = 0

    def type(self, ch: str) -> None:
        self.text += ch
        self.cursor += 1

    def save(self) -> Memento:
        return Memento(self.text, self.cursor)

    def restore(self, m: Memento) -> None:
        self.text, self.cursor = m.text, m.cursor


class History:
    def __init__(self) -> None:
        self._stack: list[Memento] = []

    def push(self, m: Memento) -> None:
        self._stack.append(m)

    def pop(self) -> Memento | None:
        return self._stack.pop() if self._stack else None


ed, hist = Editor(), History()
ed.type("a")
hist.push(ed.save())
ed.type("b")
ed.restore(hist.pop())
print(ed.text)  # a
```

### Go

```go
type Memento struct {
    text   string
    cursor int
}

type Editor struct {
    Text   string
    Cursor int
}

func (e *Editor) Type(ch string) {
    e.Text += ch
    e.Cursor++
}

func (e Editor) Save() Memento {
    return Memento{text: e.Text, cursor: e.Cursor}
}

func (e *Editor) Restore(m Memento) {
    e.Text, e.Cursor = m.text, m.cursor
}

type History struct{ stack []Memento }

func (h *History) Push(m Memento) { h.stack = append(h.stack, m) }
func (h *History) Pop() (Memento, bool) {
    n := len(h.stack)
    if n == 0 {
        return Memento{}, false
    }
    m := h.stack[n-1]
    h.stack = h.stack[:n-1]
    return m, true
}
```

Strict encapsulation (opaque memento) is nicer in languages with nested/private types; interviews accept a simple snapshot struct.

## When to use

- Undo/restore of complex state where storing full snapshots is acceptable.
- Checkpoints before risky operations.
- You want caretaker (`History`) not to depend on Editor fields.

## When not to use / pitfalls

- Huge state snapshotted every keystroke → memory blowup; use diffs or Command undo.
- Mutable mementos shared across history → corruption; prefer immutable snapshots.
- Leaking memento internals to UI/caretaker breaks encapsulation.
- Don’t confuse with **Command** undo (inverse operations) — pick based on size/complexity of state vs ops.

## Interview trigger phrase

> “I’d snapshot Editor state into a Memento stack for restore — History never peeks inside.”

## Exercise

A form wizard has 4 steps of draft data; Back should restore the previous step.

1. What does each memento contain?
2. When is Command undo better than Memento?
3. How do you stop History from editing the snapshot?
