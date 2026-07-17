# Dependency Inversion Principle (DIP)

> High-level policy should **depend on abstractions**, not on concrete low-level details.

## Plain English

Your `OrderService` should not hard-code `SmtpEmailSender()`. It should depend on something like `Notifier` / `NotificationChannel`. The concrete sender is plugged in from the outside (constructor / main / DI container).

**Inversion:** both high-level and low-level depend on the *interface*, not high-level → concrete low-level.

Related but not identical: **Dependency Injection** is *how* you supply the dependency; DIP is *what* you depend on (abstraction).

## Why seniors get asked this

“How do you test this?” “How do you swap Kafka for Rabbit later?” Answer: invert dependencies.

## Bad: high-level owns a concrete detail

### Python

```python
class SmtpEmailSender:
    def send(self, to: str, body: str) -> None:
        print(f"SMTP → {to}: {body}")


class OrderService:
    def __init__(self) -> None:
        self._mail = SmtpEmailSender()  # locked to SMTP

    def place_order(self, user_email: str) -> None:
        # ... create order ...
        self._mail.send(user_email, "Order placed")
```

Hard to unit-test without real SMTP. Hard to add SMS without editing `OrderService`.

### Go

```go
type SmtpEmailSender struct{}

func (SmtpEmailSender) Send(to, body string) {
    fmt.Printf("SMTP → %s: %s\n", to, body)
}

type OrderService struct {
    mail SmtpEmailSender // concrete
}

func (s OrderService) PlaceOrder(userEmail string) {
    s.mail.Send(userEmail, "Order placed")
}
```

## Good: depend on an abstraction; inject the concrete

### Python

```python
from abc import ABC, abstractmethod


class NotificationChannel(ABC):
    @abstractmethod
    def send(self, to: str, body: str) -> None: ...


class SmtpEmailSender(NotificationChannel):
    def send(self, to: str, body: str) -> None:
        print(f"SMTP → {to}: {body}")


class SmsSender(NotificationChannel):
    def send(self, to: str, body: str) -> None:
        print(f"SMS → {to}: {body}")


class OrderService:
    def __init__(self, notifier: NotificationChannel) -> None:
        self._notifier = notifier

    def place_order(self, user_email: str) -> None:
        self._notifier.send(user_email, "Order placed")


# wiring (composition root / main)
svc = OrderService(SmtpEmailSender())
# tests: OrderService(FakeNotifier())
```

### Go

```go
type NotificationChannel interface {
    Send(to, body string)
}

type SmtpEmailSender struct{}
func (SmtpEmailSender) Send(to, body string) {
    fmt.Printf("SMTP → %s: %s\n", to, body)
}

type SmsSender struct{}
func (SmsSender) Send(to, body string) {
    fmt.Printf("SMS → %s: %s\n", to, body)
}

type OrderService struct {
    Notifier NotificationChannel // abstraction
}

func (s OrderService) PlaceOrder(userEmail string) {
    s.Notifier.Send(userEmail, "Order placed")
}

// main / wiring
svc := OrderService{Notifier: SmtpEmailSender{}}
```

## Interview tip

Don’t invent an interface for every class on day one. Invert at **boundaries that change or need testing**: IO, clocks, random, third-party SDKs, storage.

## Exercise

`ReportGenerator` reads sales from Postgres and writes a PDF to disk.

1. Name two abstractions you’d introduce.
2. Show how `main` (or tests) wires fakes.
3. One sentence: how is DIP different from “just using dependency injection”?
