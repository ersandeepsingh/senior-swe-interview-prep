# Abstract Factory

> Provide an interface for creating **families of related objects** without specifying their concrete classes.

## Plain English

Not one product — a *matching set*. Mac UI needs Mac buttons + Mac checkboxes; Windows needs Windows widgets. Abstract Factory gives you a “kit” so you don’t accidentally mix Mac buttons with Windows scrollbars.

## Why seniors get asked this

Cross-platform UI, multi-cloud SDKs, theme packs — seniors should explain **why a family** beats N independent factories that can be miscombined.

## Real-world analogy

Ordering a **IKEA kitchen set** for one style: cabinets, handles, and countertop that belong together — not mixing rustic handles with ultra-modern doors.

## Example

### Python

```python
from abc import ABC, abstractmethod


class Button(ABC):
    @abstractmethod
    def render(self) -> str: ...


class Checkbox(ABC):
    @abstractmethod
    def render(self) -> str: ...


class UIFactory(ABC):
    @abstractmethod
    def button(self) -> Button: ...

    @abstractmethod
    def checkbox(self) -> Checkbox: ...


class MacButton(Button):
    def render(self) -> str:
        return "MacButton"


class MacCheckbox(Checkbox):
    def render(self) -> str:
        return "MacCheckbox"


class MacFactory(UIFactory):
    def button(self) -> Button:
        return MacButton()

    def checkbox(self) -> Checkbox:
        return MacCheckbox()


class WinButton(Button):
    def render(self) -> str:
        return "WinButton"


class WinCheckbox(Checkbox):
    def render(self) -> str:
        return "WinCheckbox"


class WinFactory(UIFactory):
    def button(self) -> Button:
        return WinButton()

    def checkbox(self) -> Checkbox:
        return WinCheckbox()


def build_dialog(factory: UIFactory) -> None:
    print(factory.button().render(), factory.checkbox().render())


build_dialog(MacFactory())  # MacButton MacCheckbox
```

### Go

```go
type Button interface{ Render() string }
type Checkbox interface{ Render() string }

type UIFactory interface {
    Button() Button
    Checkbox() Checkbox
}

type macButton struct{}
func (macButton) Render() string { return "MacButton" }
type macCheckbox struct{}
func (macCheckbox) Render() string { return "MacCheckbox" }

type MacFactory struct{}
func (MacFactory) Button() Button     { return macButton{} }
func (MacFactory) Checkbox() Checkbox { return macCheckbox{} }

type winButton struct{}
func (winButton) Render() string { return "WinButton" }
type winCheckbox struct{}
func (winCheckbox) Render() string { return "WinCheckbox" }

type WinFactory struct{}
func (WinFactory) Button() Button     { return winButton{} }
func (WinFactory) Checkbox() Checkbox { return winCheckbox{} }

func BuildDialog(f UIFactory) {
    fmt.Println(f.Button().Render(), f.Checkbox().Render())
}
```

## When to use

- Products must stay consistent as a family (platform, theme, cloud vendor).
- Client code should depend only on abstract products + one factory interface.
- Swapping the whole family at startup (config → `MacFactory` vs `WinFactory`).

## When not to use / pitfalls

- One product type → Factory Method / simple factory is enough.
- Adding a new product *role* (e.g. `Slider`) forces changing every concrete factory — costly.
- Easy to over-engineer interview solutions; say “family consistency” or skip it.

## Interview trigger phrase

> “If Button and Checkbox must match a platform, I’d use an Abstract Factory so clients can’t mix Mac and Windows widgets.”

## Exercise

Support **Postgres** and **MySQL** stacks: each needs a `Connection` and a `MigrationRunner` that match the DB.

1. Sketch `DBFactory` with two methods.
2. Explain what goes wrong if you pick Postgres connection + MySQL migrator.
3. Would a single `CreateConnection(dbType)` factory be enough here? Why/why not?
