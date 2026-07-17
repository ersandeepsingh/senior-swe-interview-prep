# Vending Machine

> Coin handling, dispense, refund → **State pattern**. 🟡

## Scope / Requirements

**In scope**
- Select product, insert money, dispense or refund.
- Track inventory and current balance.
- Explicit states: Idle → HasMoney / ProductSelected (order varies) → Dispense → Idle; cancel → refund.

**Out of scope**
- Card payments, change-making complexity beyond simple refund of inserted amount, admin restock UI polish.

**Domain invariants**
- Cannot dispense if balance < price or stock is 0.
- Inserted money is held until dispense or cancel; then either product out + change policy, or full refund.
- Only one “current selection” at a time (simplify).
- State transitions are the source of truth for allowed operations.

## Core Entities & Responsibilities

| Entity | Responsibility |
|--------|----------------|
| `Product` / `Inventory` | Code, price, quantity. |
| `VendingMachine` | Context holding state + balance + selection. |
| `State` | `insert`, `select`, `dispense`, `cancel` — behavior per state. |
| `Coin` / `Payment` | Accepted denominations; running balance. |

## Key Interfaces / Patterns

- **State:** each state implements the same operations; illegal ops return errors or no-ops. This is the interview’s main ask.
- **Optional Strategy:** payment method (cash vs card) later — don’t start there.

## End-to-End Flow

1. Idle → user selects A1 (or inserts coins first — pick one UX and stick to it).
2. Insert coins until balance ≥ price.
3. `dispense`: decrement stock, reduce balance / return change, go Idle.
4. Or `cancel`: refund balance, clear selection, Idle.

## Python Skeleton

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Product:
    code: str
    name: str
    price: int  # cents
    qty: int


class State(ABC):
    @abstractmethod
    def insert(self, m: VendingMachine, amount: int) -> None: ...
    @abstractmethod
    def select(self, m: VendingMachine, code: str) -> None: ...
    @abstractmethod
    def dispense(self, m: VendingMachine) -> None: ...
    @abstractmethod
    def cancel(self, m: VendingMachine) -> int: ...


class IdleState(State):
    def insert(self, m: VendingMachine, amount: int) -> None:
        m.balance += amount
        m.set_state(HasMoneyState())

    def select(self, m: VendingMachine, code: str) -> None:
        if code not in m.inventory or m.inventory[code].qty <= 0:
            raise RuntimeError("unavailable")
        m.selected = code
        m.set_state(HasSelectionState())

    def dispense(self, m: VendingMachine) -> None:
        raise RuntimeError("nothing to dispense")

    def cancel(self, m: VendingMachine) -> int:
        return 0


class HasSelectionState(State):
    def insert(self, m: VendingMachine, amount: int) -> None:
        m.balance += amount
        m.set_state(ReadyState())

    def select(self, m: VendingMachine, code: str) -> None:
        if code not in m.inventory or m.inventory[code].qty <= 0:
            raise RuntimeError("unavailable")
        m.selected = code

    def dispense(self, m: VendingMachine) -> None:
        raise RuntimeError("insert money")

    def cancel(self, m: VendingMachine) -> int:
        m.selected = None
        m.set_state(IdleState())
        return 0


class HasMoneyState(State):
    def insert(self, m: VendingMachine, amount: int) -> None:
        m.balance += amount

    def select(self, m: VendingMachine, code: str) -> None:
        if code not in m.inventory or m.inventory[code].qty <= 0:
            raise RuntimeError("unavailable")
        m.selected = code
        m.set_state(ReadyState())

    def dispense(self, m: VendingMachine) -> None:
        raise RuntimeError("select product")

    def cancel(self, m: VendingMachine) -> int:
        refund, m.balance = m.balance, 0
        m.set_state(IdleState())
        return refund


class ReadyState(State):
    """Selection + enough money (checked on dispense)."""

    def insert(self, m: VendingMachine, amount: int) -> None:
        m.balance += amount

    def select(self, m: VendingMachine, code: str) -> None:
        m.selected = code

    def dispense(self, m: VendingMachine) -> None:
        p = m.inventory[m.selected]
        if m.balance < p.price or p.qty <= 0:
            raise RuntimeError("cannot dispense")
        p.qty -= 1
        m.balance -= p.price
        change = m.balance
        m.balance = 0
        m.selected = None
        m.set_state(IdleState())
        m.last_change = change

    def cancel(self, m: VendingMachine) -> int:
        refund, m.balance = m.balance, 0
        m.selected = None
        m.set_state(IdleState())
        return refund


