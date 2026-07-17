# Factory Method

> Define an interface for creating an object, but let **subclasses (or a creator strategy) decide** which concrete class to instantiate.

## Plain English

Callers ask for “a notification” / “a parser” without `if type == ...` everywhere. Creation logic lives in one place — a factory method or small factory type — so adding a new variant touches the factory, not every call site.

Classic GoF: a creator class with `createProduct()` overridden by subclasses. In interviews, a **simple factory function/class** that maps type → object is usually enough and is what people mean.

## Why seniors get asked this

Notification channels, payment methods, vehicle types — interviewers watch whether you centralize construction instead of scattering `if/else` + `new` through the domain.

## Real-world analogy

A **vending machine button** doesn’t know how the snack is packaged in the warehouse; pressing “chips” asks the machine to dispense the right item.

## Example

### Python

```python
from abc import ABC, abstractmethod


class Notification(ABC):
    @abstractmethod
    def send(self, to: str, msg: str) -> None: ...


class EmailNotification(Notification):
    def send(self, to: str, msg: str) -> None:
        print(f"Email → {to}: {msg}")


class SmsNotification(Notification):
    def send(self, to: str, msg: str) -> None:
        print(f"SMS → {to}: {msg}")


def create_notification(kind: str) -> Notification:
    if kind == "email":
        return EmailNotification()
    if kind == "sms":
        return SmsNotification()
    raise ValueError(f"unknown kind: {kind}")


n = create_notification("email")
n.send("a@b.com", "Order shipped")
```

### Go

```go
type Notification interface {
    Send(to, msg string)
}

type EmailNotification struct{}
func (EmailNotification) Send(to, msg string) {
    fmt.Printf("Email → %s: %s\n", to, msg)
}

type SmsNotification struct{}
func (SmsNotification) Send(to, msg string) {
    fmt.Printf("SMS → %s: %s\n", to, msg)
}

func CreateNotification(kind string) (Notification, error) {
    switch kind {
    case "email":
        return EmailNotification{}, nil
    case "sms":
        return SmsNotification{}, nil
    default:
        return nil, fmt.Errorf("unknown kind: %s", kind)
    }
}
```

## When to use

- Several related product types share an interface; callers shouldn’t know concretes.
- Creation rules may grow (defaults, validation, config) and you want one place for them.
- You expect “add one more type” without editing every use site.

## When not to use / pitfalls

- Two stable types with no growth → a direct constructor is fine (YAGNI).
- Don’t confuse with **Abstract Factory** (families of products) or **Strategy** (behavior swap after creation).
- A giant `switch` factory that also contains business logic is still a God function — factory should mostly *create*.

## Interview trigger phrase

> “Call sites shouldn’t `new` concrete channels — I’d put construction behind a factory so adding Push doesn’t touch OrderService.”

## Exercise

`ReportExporter` must support `csv` and `pdf` today, maybe `xlsx` later.

1. Define a common interface and a factory method/function.
2. Show how `main` requests `"csv"` without importing the PDF type.
3. When would you skip the factory?
