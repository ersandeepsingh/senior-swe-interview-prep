# Text Editor / Undo-Redo

> Edit ops with history → **Command + Memento**. 🟡

## Scope / Requirements

**In scope**
- Document buffer; insert/delete at cursor or index.
- Undo / redo stacks.
- Clear redo on new edit after undo (standard editor behavior).

**Out of scope**
- Full collaborative CRDT, rich text, GUI, persistent file formats.

**Domain invariants**
- Each successful edit pushes an inverse (or memento) onto undo stack; redo cleared.
- Undo pops last edit, applies inverse, pushes onto redo.
- Redo reapplies; cursor/content stay consistent with op bounds.
- Document indices valid: `0 <= i <= len(text)` for insert; delete length must fit.

## Core Entities & Responsibilities

| Entity | Responsibility |
|--------|----------------|
| `Document` | Mutable text buffer. |
| `Command` | `execute` / `undo`. |
| `InsertCommand` / `DeleteCommand` | Concrete edits. |
| `History` / `Editor` | Undo/redo stacks; invoke commands. |
| `Memento` (alt) | Snapshot of full state — simpler but heavier. |

## Key Interfaces / Patterns

- **Command:** encapsulate edit + inverse — preferred for large docs.
- **Memento:** snapshot before change — OK for small buffers; discuss trade-off.
- Often both mentioned: memento for selection state, command for text ops.

## End-to-End Flow

1. `insert(0, "Hi")` → doc=`Hi`; undo stack=[Insert].
2. `insert(2, "!")` → `Hi!`.
3. `undo()` → `Hi`; redo has Insert `!`.
4. New `delete` → redo cleared.

## Python Skeleton

```python
from __future__ import annotations
from abc import ABC, abstractmethod


class Document:
    def __init__(self, text: str = ""):
        self.text = text

    def insert(self, i: int, s: str) -> None:
        if not 0 <= i <= len(self.text):
            raise IndexError("cursor")
        self.text = self.text[:i] + s + self.text[i:]

    def delete(self, i: int, length: int) -> str:
        if length < 0 or i < 0 or i + length > len(self.text):
            raise IndexError("range")
        removed = self.text[i : i + length]
        self.text = self.text[:i] + self.text[i + length :]
        return removed


class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...
    @abstractmethod
    def undo(self) -> None: ...


class InsertCommand(Command):
    def __init__(self, doc: Document, index: int, text: str):
        self.doc = doc
        self.index = index
        self.text = text

    def execute(self) -> None:
        self.doc.insert(self.index, self.text)

    def undo(self) -> None:
        self.doc.delete(self.index, len(self.text))


class DeleteCommand(Command):
    def __init__(self, doc: Document, index: int, length: int):
        self.doc = doc
        self.index = index
        self.length = length
        self.removed = ""

    def execute(self) -> None:
        self.removed = self.doc.delete(self.index, self.length)

    def undo(self) -> None:
        self.doc.insert(self.index, self.removed)


class Editor:
    def __init__(self):
        self.doc = Document()
        self.undo_stack: list[Command] = []
        self.redo_stack: list[Command] = []

    def apply(self, cmd: Command) -> None:
        cmd.execute()
        self.undo_stack.append(cmd)
        self.redo_stack.clear()

    def insert(self, index: int, text: str) -> None:
        self.apply(InsertCommand(self.doc, index, text))

    def delete(self, index: int, length: int) -> None:
        self.apply(DeleteCommand(self.doc, index, length))

    def undo(self) -> None:
        if not self.undo_stack:
            return
        cmd = self.undo_stack.pop()
        cmd.undo()
        self.redo_stack.append(cmd)

    def redo(self) -> None:
        if not self.redo_stack:
            return
        cmd = self.redo_stack.pop()
        cmd.execute()
        self.undo_stack.append(cmd)


# --- Memento alternative (snapshot) ---
class Memento:
    def __init__(self, text: str):
        self.text = text


class MementoEditor:
    def __init__(self):
        self.text = ""
        self.undo_stack: list[Memento] = []
        self.redo_stack: list[Memento] = []

    def _snapshot(self) -> None:
        self.undo_stack.append(Memento(self.text))
        self.redo_stack.clear()

    def insert(self, i: int, s: str) -> None:
        self._snapshot()
        self.text = self.text[:i] + s + self.text[i:]

    def undo(self) -> None:
        if not self.undo_stack:
            return
        self.redo_stack.append(Memento(self.text))
        self.text = self.undo_stack.pop().text
```

## Go Skeleton

```go
package editor

type Document struct{ Text string }

func (d *Document) Insert(i int, s string) {
    d.Text = d.Text[:i] + s + d.Text[i:]
}

func (d *Document) Delete(i, n int) string {
    removed := d.Text[i : i+n]
    d.Text = d.Text[:i] + d.Text[i+n:]
    return removed
}

type Command interface {
    Execute()
    Undo()
}

type InsertCmd struct {
    Doc        *Document
    Index      int
    Text       string
}

func (c *InsertCmd) Execute() { c.Doc.Insert(c.Index, c.Text) }
func (c *InsertCmd) Undo()    { c.Doc.Delete(c.Index, len(c.Text)) }

type DeleteCmd struct {
    Doc     *Document
    Index   int
    Length  int
    Removed string
}

func (c *DeleteCmd) Execute() { c.Removed = c.Doc.Delete(c.Index, c.Length) }
func (c *DeleteCmd) Undo()    { c.Doc.Insert(c.Index, c.Removed) }

type Editor struct {
    Doc   *Document
    UndoS []Command
    RedoS []Command
}

func NewEditor() *Editor {
    return &Editor{Doc: &Document{}}
}

func (e *Editor) Apply(cmd Command) {
    cmd.Execute()
    e.UndoS = append(e.UndoS, cmd)
    e.RedoS = nil
}

func (e *Editor) Undo() {
    if len(e.UndoS) == 0 {
        return
    }
    cmd := e.UndoS[len(e.UndoS)-1]
    e.UndoS = e.UndoS[:len(e.UndoS)-1]
    cmd.Undo()
    e.RedoS = append(e.RedoS, cmd)
}

func (e *Editor) Redo() {
    if len(e.RedoS) == 0 {
        return
    }
    cmd := e.RedoS[len(e.RedoS)-1]
    e.RedoS = e.RedoS[:len(e.RedoS)-1]
    cmd.Execute()
    e.UndoS = append(e.UndoS, cmd)
}
```

## Concurrency / Consistency

- Single-threaded document edits; collaborative editing needs OT/CRDT (say so if asked).
- History stacks are not shared across users without merging semantics.

## Extensions / Trade-offs / Pitfalls

- Macro commands (multi-edit transaction = composite Command).
- Cap undo history size.
- Pitfall: mutating command fields after execute; pitfall: not clearing redo.
- Memento memory blow-up on large files vs command inverse.

## Interview Discussion Points

- Command vs Memento — when each wins?
- How do you undo a replace operation?
- Cursor as part of memento vs derived?

## Exercise

Type `Hi`, undo, redo, then delete `H` and show redo is cleared on new edit.

**Follow-ups**
1. Implement `ReplaceCommand`.
2. Batch consecutive inserts into one undo step (editor UX).
3. Explain why CRDTs appear when two users edit concurrently.
