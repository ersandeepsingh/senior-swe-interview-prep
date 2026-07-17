# Testability

> Injected dependencies + **pure domain logic** so it’s unit-testable.

## Plain English

If pricing, matching, or discount math is a pure function/strategy, you test it with tables of inputs — no DB, no clock, no network. Services accept repositories and strategies in the constructor so tests inject fakes.

Testability is the practical payoff of DIP, Strategy, and small pure functions.

## Senior signal

When asked “how do you test this?”, you point at seams: fake `Inventory`, stub `PaymentMethod`, deterministic `PricingStrategy`. You don’t need a full framework — a hand-written fake is enough in LLD.

## Examples

### Python

```python
from abc import ABC, abstractmethod


class PaymentMethod(ABC):
    @abstractmethod
    def charge(self, order_id: str, amount: int) -> bool: ...


class CheckoutService:
    def __init__(self, payment: PaymentMethod):
        self._payment = payment

    def checkout(self, order_id: str, amount: int) -> str:
        if amount <= 0:
            raise ValueError("amount")
        if not self._payment.charge(order_id, amount):
            raise RuntimeError("payment failed")
        return "PAID"


class FakePayment(PaymentMethod):
    def __init__(self, ok: bool = True):
        self.ok, self.calls = ok, []

    def charge(self, order_id: str, amount: int) -> bool:
        self.calls.append((order_id, amount))
        return self.ok


def test_checkout_success():
    pay = FakePayment(ok=True)
    svc = CheckoutService(pay)
    assert svc.checkout("o1", 100) == "PAID"
    assert pay.calls == [("o1", 100)]


def test_checkout_payment_failure():
    svc = CheckoutService(FakePayment(ok=False))
    try:
        svc.checkout("o1", 100)
        assert False, "expected error"
    except RuntimeError:
        pass
```

### Go

```go
type PaymentMethod interface {
    Charge(orderID string, amount int) bool
}

type CheckoutService struct{ Pay PaymentMethod }

func (s CheckoutService) Checkout(orderID string, amount int) error {
    if amount <= 0 {
        return fmt.Errorf("amount")
    }
    if !s.Pay.Charge(orderID, amount) {
        return fmt.Errorf("payment failed")
    }
    return nil
}

type FakePayment struct {
    OK    bool
    Calls []string
}

func (f *FakePayment) Charge(orderID string, amount int) bool {
    f.Calls = append(f.Calls, orderID)
    return f.OK
}

func TestCheckout(t *testing.T) {
    fake := &FakePayment{OK: true}
    if err := (CheckoutService{fake}).Checkout("o1", 100); err != nil {
        t.Fatal(err)
    }
}
```

## When / how to apply

1. Inject every I/O dependency (repo, clock, rng, gateway).
2. Keep decision logic in pure strategies / functions.
3. Prefer fakes over mocks when state is simple.
4. Say which tests you’d write even if you don’t type them all: happy path, invariant violation, payment fail → release stock.

## Pitfalls

- `datetime.now()` / `random` buried inside domain — inject clock/rng.
- Singletons and global registries — hard to isolate.
- Testing only through the full UI/main.
- Over-mocking until tests mirror implementation.

## Interview trigger

> “I’d unit-test discount and reserve logic with an in-memory inventory and a fake payment — no DB required.”

## Exercise

Take your **coupon engine** or **wallet debit**: write two tests (success + insufficient funds / ineligible coupon) using a fake or pure function. Speak the test names out loud as acceptance criteria.
