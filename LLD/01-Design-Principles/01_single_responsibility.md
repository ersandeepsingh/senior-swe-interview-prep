# Single Responsibility Principle (SRP)

> A class (or module) should have **one reason to change**.

## Plain English

If you change *how invoices are formatted* and that forces you to touch *payment logic*, those two concerns are stuck in the same place. Split them.

**One responsibility ≠ one method.** It means one *business* reason to change (e.g. “how we send email” vs “how we calculate tax”).

## Why seniors get asked this

Machine-coding often starts as a “God class.” Interviewers watch whether you carve it into focused pieces without over-splitting into 20 tiny files.

## Bad: one class does everything

### Python

```python
class OrderService:
    def place_order(self, user_id: str, items: list[dict]) -> None:
        total = sum(i["price"] * i["qty"] for i in items)
        # persistence
        print(f"INSERT order user={user_id} total={total}")
        # email
        print(f"Email to {user_id}: thanks for order of {total}")
        # analytics
        print(f"Track event order_placed amount={total}")
```

Change email templates → touch `OrderService`. Change DB → touch `OrderService`. Change analytics → same class. **Three reasons to change.**

### Go

```go
type OrderService struct{}

func (s OrderService) PlaceOrder(userID string, items []Item) {
    total := 0
    for _, it := range items {
        total += it.Price * it.Qty
    }
    fmt.Printf("INSERT order user=%s total=%d\n", userID, total)
    fmt.Printf("Email to %s: thanks for order of %d\n", userID, total)
    fmt.Printf("Track event order_placed amount=%d\n", total)
}
```

## Good: one reason to change per type

### Python

```python
class OrderRepository:
    def save(self, user_id: str, total: int) -> None:
        print(f"INSERT order user={user_id} total={total}")


class EmailNotifier:
    def send_order_confirmation(self, user_id: str, total: int) -> None:
        print(f"Email to {user_id}: thanks for order of {total}")


class Analytics:
    def track_order_placed(self, total: int) -> None:
        print(f"Track event order_placed amount={total}")


class OrderService:
    def __init__(self, repo: OrderRepository, mail: EmailNotifier, analytics: Analytics):
        self._repo = repo
        self._mail = mail
        self._analytics = analytics

    def place_order(self, user_id: str, items: list[dict]) -> None:
        total = sum(i["price"] * i["qty"] for i in items)
        self._repo.save(user_id, total)
        self._mail.send_order_confirmation(user_id, total)
        self._analytics.track_order_placed(total)
```

`OrderService` **orchestrates**. Email wording lives only in `EmailNotifier`.

### Go

```go
type OrderRepository struct{}
func (r OrderRepository) Save(userID string, total int) {
    fmt.Printf("INSERT order user=%s total=%d\n", userID, total)
}

type EmailNotifier struct{}
func (e EmailNotifier) SendOrderConfirmation(userID string, total int) {
    fmt.Printf("Email to %s: thanks for order of %d\n", userID, total)
}

type Analytics struct{}
func (a Analytics) TrackOrderPlaced(total int) {
    fmt.Printf("Track event order_placed amount=%d\n", total)
}

type OrderService struct {
    Repo      OrderRepository
    Mail      EmailNotifier
    Analytics Analytics
}

func (s OrderService) PlaceOrder(userID string, items []Item) {
    total := 0
    for _, it := range items {
        total += it.Price * it.Qty
    }
    s.Repo.Save(userID, total)
    s.Mail.SendOrderConfirmation(userID, total)
    s.Analytics.TrackOrderPlaced(total)
}
```

## Interview trigger phrase

> “This class has too many reasons to change — I’d split persistence, notification, and domain rules.”

## Exercise

**Design a `UserAccount` feature** that can: create a user, hash a password, save to DB, and send a welcome email.

1. Sketch 3–4 types and what each owns.
2. Say out loud: *what change would touch only one type?*
3. Stop before inventing interfaces you don’t need yet (that’s OCP / DIP later).
