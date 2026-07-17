# State

> Let an object **alter its behavior when its internal state changes** — as if the object changed its class.

## Plain English

A vending machine accepts coins only in `Idle`, dispenses only in `HasMoney`, etc. Instead of a giant `if state == ...` in every method, each state object implements the actions legal for that state and performs transitions.

## Why seniors get asked this

Vending machines, orders, elevators, traffic lights — **lifecycle** problems. Interviewers want explicit states + transitions, not boolean soup (`isPaid && !isShipped && ...`).

## Real-world analogy

A **traffic light**: red, yellow, green each allow different actions (stop / prepare / go). The intersection “behaves differently” based on which light is lit.

## Example

### Python

```python
from abc import ABC, abstractmethod


class VendingMachine:
    def __init__(self) -> None:
        self.state: State = Idle(self)
        self.balance = 0

    def insert(self, coins: int) -> None:
        self.state.insert(coins)

    def select(self) -> None:
        self.state.select()


class State(ABC):
    def __init__(self, m: VendingMachine) -> None:
        self.m = m

    @abstractmethod
    def insert(self, coins: int) -> None: ...

    @abstractmethod
    def select(self) -> None: ...


class Idle(State):
    def insert(self, coins: int) -> None:
        self.m.balance += coins
        self.m.state = HasMoney(self.m)
        print(f"balance={self.m.balance}")

    def select(self) -> None:
        print("insert coins first")


class HasMoney(State):
    def insert(self, coins: int) -> None:
        self.m.balance += coins
        print(f"balance={self.m.balance}")

    def select(self) -> None:
        if self.m.balance < 50:
            print("need 50")
            return
        self.m.balance -= 50
        print("dispensed")
        self.m.state = Idle(self.m)


vm = VendingMachine()
vm.select()
vm.insert(50)
vm.select()
```

### Go

```go
type State interface {
    Insert(coins int)
    Select()
}

type VendingMachine struct {
    State   State
    Balance int
}

type Idle struct{ M *VendingMachine }
func (s Idle) Insert(coins int) {
    s.M.Balance += coins
    s.M.State = HasMoney{M: s.M}
    fmt.Println("balance=", s.M.Balance)
}
func (s Idle) Select() { fmt.Println("insert coins first") }

type HasMoney struct{ M *VendingMachine }
func (s HasMoney) Insert(coins int) {
    s.M.Balance += coins
}
func (s HasMoney) Select() {
    if s.M.Balance < 50 {
        fmt.Println("need 50")
        return
    }
    s.M.Balance -= 50
    fmt.Println("dispensed")
    s.M.State = Idle{M: s.M}
}
```

## When to use

- Behavior differs sharply by lifecycle phase; transitions are first-class.
- Boolean/enum flags create invalid combinations.
- You need to make illegal operations obvious per state.

## When not to use / pitfalls

- Two states with tiny differences → enum + small switch can be clearer.
- Too many micro-states → explosion; consider hierarchical state machines only if needed.
- Don’t confuse with **Strategy** (client swaps algorithm; not driven by internal lifecycle).
- Shared mutable data on the context must stay consistent across transitions.

## Interview trigger phrase

> “Order lifecycle has illegal ops per phase — I’d model explicit State objects and transitions instead of boolean flags.”

## Exercise

Model order states: `Created` → `Paid` → `Shipped` → `Delivered`. Cancel allowed only before shipped.

1. Which transitions are legal?
2. Where does `cancel()` live, and what does it reject?
3. State vs Strategy in one sentence.
