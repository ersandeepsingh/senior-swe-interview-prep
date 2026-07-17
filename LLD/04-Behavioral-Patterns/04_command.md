# Command

> Encapsulate a request as an **object** — parameterize clients with different requests, queue them, and support undo.

## Plain English

Instead of calling `light.on()` directly from a button, wrap the action in a `Command` with `execute()` / `undo()`. Buttons, queues, and macros all hold commands without knowing the receiver details.

## Why seniors get asked this

Undo/redo editors, job queues, remote controls, transactional operations. Seniors mention storing history and reversibility.

## Real-world analogy

A **restaurant order ticket**: the waiter writes the request; the kitchen executes it later. The ticket is the command — separable from who cooks.

## Example

### Python

```python
from abc import ABC, abstractmethod


class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def undo(self) -> None: ...


class Light:
    def __init__(self) -> None:
        self.on = False

    def turn_on(self) -> None:
        self.on = True
        print("light on")

    def turn_off(self) -> None:
        self.on = False
        print("light off")


class LightOnCommand(Command):
    def __init__(self, light: Light) -> None:
        self._light = light

    def execute(self) -> None:
        self._light.turn_on()

    def undo(self) -> None:
        self._light.turn_off()


class Remote:
    def __init__(self) -> None:
        self._history: list[Command] = []

    def press(self, cmd: Command) -> None:
        cmd.execute()
        self._history.append(cmd)

    def undo_last(self) -> None:
        if self._history:
            self._history.pop().undo()


light = Light()
remote = Remote()
remote.press(LightOnCommand(light))
remote.undo_last()
```

### Go

```go
type Command interface {
    Execute()
    Undo()
}

type Light struct{ On bool }
func (l *Light) TurnOn()  { l.On = true; fmt.Println("light on") }
func (l *Light) TurnOff() { l.On = false; fmt.Println("light off") }

type LightOnCommand struct{ Light *Light }
func (c LightOnCommand) Execute() { c.Light.TurnOn() }
func (c LightOnCommand) Undo()    { c.Light.TurnOff() }

type Remote struct{ history []Command }

func (r *Remote) Press(cmd Command) {
    cmd.Execute()
    r.history = append(r.history, cmd)
}

func (r *Remote) UndoLast() {
    if n := len(r.history); n > 0 {
        r.history[n-1].Undo()
        r.history = r.history[:n-1]
    }
}
```

## When to use

- Undo/redo or macro (composite) commands.
- Decouple invoker (UI/button/queue) from receiver.
- Schedule, retry, or log operations as first-class objects.

## When not to use / pitfalls

- Simple direct calls don’t need Command objects.
- Undo that isn’t a true inverse (partial side effects) — be honest about limitations.
- Explosion of tiny command classes; sometimes lambdas/closures are enough.
- Don’t confuse with **Memento** (snapshot state) — Command often *replays/inverses* operations; Memento *restores* data.

## Interview trigger phrase

> “Each edit is a Command with execute/undo so the editor can keep a history stack.”

## Exercise

Text editor supports insert text and delete selection, with undo.

1. Sketch two command types and the history stack.
2. What does `undo` need to store for insert?
3. Command vs Memento — when pick which?
