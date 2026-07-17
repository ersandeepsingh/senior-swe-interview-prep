# Actor Model

> **One mailbox per actor** — state is owned by a single goroutine/thread; others communicate only via **messages** (no shared mutable state).

## Plain English

Each account (actor) has its own inbox. All deposits and withdrawals are messages processed **one at a time** in order. No other thread touches the balance directly — no balance races.

## Simple analogy

Bank teller with a personal queue: customers line up at *their* teller’s window; the teller updates the ledger alone. No two tellers edit the same ledger page.

## Why seniors get asked this

Digital wallets, chat rooms, game entities, order-per-user serialization — seniors explain how actors avoid locks and where mailboxes can still backlog (backpressure).

## Good: actor with mailbox

### Python

```python
import queue
import threading
from dataclasses import dataclass


@dataclass(frozen=True)
class Deposit:
    amount: int


@dataclass(frozen=True)
class Withdraw:
    amount: int


@dataclass(frozen=True)
class BalanceReply:
    balance: int


class AccountActor:
    def __init__(self) -> None:
        self._inbox: queue.Queue = queue.Queue()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        balance = 0
        while True:
            msg = self._inbox.get()
            if msg is None:
                return
            if isinstance(msg, Deposit):
                balance += msg.amount
            elif isinstance(msg, Withdraw):
                if msg.amount > balance:
                    raise ValueError("insufficient funds")
                balance -= msg.amount
            elif isinstance(msg, tuple) and msg[0] == "balance":
                _, reply_q = msg
                reply_q.put(BalanceReply(balance))

    def deposit(self, amount: int) -> None:
        self._inbox.put(Deposit(amount))

    def balance(self) -> int:
        reply_q: queue.Queue[BalanceReply] = queue.Queue(maxsize=1)
        self._inbox.put(("balance", reply_q))
        return reply_q.get().balance

    def stop(self) -> None:
        self._inbox.put(None)
        self._thread.join()
```

Messages are immutable dataclasses; only the actor thread mutates `balance`.

### Go

```go
package main

import (
    "context"
    "fmt"
)

type Deposit struct{ Amount int }
type Withdraw struct{ Amount int }
type BalanceRequest struct{ Reply chan int }

type AccountActor struct {
    inbox chan any
}

func NewAccountActor(ctx context.Context) *AccountActor {
    a := &AccountActor{inbox: make(chan any, 8)}
    go a.run(ctx)
    return a
}

func (a *AccountActor) run(ctx context.Context) {
    balance := 0
    for {
        select {
        case <-ctx.Done():
            return
        case msg := <-a.inbox:
            switch m := msg.(type) {
            case Deposit:
                balance += m.Amount
            case Withdraw:
                if m.Amount > balance {
                    fmt.Println("insufficient funds")
                    continue
                }
                balance -= m.Amount
            case BalanceRequest:
                m.Reply <- balance
            }
        }
    }
}

func (a *AccountActor) Deposit(amount int) { a.inbox <- Deposit{Amount: amount} }

func (a *AccountActor) Balance(ctx context.Context) (int, error) {
    reply := make(chan int, 1)
    select {
    case <-ctx.Done():
        return 0, ctx.Err()
    case a.inbox <- BalanceRequest{Reply: reply}:
    }
    select {
    case <-ctx.Done():
        return 0, ctx.Err()
    case b := <-reply:
        return b, nil
    }
}

func main() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()
    acc := NewAccountActor(ctx)
    acc.Deposit(100)
    fmt.Println(acc.Balance(ctx))
}
```

Pass `context` for cancellation; bounded `inbox` applies backpressure if the actor falls behind.

## Concurrency safety

| Concern | What to watch |
|---------|----------------|
| **Race** | Bypassing the actor and reading shared fields — defeats the model. All access via messages. |
| **Deadlock** | Request/reply while holding actor’s synchronous call from inside the same actor (re-entrant deadlock). |
| **Backpressure** | Unbounded mailbox → memory growth if producers outpace consumer. Use bounded channels / `Queue(maxsize=...)`. |

**Python GIL:** actors still help structure and avoid shared mutable state; for CPU parallelism use multiprocessing actors or separate processes.

## When to use / not use

**Use:** per-entity serialization (one wallet, one game room); state machines with ordered events; reducing lock complexity.

**Don’t use:** simple CRUD with a DB as the serialization point; tiny shared counters (a mutex is simpler); cross-actor transactions needing atomicity across entities (need sagas / DB locks).

## Pitfalls

- Leaking direct references to actor-internal state.
- Unbounded mailboxes under burst traffic.
- Ask pattern without timeout — caller blocks forever if actor dies.
- One giant “god actor” — split by domain entity (one actor per account, not one for the whole bank).

## Interview trigger phrase

> “Each account is an **actor** with a mailbox — all mutations are messages processed serially, so we avoid shared locks on balance.”

## Exercise

**Chat room:** users join, leave, send messages; each room is independent.

1. One actor per room vs one global actor — trade-offs?
2. How do you broadcast a message to 1k users without blocking the room actor forever?
3. Room actor crashes — what do clients see?
