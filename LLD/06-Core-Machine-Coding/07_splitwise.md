# Splitwise

> Expense splitting, balances, settle-up → **Strategy (split types) + graph settle**. 🔴

## Scope / Requirements

**In scope**
- Users, groups (optional), expenses with split types: equal, exact, percent.
- Maintain pairwise balances (who owes whom).
- Show balances; simplify debts (settle-up / minimize transactions).

**Out of scope**
- Real payments, currency FX, recurring expenses, chat.

**Domain invariants**
- For an expense, sum(shares) == amount (exact cents — careful with rounding).
- Percent splits sum to 100%; equal splits divide with remainder policy (give leftover cents to first users).
- Balance is antisymmetric: `bal(A,B) = -bal(B,A)` (store one side or net ledger).
- Settle-up does not change net worth of anyone — only consolidates edges.

## Core Entities & Responsibilities

| Entity | Responsibility |
|--------|----------------|
| `User` | Id, name. |
| `Expense` | Amount, paidBy, participants, split type + metadata. |
| `SplitStrategy` | Compute `user → share`. |
| `BalanceSheet` | Net receivables between users. |
| `ExpenseService` | Add expense, update balances. |
| `Settler` | Minimize cash flows from nets. |

## Key Interfaces / Patterns

- **Strategy — `SplitStrategy`:** equal/exact/percent — open for “shares” later.
- **Graph / greedy settle:** compute net credit/debit, match debtors to creditors.
- **Facade:** `SplitwiseApp` over ledger + groups if UI-facing.

## End-to-End Flow

1. A pays 900 for A,B,C equal → each owes 300; B→A 300, C→A 300 (A’s net +600).
2. Query balances.
3. Settle-up: suggest B pays A 300, C pays A 300 (or fewer txns if more users).

## Python Skeleton

```python
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class Expense:
    expense_id: str
    amount: int  # cents
    paid_by: str
    participants: list[str]
    splits: dict[str, int]  # user -> share cents


class SplitStrategy(ABC):
    @abstractmethod
    def split(self, amount: int, participants: list[str], meta: dict) -> dict[str, int]: ...


class EqualSplit(SplitStrategy):
    def split(self, amount: int, participants: list[str], meta: dict) -> dict[str, int]:
        n = len(participants)
        base, rem = divmod(amount, n)
        out = {u: base for u in participants}
        for i in range(rem):
            out[participants[i]] += 1  # remainder cents
        return out


class ExactSplit(SplitStrategy):
    def split(self, amount: int, participants: list[str], meta: dict) -> dict[str, int]:
        shares: dict[str, int] = meta["shares"]
        if sum(shares.values()) != amount:
            raise ValueError("shares must sum to amount")
        return shares


class PercentSplit(SplitStrategy):
    def split(self, amount: int, participants: list[str], meta: dict) -> dict[str, int]:
        pct: dict[str, float] = meta["percent"]
        if abs(sum(pct.values()) - 100.0) > 1e-6:
            raise ValueError("percent must sum 100")
        raw = {u: amount * pct[u] / 100.0 for u in participants}
        floors = {u: int(raw[u]) for u in participants}
        rem = amount - sum(floors.values())
        # assign leftover to largest fractional parts
        order = sorted(participants, key=lambda u: raw[u] - floors[u], reverse=True)
        for i in range(rem):
            floors[order[i]] += 1
        return floors


class BalanceSheet:
    def __init__(self):
        # bal[a][b] > 0 means b owes a
        self._bal: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def add_expense(self, paid_by: str, shares: dict[str, int]) -> None:
        for user, share in shares.items():
            if user == paid_by:
                continue
            self._bal[paid_by][user] += share
            self._bal[user][paid_by] -= share

    def net_balances(self) -> dict[str, int]:
        net: dict[str, int] = defaultdict(int)
        for a, m in self._bal.items():
            for b, v in m.items():
                if v > 0:
                    net[a] += v
                    net[b] -= v
        return dict(net)


def simplify(net: dict[str, int]) -> list[tuple[str, str, int]]:
    """Return list of (from_debtor, to_creditor, amount)."""
    debtors = [[u, -amt] for u, amt in net.items() if amt < 0]
    creditors = [[u, amt] for u, amt in net.items() if amt > 0]
    debtors.sort(key=lambda x: x[1])
    creditors.sort(key=lambda x: x[1])
    i = j = 0
    txns = []
    while i < len(debtors) and j < len(creditors):
        d_user, d_amt = debtors[i]
        c_user, c_amt = creditors[j]
        pay = min(d_amt, c_amt)
        txns.append((d_user, c_user, pay))
        debtors[i][1] -= pay
        creditors[j][1] -= pay
        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1
    return txns


class ExpenseService:
    def __init__(self, strategies: dict[str, SplitStrategy]):
        self.strategies = strategies
        self.sheet = BalanceSheet()
        self.expenses: list[Expense] = []
        self._seq = 0

    def add(self, amount: int, paid_by: str, participants: list[str], kind: str, meta: dict | None = None) -> Expense:
        shares = self.strategies[kind].split(amount, participants, meta or {})
        self.sheet.add_expense(paid_by, shares)
        self._seq += 1
        e = Expense(f"E{self._seq}", amount, paid_by, participants, shares)
        self.expenses.append(e)
        return e
```

