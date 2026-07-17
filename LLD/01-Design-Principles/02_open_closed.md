# Open/Closed Principle (OCP)

> Software entities should be **open for extension**, **closed for modification**.

## Plain English

Add a new behavior by **adding new code**, not by editing a long `if/else` or `switch` in existing, working code.

You still change *something* (you add a class). You avoid repeatedly opening the same “hub” file every time product asks for one more type.

## Why seniors get asked this

Payments, shipping, pricing, notifications — interviewers love “add one more kind.” They want Strategy / polymorphism, not a growing `if` ladder.

## Bad: extend by editing the center

### Python

```python
class PaymentProcessor:
    def pay(self, method: str, amount: int) -> None:
        if method == "card":
            print(f"Charging card {amount}")
        elif method == "upi":
            print(f"UPI collect {amount}")
        elif method == "wallet":
            print(f"Wallet debit {amount}")
        # next week: crypto → edit this method again
```

Every new method = risk of breaking old ones.

### Go

```go
func Pay(method string, amount int) {
    switch method {
    case "card":
        fmt.Printf("Charging card %d\n", amount)
    case "upi":
        fmt.Printf("UPI collect %d\n", amount)
    case "wallet":
        fmt.Printf("Wallet debit %d\n", amount)
    }
}
```

## Good: extend by adding a type

### Python

```python
from abc import ABC, abstractmethod


class PaymentMethod(ABC):
    @abstractmethod
    def pay(self, amount: int) -> None: ...


class CardPayment(PaymentMethod):
    def pay(self, amount: int) -> None:
        print(f"Charging card {amount}")


class UpiPayment(PaymentMethod):
    def pay(self, amount: int) -> None:
        print(f"UPI collect {amount}")


class WalletPayment(PaymentMethod):
    def pay(self, amount: int) -> None:
        print(f"Wallet debit {amount}")


class PaymentProcessor:
    def pay(self, method: PaymentMethod, amount: int) -> None:
        method.pay(amount)


# New week: crypto — add a class, leave PaymentProcessor alone
class CryptoPayment(PaymentMethod):
    def pay(self, amount: int) -> None:
        print(f"Crypto transfer {amount}")
```

### Go

```go
type PaymentMethod interface {
    Pay(amount int)
}

type CardPayment struct{}
func (CardPayment) Pay(amount int) { fmt.Printf("Charging card %d\n", amount) }

type UpiPayment struct{}
func (UpiPayment) Pay(amount int) { fmt.Printf("UPI collect %d\n", amount) }

type WalletPayment struct{}
func (WalletPayment) Pay(amount int) { fmt.Printf("Wallet debit %d\n", amount) }

type PaymentProcessor struct{}
func (PaymentProcessor) Pay(m PaymentMethod, amount int) { m.Pay(amount) }

// New week: add CryptoPayment — PaymentProcessor unchanged
type CryptoPayment struct{}
func (CryptoPayment) Pay(amount int) { fmt.Printf("Crypto transfer %d\n", amount) }
```

## Interview tip

OCP is not “never touch existing files.” It’s: **don’t keep reopening the same decision hub**. Sometimes a simple `if` is fine for 2 stable cases — say that trade-off out loud.

## Exercise

Checkout has shipping: `standard` (flat ₹50) and `express` (₹150). Product wants `same_day` (₹300) and later maybe `pickup` (₹0).

1. Refactor so adding `same_day` does not edit the pricing calculator’s `if/else`.
2. In Python and Go, name the interface/method and one concrete type.
3. When would you *not* bother with OCP yet? (Hint: YAGNI.)
