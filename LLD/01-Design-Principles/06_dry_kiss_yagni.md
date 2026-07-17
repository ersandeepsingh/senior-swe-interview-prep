# DRY / KISS / YAGNI

Three short principles that keep interview designs **simple and honest**. Seniors get points for *not* over-engineering.

---

## DRY — Don’t Repeat Yourself

> Every piece of knowledge should have a **single, clear representation**.

### Plain English

If the same rule lives in two places, one will rot. Extract the shared rule — but don’t force unrelated things into one abstraction (“wrong DRY”).

### Bad (duplicated rule)

```python
def apply_checkout_discount(total: int, is_premium: bool) -> int:
    if is_premium:
        return int(total * 0.9)
    return total


def apply_renewal_discount(total: int, is_premium: bool) -> int:
    if is_premium:
        return int(total * 0.9)  # same rule, copy-pasted
    return total
```

```go
func ApplyCheckoutDiscount(total int, premium bool) int {
    if premium {
        return total * 9 / 10
    }
    return total
}

func ApplyRenewalDiscount(total int, premium bool) int {
    if premium {
        return total * 9 / 10 // duplicated knowledge
    }
    return total
}
```

### Good (one place for the rule)

```python
def premium_price(total: int, is_premium: bool) -> int:
    return int(total * 0.9) if is_premium else total


def apply_checkout_discount(total: int, is_premium: bool) -> int:
    return premium_price(total, is_premium)


def apply_renewal_discount(total: int, is_premium: bool) -> int:
    return premium_price(total, is_premium)
```

```go
func PremiumPrice(total int, premium bool) int {
    if premium {
        return total * 9 / 10
    }
    return total
}
```

**Wrong DRY:** merging `User` and `Invoice` into one “Entity” because both have `id` and `created_at`. Same shape ≠ same knowledge.

---

## KISS — Keep It Simple, Stupid

> Prefer the **simplest design that works** for the stated requirements.

### Plain English

In a 45-minute LLD, a clear class diagram + a few interfaces beats a miniature framework.

### Example

Need: store last 100 events in memory for an interview problem.

**Simple enough:** a list / ring buffer.

**Not KISS (yet):** Kafka + Redis Streams + CQRS “because scale.”

```python
from collections import deque


class RecentEvents:
    def __init__(self, capacity: int = 100):
        self._q: deque[str] = deque(maxlen=capacity)

    def add(self, event: str) -> None:
        self._q.append(event)

    def list(self) -> list[str]:
        return list(self._q)
```

```go
type RecentEvents struct {
    buf  []string
    cap  int
    head int
    size int
}

func NewRecentEvents(capacity int) *RecentEvents {
    return &RecentEvents{buf: make([]string, capacity), cap: capacity}
}

func (r *RecentEvents) Add(event string) {
    r.buf[r.head] = event
    r.head = (r.head + 1) % r.cap
    if r.size < r.cap {
        r.size++
    }
}
```

Say out loud: “I’d start with an in-memory ring buffer; if durability is required, we swap the store behind an interface.”

---

## YAGNI — You Aren’t Gonna Need It

> Don’t build features or abstractions **for imagined future requirements**.

### Plain English

Interviewer said “one parking lot.” Don’t invent multi-city sharding, plugin loaders, and event sourcing unless asked.

### Bad (speculative)

```python
class ParkingLotFactoryProviderAbstractBuilder:  # nobody asked for this
    ...
```

### Good (ship what’s asked)

```python
class ParkingLot:
    def __init__(self, spots: int):
        self._free = spots

    def park(self) -> bool:
        if self._free == 0:
            return False
        self._free -= 1
        return True
```

```go
type ParkingLot struct{ free int }

func NewParkingLot(spots int) *ParkingLot { return &ParkingLot{free: spots} }

func (p *ParkingLot) Park() bool {
    if p.free == 0 {
        return false
    }
    p.free--
    return true
}
```

When they add “two floors,” *then* introduce floors — that’s OCP/YAGNI working together.

---

## How they work together in an interview

| Principle | Use when… |
|-----------|-----------|
| **DRY** | Same business rule appears twice |
| **KISS** | Choosing between clever vs clear |
| **YAGNI** | Tempted to add “for later” hooks |

## Exercise

Prompt: “Design a rate limiter: max 100 requests per user per minute. In-memory is fine.”

1. List 3 things a junior might over-build (YAGNI violations).
2. Write a KISS sketch (Python or Go) for the happy path.
3. Point to one place you’d DRY if you also need “per IP” later — without building it now.
