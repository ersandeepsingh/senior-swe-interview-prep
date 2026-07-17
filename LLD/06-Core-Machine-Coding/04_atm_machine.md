# ATM Machine

> Auth, withdrawal, cash dispensing → **State + Chain of Responsibility**. 🟡

## Scope / Requirements

**In scope**
- Card insert → PIN auth → choose transaction (withdraw focus) → dispense cash → eject.
- Cash dispenser breaks amount into denominations (2000/500/100…) via chain.
- Session state machine; max PIN attempts.

**Out of scope**
- Full bank network, deposit hardware, mini-statement UI, multi-language.

**Domain invariants**
- No withdrawal without authenticated session.
- Dispense only if ATM cash + account balance suffice (account may be stubbed).
- Denomination chain must total exactly the requested amount or fail entirely (no partial dispense).
- Card ejected / session cleared on exit or too many bad PINs.

## Core Entities & Responsibilities

| Entity | Responsibility |
|--------|----------------|
| `ATM` | Context: state, card, session. |
| `ATMState` | Idle, CardInserted, Authenticated, Dispensing… |
| `Card` / `BankService` | Validate PIN, get/debit balance (interface). |
| `Dispenser` / `CashHandler` | Chain: try notes of one denomination, pass remainder. |
| `Cassette` | Count of notes per denomination. |

## Key Interfaces / Patterns

- **State:** session lifecycle and which ops are legal.
- **Chain of Responsibility:** each handler peels off as many of its notes as possible; last handler fails if remainder ≠ 0.
- **DIP:** `BankService` interface so ATM doesn’t know core banking.

## End-to-End Flow

1. Idle → insert card → enter PIN → bank validates.
2. Withdraw 3700 → check balance & ATM cash → chain: 1×2000 + 3×500 + 2×100 → debit account → update cassettes → eject.

## Python Skeleton

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Cassette:
    denomination: int
    count: int