class VendingMachine:
    def __init__(self, inventory: dict[str, Product]):
        self.inventory = inventory
        self.balance = 0
        self.selected: str | None = None
        self.last_change = 0
        self._state: State = IdleState()

    def set_state(self, s: State) -> None:
        self._state = s

    def insert(self, amount: int) -> None:
        self._state.insert(self, amount)

    def select(self, code: str) -> None:
        self._state.select(self, code)

    def dispense(self) -> None:
        self._state.dispense(self)

    def cancel(self) -> int:
        return self._state.cancel(self)
```

## Go Skeleton

```go
package vending

import "errors"

type Product struct {
    Code  string
    Name  string
    Price int
    Qty   int
}

type State interface {
    Insert(m *Machine, amount int) error
    Select(m *Machine, code string) error
    Dispense(m *Machine) error
    Cancel(m *Machine) int
}

type Machine struct {
    Inventory map[string]*Product
    Balance   int
    Selected  string
    State     State
}

func NewMachine(inv map[string]*Product) *Machine {
    m := &Machine{Inventory: inv}
    m.State = Idle{}
    return m
}

type Idle struct{}

func (Idle) Insert(m *Machine, amount int) error {
    m.Balance += amount
    m.State = HasMoney{}
    return nil
}
func (Idle) Select(m *Machine, code string) error {
    p, ok := m.Inventory[code]
    if !ok || p.Qty <= 0 {
        return errors.New("unavailable")
    }
    m.Selected = code
    m.State = Ready{} // if money already there; else HasSelection — keep interview simple
    return nil
}
func (Idle) Dispense(*Machine) error { return errors.New("idle") }
func (Idle) Cancel(*Machine) int     { return 0 }

type HasMoney struct{}

func (HasMoney) Insert(m *Machine, amount int) error { m.Balance += amount; return nil }
func (HasMoney) Select(m *Machine, code string) error {
    p, ok := m.Inventory[code]
    if !ok || p.Qty <= 0 {
        return errors.New("unavailable")
    }
    m.Selected = code
    m.State = Ready{}
    return nil
}
func (HasMoney) Dispense(*Machine) error { return errors.New("select first") }
func (HasMoney) Cancel(m *Machine) int {
    r := m.Balance
    m.Balance = 0
    m.State = Idle{}
    return r
}

type Ready struct{}

func (Ready) Insert(m *Machine, amount int) error { m.Balance += amount; return nil }
func (Ready) Select(m *Machine, code string) error {
    m.Selected = code
    return nil
}
func (Ready) Dispense(m *Machine) error {
    p := m.Inventory[m.Selected]
    if m.Balance < p.Price || p.Qty <= 0 {
        return errors.New("cannot dispense")
    }
    p.Qty--
    m.Balance -= p.Price
    // change left in Balance for caller to collect, or return it
    m.Selected = ""
    m.State = Idle{}
    return nil
}
func (Ready) Cancel(m *Machine) int {
    r := m.Balance
    m.Balance, m.Selected = 0, ""
    m.State = Idle{}
    return r
}
```

## Concurrency / Consistency

- Usually single-user hardware; still mention: inventory decrement must be atomic with payment capture.
- Restocking vs purchase: mutex on inventory map.

## Extensions / Trade-offs / Pitfalls

- Exact change vs change-maker (greedy denominations) — separate `ChangeMaker` strategy.
- Card payment: new states or a payment Strategy; don’t explode the state graph.
- Pitfall: putting all `if state ==` in one class — interviewer wants State objects or a clear transition table.
- Pitfall: dispensing without decrementing qty (inventory bug).

## Interview Discussion Points

- Select-first vs pay-first UX — how does the state diagram change?
- When is a transition table / enum enough vs full State classes?
- How do you test every illegal operation per state?

## Exercise

Draw the state diagram, then implement **select → insert → dispense** and **cancel refund**.

**Follow-ups**
1. Add “sold out” handling that stays in a usable state without crashing.
2. Support returning change in coins via a `ChangeMaker` without bloating `Ready.Dispense`.
3. Name one new state you’d add for maintenance/restock mode.
