# Error Handling & Validation

> Domain exceptions vs return codes; **fail fast** at boundaries.

## Plain English

Validate input and invariants at the edge of the domain (service / aggregate methods). Reject illegal state transitions and bad payloads early with clear errors. Don’t let corrupt state travel deeper and fail mysteriously in persistence.

Prefer **domain-meaningful** errors (`InsufficientFunds`, `SeatUnavailable`) over generic `false` or bare strings — callers and tests can branch.

## Senior signal

You distinguish: validation errors (caller fault), domain rule violations, and infra failures. You don’t `print` and continue after an invariant break.

## Examples

### Python

```python
class DomainError(Exception):
    pass


class InsufficientFunds(DomainError):
    pass


class IllegalTransition(DomainError):
    pass


ALLOWED = {"PENDING": {"PAID", "CANCELLED"}, "PAID": {"SHIPPED"}}


def transition(status: str, to: str) -> str:
    if to not in ALLOWED.get(status, set()):
        raise IllegalTransition(f"{status} → {to}")
    return to


def debit(balance: int, amount: int) -> int:
    if amount <= 0:
        raise ValueError("amount must be positive")  # input validation
    if balance < amount:
        raise InsufficientFunds()
    return balance - amount
```

### Go

```go
var (
    ErrInsufficientFunds = errors.New("insufficient funds")
    ErrIllegalTransition = errors.New("illegal transition")
)

func Debit(balance, amount int64) (int64, error) {
    if amount <= 0 {
        return balance, fmt.Errorf("amount must be positive")
    }
    if balance < amount {
        return balance, ErrInsufficientFunds
    }
    return balance - amount, nil
}

func Transition(status, to string) (string, error) {
    // check ALLOWED map
    if !allowed(status, to) {
        return status, ErrIllegalTransition
    }
    return to, nil
}
```

## When / how to apply

1. Validate primitives at API/service entry (null, empty, negative qty).
2. Enforce invariants inside aggregates (`Order.transition`).
3. Map domain errors → HTTP 4xx / application error codes at the adapter layer.
4. Don’t catch-and-ignore; log infra errors and fail the unit of work.

## Pitfalls

- Returning `None`/`null` for both “not found” and “error”.
- Validating only in the UI.
- Huge try/except that swallows bugs.
- Using exceptions for normal control flow in hot match loops (prefer explicit results there if performance matters — say so).

## Interview trigger

> “I’d fail fast on illegal transitions with a domain exception, and keep validation at the service boundary so the entity never enters a bad state.”

## Exercise

For **vending machine** or **order state**: list 3 illegal actions and show how each surfaces as a typed error in Python or Go.