## Go Skeleton

```go
package splitwise

import "errors"

type SplitStrategy interface {
    Split(amount int, participants []string, meta map[string]any) (map[string]int, error)
}

type EqualSplit struct{}

func (EqualSplit) Split(amount int, participants []string, _ map[string]any) (map[string]int, error) {
    n := len(participants)
    base, rem := amount/n, amount%n
    out := map[string]int{}
    for i, u := range participants {
        out[u] = base
        if i < rem {
            out[u]++
        }
    }
    return out, nil
}

type BalanceSheet struct {
    // bal[a][b] > 0 => b owes a
    bal map[string]map[string]int
}

func NewSheet() *BalanceSheet {
    return &BalanceSheet{bal: map[string]map[string]int{}}
}

func (s *BalanceSheet) ensure(a, b string) {
    if s.bal[a] == nil {
        s.bal[a] = map[string]int{}
    }
}

func (s *BalanceSheet) AddExpense(paidBy string, shares map[string]int) {
    for user, share := range shares {
        if user == paidBy {
            continue
        }
        s.ensure(paidBy, user)
        s.ensure(user, paidBy)
        s.bal[paidBy][user] += share
        s.bal[user][paidBy] -= share
    }
}

func (s *BalanceSheet) Nets() map[string]int {
    net := map[string]int{}
    for a, m := range s.bal {
        for b, v := range m {
            if v > 0 {
                net[a] += v
                net[b] -= v
            }
        }
    }
    return net
}

type Txn struct{ From, To string; Amount int }

func Simplify(net map[string]int) []Txn {
    type pair struct {
        u string
        a int
    }
    var debtors, creditors []pair
    for u, a := range net {
        if a < 0 {
            debtors = append(debtors, pair{u, -a})
        } else if a > 0 {
            creditors = append(creditors, pair{u, a})
        }
    }
    var out []Txn
    i, j := 0, 0
    for i < len(debtors) && j < len(creditors) {
        pay := debtors[i].a
        if creditors[j].a < pay {
            pay = creditors[j].a
        }
        out = append(out, Txn{debtors[i].u, creditors[j].u, pay})
        debtors[i].a -= pay
        creditors[j].a -= pay
        if debtors[i].a == 0 {
            i++
        }
        if creditors[j].a == 0 {
            j++
        }
    }
    return out
}

type Service struct {
    Strategies map[string]SplitStrategy
    Sheet      *BalanceSheet
}

func (s *Service) Add(amount int, paidBy string, participants []string, kind string, meta map[string]any) error {
    shares, err := s.Strategies[kind].Split(amount, participants, meta)
    if err != nil {
        return err
    }
    if sum(shares) != amount {
        return errors.New("invariant broken")
    }
    s.Sheet.AddExpense(paidBy, shares)
    return nil
}

func sum(m map[string]int) int {
    t := 0
    for _, v := range m {
        t += v
    }
    return t
}
```

## Concurrency / Consistency

- Adding expenses concurrently: lock balance sheet or use per-user actor / serial ledger append.
- Store immutable expense events; derive balances (event sourcing lite) for auditability.

## Extensions / Trade-offs / Pitfalls

- Rounding pennies — must document remainder rule.
- Group vs global balances; simplify within group only.
- Pitfall: updating only one direction of the pair.
- Soft delete expense → reverse ledger entry, don’t mutate history silently.

## Interview Discussion Points

- Why Strategy for splits vs switch in service?
- Is settle-up NP-hard optimally? (yes for min transactions in general — greedy is heuristic OK for interview)
- Integer cents vs floats — what bug do floats cause?

## Exercise

A pays 900 equal for A,B,C; then B pays 300 exact {B:100,C:200}. Show nets and simplify.

**Follow-ups**
1. Implement percent split with cent remainder safely.
2. Add group-scoped balances.
3. Explain how you’d reverse an expense.
