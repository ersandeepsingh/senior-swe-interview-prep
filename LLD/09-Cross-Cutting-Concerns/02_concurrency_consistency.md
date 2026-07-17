# Concurrency & Consistency

> Seat/inventory locking, idempotency, race conditions — call these out **proactively**.

## Plain English

When two requests touch the same scarce resource (seat, SKU, driver, wallet), “check then act” without coordination double-books. Consistency means defining what must never happen (oversell, negative balance) and picking locks, CAS, single-writer queues, or DB constraints to enforce it.

Idempotency means retries don’t apply the effect twice.

## Senior signal

After the happy path, you say: “Here’s the race, here’s the critical section, here’s idempotency.” You don’t need a distributed systems thesis — a correct **per-key lock** or **single thread per symbol** story is enough.

## Examples

### Python

```python
import threading


class SeatBooker:
    def __init__(self):
        self._seats: set[str] = {"A1", "A2"}
        self._lock = threading.Lock()
        self._idem: dict[str, bool] = {}

    def book(self, seat: str, idem_key: str) -> bool:
        with self._lock:
            if idem_key in self._idem:
                return self._idem[idem_key]
            ok = seat in self._seats
            if ok:
                self._seats.remove(seat)
            self._idem[idem_key] = ok
            return ok
```

### Go

```go
type SeatBooker struct {
    mu    sync.Mutex
    seats map[string]struct{}
    idem  map[string]bool
}

func (b *SeatBooker) Book(seat, idemKey string) bool {
    b.mu.Lock()
    defer b.mu.Unlock()
    if v, ok := b.idem[idemKey]; ok {
        return v
    }
    _, available := b.seats[seat]
    if available {
        delete(b.seats, seat)
    }
    b.idem[idemKey] = available
    return available
}
```

**Stronger stories to name:** per-SKU mutex; lock wallets in sorted id order; matching engine actor per symbol; SQL `UPDATE stock SET qty = qty - 1 WHERE qty >= 1`.

## When / how to apply

1. Identify **shared mutable** nouns (inventory, seats, balances, drivers).
2. State the bad interleaving in one sentence.
3. Choose the simplest fix that preserves the invariant (mutex → optimistic version → queue).
4. Add idempotency keys on payment/checkout/transfer APIs.

## Pitfalls

- Global lock over the whole app — correct but kills concurrency; prefer keyed locks.
- Forgetting deadlock potential when locking two accounts.
- Holding locks during slow I/O / observer callbacks.
- Soft UI checks without server-side atomic reserve.

## Interview trigger

> “Two checkouts can race on the last unit — I’d reserve with an atomic decrement or per-SKU lock, and make checkout idempotent.”

## Exercise

Pick **BookMyShow seat hold** or **wallet transfer**: write the race, the invariant, and 5 lines of lock/CAS pseudocode. Say how TTL holds avoid permanent leaks.
