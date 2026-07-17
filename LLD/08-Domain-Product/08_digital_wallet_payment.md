# Digital Wallet / Payment

> Balance, transactions, ledger — **State** + **double-entry** + **concurrency**. 🔴

## Scope / requirements

**In:** create wallet, credit/debit, transfer P2P, view ledger, idempotent operations, basic txn states (`PENDING → POSTED` / `FAILED`).

**Out:** card networks, KYC flows, multi-currency FX depth — stub currency as code on `Money`.

## Entities

| Entity | Owns |
|--------|------|
| `Wallet` / `Account` | account id, status |
| `Money` | immutable amount + currency |
| `LedgerEntry` | account, direction, amount, txn_id |
| `Transaction` | id, type, state, legs |
| `WalletService` | orchestration + locking |

## Invariants

- Sum of ledger entries for a posted txn = 0 (double-entry: debit + credit).
- Available balance = sum(posted credits) − sum(posted debits) (≥ 0 unless overdraft allowed).
- Never mutate posted entries — append-only ledger.
- Transfer is atomic across both wallets or neither.

## Interfaces / patterns — and why

| Seam | Pattern | Why |
|------|---------|-----|
| Txn lifecycle | **State** | Pending authorization vs posted |
| Money | Immutable value object | Avoid float; cents/int |
| Persistence | Repository | Ledger store |
| Per-account processing | Actor / lock ordering | Concurrency |

## End-to-end flow

1. `transfer(from, to, amount, idem_key)` → create `PENDING` txn.
2. Lock accounts in **deterministic order** → check balance → append two ledger legs → `POSTED`.
3. Replay same `idem_key` → return original result.

## Skeletons

### Python

```python
from dataclasses import dataclass
from threading import Lock


@dataclass(frozen=True)
class Money:
    cents: int
    currency: str = "INR"

    def __post_init__(self):
        if self.cents < 0:
            raise ValueError("negative")


class Ledger:
    def __init__(self):
        self.entries: list[tuple[str, int, str]] = []  # account, +/−cents, txn_id

    def balance(self, account: str) -> int:
        return sum(c for a, c, _ in self.entries if a == account)


class WalletService:
    def __init__(self):
        self.ledger = Ledger()
        self._locks: dict[str, Lock] = {}
        self._idem: dict[str, str] = {}
        self._meta_lock = Lock()

    def _lock_for(self, account: str) -> Lock:
        with self._meta_lock:
            return self._locks.setdefault(account, Lock())

    def transfer(self, src: str, dst: str, amount: Money, idem_key: str) -> str:
        if idem_key in self._idem:
            return self._idem[idem_key]
        if amount.currency != "INR":
            raise ValueError("currency")
        first, second = sorted([src, dst])
        l1, l2 = self._lock_for(first), self._lock_for(second)
        with l1:
            with l2:
                if self.ledger.balance(src) < amount.cents:
                    raise RuntimeError("insufficient funds")
                txn_id = f"txn-{len(self.ledger.entries)}"
                self.ledger.entries.append((src, -amount.cents, txn_id))
                self.ledger.entries.append((dst, amount.cents, txn_id))
                self._idem[idem_key] = txn_id
                return txn_id
```

### Go

```go
type Money struct {
    Cents    int64
    Currency string
}

type WalletService struct {
    mu     sync.Mutex // or per-account locks with ordered acquire
    ledger map[string]int64
    idem   map[string]string
}

func (s *WalletService) Transfer(src, dst string, m Money, idemKey string) (string, error) {
    s.mu.Lock()
    defer s.mu.Unlock()
    if id, ok := s.idem[idemKey]; ok {
        return id, nil
    }
    if s.ledger[src] < m.Cents {
        return "", fmt.Errorf("insufficient funds")
    }
    txnID := fmt.Sprintf("txn-%d", len(s.idem))
    s.ledger[src] -= m.Cents
    s.ledger[dst] += m.Cents
    s.idem[idemKey] = txnID
    return txnID, nil
}
```

## Concurrency / consistency

- **Lock ordering** (`min(account_id), max(...)`) prevents deadlocks on P2P transfer.
- Idempotency keys for retries after timeouts.
- Prefer ledger append + derived balance; don’t “SET balance” without journal in serious designs.
- Actor-per-account: serialize all txns for one wallet.

## Tradeoffs / pitfalls

- Floating point money — use integer minor units.
- Updating two balances without a transaction boundary.
- Missing idempotency → double spend on client retry.

## Interview prompts

- Why double-entry over a single balance field?
- How do you deadlock-proof transfers?
- Pending auth hold vs posted capture?

## Exercise / follow-ups

1. Add `hold(amount)` / `capture` / `release` for payment auth.
2. Multi-currency wallets with explicit FX txn (two pairs of legs).
3. Write a test: concurrent transfers out of one wallet never go negative.
