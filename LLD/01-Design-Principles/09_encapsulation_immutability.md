# Encapsulation / Immutability

> **Hide** internal state; expose clear operations. Prefer **immutable** values for money, IDs, coordinates, money-like amounts.

## Plain English

**Encapsulation:** outsiders shouldn’t poke `obj._balance = -1`. They call `withdraw(amount)` which enforces rules.

**Immutability:** once created, a value doesn’t change. “Change” means return a *new* value (`money.add(tax)` → new `Money`). Safer for concurrency and reasoning.

## Why seniors get asked this

Race conditions, invalid invariants, “who mutated this list?” — seniors show they protect state and use value objects where it matters.

---

## Encapsulation

### Bad: public mutable guts

```python
class BankAccount:
    def __init__(self, balance: int):
        self.balance = balance  # anyone can set anything


acc = BankAccount(100)
acc.balance = -50  # invariant broken
```

```go
type BankAccount struct {
    Balance int // exported — any package can set it
}

acc := BankAccount{Balance: 100}
acc.Balance = -50
```

### Good: hide state, expose operations

```python
class BankAccount:
    def __init__(self, balance: int):
        if balance < 0:
            raise ValueError("balance cannot be negative")
        self._balance = balance

    def balance(self) -> int:
        return self._balance

    def deposit(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self._balance += amount

    def withdraw(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount
```

```go
type BankAccount struct {
    balance int // unexported
}

func NewBankAccount(balance int) (*BankAccount, error) {
    if balance < 0 {
        return nil, fmt.Errorf("balance cannot be negative")
    }
    return &BankAccount{balance: balance}, nil
}

func (a *BankAccount) Balance() int { return a.balance }

func (a *BankAccount) Deposit(amount int) error {
    if amount <= 0 {
        return fmt.Errorf("amount must be positive")
    }
    a.balance += amount
    return nil
}

func (a *BankAccount) Withdraw(amount int) error {
    if amount <= 0 {
        return fmt.Errorf("amount must be positive")
    }
    if amount > a.balance {
        return fmt.Errorf("insufficient funds")
    }
    a.balance -= amount
    return nil
}
```

---

## Immutability (value objects)

### Bad: mutable “money”

```python
class Money:
    def __init__(self, amount: int, currency: str):
        self.amount = amount
        self.currency = currency


price = Money(100, "INR")
tax = price
tax.amount = 18  # oops — also changed price
```

### Good: immutable Money

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("currency mismatch")
        return Money(self.amount + other.amount, self.currency)


price = Money(100, "INR")
total = price.add(Money(18, "INR"))
# price still 100; total is 118
```

```go
type Money struct {
    amount   int
    currency string
}

func NewMoney(amount int, currency string) Money {
    return Money{amount: amount, currency: currency}
}

func (m Money) Amount() int      { return m.amount }
func (m Money) Currency() string { return m.currency }

func (m Money) Add(other Money) (Money, error) {
    if m.currency != other.currency {
        return Money{}, fmt.Errorf("currency mismatch")
    }
    return Money{amount: m.amount + other.amount, currency: m.currency}, nil
}
```

In Go, returning a new `Money` by value is the usual immutability style; don’t expose setters.

### Also good: immutable coordinates

```python
@dataclass(frozen=True)
class Coordinate:
    x: int
    y: int
```

```go
type Coordinate struct{ X, Y int } // treat as value; don't mutate in place in APIs
```

## Interview trigger phrase

> “I’d keep invariants inside the type — and use immutable value objects for Money so shared references can’t corrupt totals.”

## Exercise

Design a `Cart` with line items `(sku, qty, unit_price)`.

1. What should be encapsulated vs exposed?
2. Should `Money` / line totals be immutable? Why?
3. Sketch (Python or Go) `cart.total()` without letting callers mutate internal lists freely (return a copy or don’t expose the list).
