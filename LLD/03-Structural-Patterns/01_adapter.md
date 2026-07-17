# Adapter

> Convert one interface into another that clients expect — make **incompatible APIs** work together without changing the adaptee.

## Plain English

Your code wants `PaymentGateway.charge(amount)`. The third-party SDK exposes `StripeClient.createCharge(cents, currency)`. An Adapter wraps the SDK and speaks *your* interface.

## Why seniors get asked this

Integrating legacy or vendor SDKs is everyday work. Interviewers check whether you isolate vendor shapes behind your domain interface so swapping Stripe → Razorpay is localized.

## Real-world analogy

A **travel plug adapter**: your laptop’s plug doesn’t change; the wall socket does — the adapter sits in between.

## Example

### Python

```python
from abc import ABC, abstractmethod


class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount_rupees: int) -> None: ...


# Third-party — we don't modify this
class StripeClient:
    def create_charge(self, cents: int, currency: str) -> None:
        print(f"Stripe charge {cents} {currency}")


class StripeAdapter(PaymentGateway):
    def __init__(self, client: StripeClient) -> None:
        self._client = client

    def charge(self, amount_rupees: int) -> None:
        self._client.create_charge(amount_rupees * 100, "INR")


gateway: PaymentGateway = StripeAdapter(StripeClient())
gateway.charge(50)  # domain code never sees Stripe
```

### Go

```go
type PaymentGateway interface {
    Charge(amountRupees int)
}

// Third-party shape
type StripeClient struct{}

func (StripeClient) CreateCharge(cents int, currency string) {
    fmt.Printf("Stripe charge %d %s\n", cents, currency)
}

type StripeAdapter struct {
    Client StripeClient
}

func (a StripeAdapter) Charge(amountRupees int) {
    a.Client.CreateCharge(amountRupees*100, "INR")
}
```

## When to use

- You must use a library whose API doesn’t match your abstractions.
- You want domain code free of vendor types and naming.
- Migrating legacy modules: adapt old API to new without big-bang rewrite.

## When not to use / pitfalls

- If you own both sides, just change the API — don’t add a useless wrapper.
- Fat adapters that leak vendor types into callers defeat the purpose.
- Don’t confuse with **Facade** (simplify many classes) or **Decorator** (same interface + extra behavior).
- One adapter per vendor/interface is fine; a mega-adapter for everything isn’t.

## Interview trigger phrase

> “I’d wrap the Stripe SDK behind our PaymentGateway adapter so checkout never depends on Stripe types.”

## Exercise

Your app expects `Logger.log(level, message)`. A vendor offers `Audit.write(eventJSON string)`.

1. Sketch an Adapter implementing `Logger`.
2. What should *not* appear in call sites?
3. How is this different from a Facade?