class CashHandler(ABC):
    def __init__(self, cassette: Cassette, next: CashHandler | None = None):
        self.cassette = cassette
        self.next = next

    def dispense(self, amount: int) -> dict[int, int]:
        denom = self.cassette.denomination
        take = min(amount // denom, self.cassette.count)
        # greedy; for interview OK — mention DP for optimal later
        used = {denom: take} if take else {}
        remainder = amount - take * denom
        if remainder == 0:
            self.cassette.count -= take
            return used
        if not self.next:
            raise RuntimeError("cannot dispense exact amount")
        rest = self.next.dispense(remainder)
        self.cassette.count -= take
        used.update(rest)
        return used


@dataclass
class BankService(ABC):
    @abstractmethod
    def authenticate(self, card_id: str, pin: str) -> bool: ...
    @abstractmethod
    def balance(self, card_id: str) -> int: ...
    @abstractmethod
    def debit(self, card_id: str, amount: int) -> None: ...


class ATMState(ABC):
    @abstractmethod
    def insert_card(self, atm: ATM, card_id: str) -> None: ...
    @abstractmethod
    def enter_pin(self, atm: ATM, pin: str) -> None: ...
    @abstractmethod
    def withdraw(self, atm: ATM, amount: int) -> dict[int, int]: ...
    @abstractmethod
    def eject(self, atm: ATM) -> None: ...


class Idle(ATMState):
    def insert_card(self, atm: ATM, card_id: str) -> None:
        atm.card_id = card_id
        atm.pin_attempts = 0
        atm.state = CardInserted()

    def enter_pin(self, atm: ATM, pin: str) -> None:
        raise RuntimeError("no card")

    def withdraw(self, atm: ATM, amount: int) -> dict[int, int]:
        raise RuntimeError("no card")

    def eject(self, atm: ATM) -> None:
        pass


class CardInserted(ATMState):
    def insert_card(self, atm: ATM, card_id: str) -> None:
        raise RuntimeError("card present")

    def enter_pin(self, atm: ATM, pin: str) -> None:
        if atm.bank.authenticate(atm.card_id, pin):
            atm.state = Authenticated()
            return
        atm.pin_attempts += 1
        if atm.pin_attempts >= 3:
            atm.card_id = None
            atm.state = Idle()
            raise RuntimeError("card retained / session cleared")

    def withdraw(self, atm: ATM, amount: int) -> dict[int, int]:
        raise RuntimeError("auth required")

    def eject(self, atm: ATM) -> None:
        atm.card_id = None
        atm.state = Idle()


class Authenticated(ATMState):
    def insert_card(self, atm: ATM, card_id: str) -> None:
        raise RuntimeError("busy")

    def enter_pin(self, atm: ATM, pin: str) -> None:
        raise RuntimeError("already auth")

    def withdraw(self, atm: ATM, amount: int) -> dict[int, int]:
        if amount <= 0 or amount % 100 != 0:
            raise RuntimeError("invalid amount")
        if atm.bank.balance(atm.card_id) < amount:
            raise RuntimeError("insufficient funds")
        notes = atm.dispenser.dispense(amount)  # may raise
        atm.bank.debit(atm.card_id, amount)
        return notes

    def eject(self, atm: ATM) -> None:
        atm.card_id = None
        atm.state = Idle()


@dataclass
class ATM:
    bank: BankService
    dispenser: CashHandler
    state: ATMState = field(default_factory=Idle)
    card_id: str | None = None
    pin_attempts: int = 0

    def insert_card(self, card_id: str) -> None:
        self.state.insert_card(self, card_id)

    def enter_pin(self, pin: str) -> None:
        self.state.enter_pin(self, pin)

    def withdraw(self, amount: int) -> dict[int, int]:
        return self.state.withdraw(self, amount)

    def eject(self) -> None:
        self.state.eject(self)


def build_dispenser(cassettes: list[Cassette]) -> CashHandler:
    cassettes = sorted(cassettes, key=lambda c: -c.denomination)
    head: CashHandler | None = None
    for c in reversed(cassettes):
        head = CashHandlerImpl(c, head)  # see below
    return head  # type: ignore


class CashHandlerImpl(CashHandler):
    pass
```

## Go Skeleton

```go
package atm

import "errors"

type Cassette struct {
    Denom int
    Count int
}

type Handler struct {
    Cas  *Cassette
    Next *Handler
}

func (h *Handler) Dispense(amount int) (map[int]int, error) {
    take := amount / h.Cas.Denom
    if take > h.Cas.Count {
        take = h.Cas.Count
    }
    rem := amount - take*h.Cas.Denom
    out := map[int]int{}
    if take > 0 {
        out[h.Cas.Denom] = take
    }
    if rem == 0 {
        h.Cas.Count -= take
        return out, nil
    }
    if h.Next == nil {
        return nil, errors.New("cannot dispense")
    }
    rest, err := h.Next.Dispense(rem)
    if err != nil {
        return nil, err // no partial commit — ideally reserve first
    }
    h.Cas.Count -= take
    for k, v := range rest {
        out[k] = v
    }
    return out, nil
}

type Bank interface {
    Authenticate(cardID, pin string) bool
    Balance(cardID string) int
    Debit(cardID string, amount int) error
}

type ATM struct {
    Bank      Bank
    Dispenser *Handler
    CardID    string
    Auth      bool
    Attempts  int
}

func (a *ATM) InsertCard(id string) { a.CardID, a.Auth, a.Attempts = id, false, 0 }

func (a *ATM) EnterPIN(pin string) error {
    if a.CardID == "" {
        return errors.New("no card")
    }
    if a.Bank.Authenticate(a.CardID, pin) {
        a.Auth = true
        return nil
    }
    a.Attempts++
    if a.Attempts >= 3 {
        a.CardID, a.Auth = "", false
        return errors.New("locked out")
    }
    return errors.New("bad pin")
}

func (a *ATM) Withdraw(amount int) (map[int]int, error) {
    if !a.Auth {
        return nil, errors.New("unauthenticated")
    }
    if a.Bank.Balance(a.CardID) < amount {
        return nil, errors.New("insufficient funds")
    }
    notes, err := a.Dispenser.Dispense(amount)
    if err != nil {
        return nil, err
    }
    if err := a.Bank.Debit(a.CardID, amount); err != nil {
        // compensate cassette in production
        return nil, err
    }
    return notes, nil
}
```

## Concurrency / Consistency

- Dispense + debit should be transactional: reserve notes → debit → commit, or compensate on failure.
- One ATM session at a time physically; bank API needs idempotency keys for retries.

## Extensions / Trade-offs / Pitfalls

- Greedy chain fails for some cassette mixes — mention dynamic programming / “canMake”.
- Partial cassette update before chain fails → **pitfall**; two-phase: plan then commit.
- Deposit, transfer: new authenticated operations, same state shell.

## Interview Discussion Points

- Why Chain for denominations instead of one loop? (extensibility, classic CoR demo)
- How do you avoid dispensing cash if bank debit fails?
- State objects vs boolean `authenticated` — when do you upgrade?

## Exercise

Build dispenser chain for ₹2000/₹500/₹100 and withdraw ₹3700 after PIN auth.

**Follow-ups**
1. Make dispense atomic (plan notes without mutating, then apply).
2. Add a `MiniStatement` op only in Authenticated state.
3. What happens if the ₹100 cassette is empty but amount needs it?
