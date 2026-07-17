# Library Management

> Books, members, borrow/return, fines → **composition + repositories**. 🟡

## Scope / Requirements

**In scope**
- Catalog of books (title, ISBN); multiple copies.
- Members borrow/return; due dates; compute fines.
- Search by title/ISBN; enforce borrow limits.

**Out of scope**
- Payment gateway for fines, multi-branch logistics, full OPAC UI.

**Domain invariants**
- A `BookCopy` is Available, Borrowed, or Lost — only Available can be lent.
- One active loan per copy; return closes the loan and frees the copy.
- Member cannot exceed max active loans (e.g. 5).
- Fine = f(days overdue) via strategy; cannot “lose” domain rules inside the UI layer.

## Core Entities & Responsibilities

| Entity | Responsibility |
|--------|----------------|
| `Book` | ISBN, title, metadata (flyweight-ish catalog entry). |
| `BookCopy` | Physical copy id + status. |
| `Member` | Identity + active loan count. |
| `Loan` | Copy + member + borrowed/due/returned dates. |
| `LibraryService` | Borrow/return/search orchestration. |
| `BookRepository` / `LoanRepository` | Persistence ports (in-memory OK). |
| `FinePolicy` | Strategy for overdue calculation. |

## Key Interfaces / Patterns

- **Composition:** `Book` has many `BookCopy`; don’t inherit “FictionBook” trees.
- **Repository + DIP:** service depends on interfaces for testability.
- **Strategy — `FinePolicy`:** per-member-type or weekend rules later.

## End-to-End Flow

1. Librarian adds book + copies to catalog.
2. Member borrows available copy → create `Loan` with due date → mark copy Borrowed.
3. On return, mark Returned, free copy, if overdue apply `FinePolicy`.

## Python Skeleton

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum, auto
from typing import Optional


class CopyStatus(Enum):
    AVAILABLE = auto()
    BORROWED = auto()
    LOST = auto()


@dataclass
class Book:
    isbn: str
    title: str


@dataclass
class BookCopy:
    copy_id: str
    isbn: str
    status: CopyStatus = CopyStatus.AVAILABLE


@dataclass
class Member:
    member_id: str
    name: str
    active_loans: int = 0


@dataclass
class Loan:
    loan_id: str
    copy_id: str
    member_id: str
    borrowed: date
    due: date
    returned: Optional[date] = None


class FinePolicy(ABC):
    @abstractmethod
    def calculate(self, due: date, returned: date) -> float: ...


class PerDayFine(FinePolicy):
    def __init__(self, rate: float = 5.0):
        self.rate = rate

    def calculate(self, due: date, returned: date) -> float:
        days = (returned - due).days
        return max(0, days) * self.rate


class BookRepository(ABC):
    @abstractmethod
    def get_book(self, isbn: str) -> Optional[Book]: ...
    @abstractmethod
    def add_copy(self, copy: BookCopy) -> None: ...
    @abstractmethod
    def get_copy(self, copy_id: str) -> Optional[BookCopy]: ...
    @abstractmethod
    def find_available(self, isbn: str) -> Optional[BookCopy]: ...


class LoanRepository(ABC):
    @abstractmethod
    def save(self, loan: Loan) -> None: ...
    @abstractmethod
    def active_for_copy(self, copy_id: str) -> Optional[Loan]: ...


class LibraryService:
    def __init__(
        self,
        books: BookRepository,
        loans: LoanRepository,
        members: dict[str, Member],
        fine_policy: FinePolicy,
        loan_days: int = 14,
        max_loans: int = 5,
    ):
        self.books = books
        self.loans = loans
        self.members = members
        self.fine_policy = fine_policy
        self.loan_days = loan_days
        self.max_loans = max_loans
        self._seq = 0

    def borrow(self, member_id: str, isbn: str, on: date | None = None) -> Loan:
        on = on or date.today()
        m = self.members[member_id]
        if m.active_loans >= self.max_loans:
            raise RuntimeError("loan limit")
        copy = self.books.find_available(isbn)
        if not copy:
            raise RuntimeError("unavailable")
        copy.status = CopyStatus.BORROWED
        m.active_loans += 1
        self._seq += 1
        loan = Loan(f"L{self._seq}", copy.copy_id, member_id, on, on + timedelta(days=self.loan_days))
        self.loans.save(loan)
        return loan

    def return_copy(self, copy_id: str, on: date | None = None) -> float:
        on = on or date.today()
        loan = self.loans.active_for_copy(copy_id)
        if not loan or loan.returned:
            raise RuntimeError("no active loan")
        loan.returned = on
        copy = self.books.get_copy(copy_id)
        copy.status = CopyStatus.AVAILABLE
        self.members[loan.member_id].active_loans -= 1
        return self.fine_policy.calculate(loan.due, on)
```

## Go Skeleton

```go
package library

import (
    "errors"
    "time"
)

type CopyStatus int

const (
    Available CopyStatus = iota
    Borrowed
    Lost
)

type Book struct{ ISBN, Title string }
type BookCopy struct {
    ID, ISBN string
    Status   CopyStatus
}
type Member struct {
    ID          string
    Name        string
    ActiveLoans int
}
type Loan struct {
    ID, CopyID, MemberID string
    Borrowed, Due        time.Time
    Returned             *time.Time
}

type FinePolicy interface {
    Calculate(due, returned time.Time) float64
}

type PerDayFine struct{ Rate float64 }

func (p PerDayFine) Calculate(due, returned time.Time) float64 {
    days := int(returned.Sub(due).Hours() / 24)
    if days < 0 {
        return 0
    }
    return float64(days) * p.Rate
}

type BookRepo interface {
    FindAvailable(isbn string) (*BookCopy, error)
    GetCopy(id string) (*BookCopy, error)
}

type LoanRepo interface {
    Save(*Loan) error
    ActiveForCopy(copyID string) (*Loan, error)
}

type Service struct {
    Books     BookRepo
    Loans     LoanRepo
    Members   map[string]*Member
    Fine      FinePolicy
    LoanDays  int
    MaxLoans  int
    seq       int
}

func (s *Service) Borrow(memberID, isbn string, on time.Time) (*Loan, error) {
    m := s.Members[memberID]
    if m.ActiveLoans >= s.MaxLoans {
        return nil, errors.New("loan limit")
    }
    copy, err := s.Books.FindAvailable(isbn)
    if err != nil {
        return nil, err
    }
    copy.Status = Borrowed
    m.ActiveLoans++
    s.seq++
    loan := &Loan{
        ID: fmtLoan(s.seq), CopyID: copy.ID, MemberID: memberID,
        Borrowed: on, Due: on.AddDate(0, 0, s.LoanDays),
    }
    _ = s.Loans.Save(loan)
    return loan, nil
}

func (s *Service) Return(copyID string, on time.Time) (float64, error) {
    loan, err := s.Loans.ActiveForCopy(copyID)
    if err != nil || loan.Returned != nil {
        return 0, errors.New("no active loan")
    }
    loan.Returned = &on
    copy, _ := s.Books.GetCopy(copyID)
    copy.Status = Available
    s.Members[loan.MemberID].ActiveLoans--
    return s.Fine.Calculate(loan.Due, on), nil
}

func fmtLoan(n int) string { return "L" + string(rune('0'+n%10)) }
```

## Concurrency / Consistency

- Borrow same last copy: transaction or row lock on copy status (`AVAILABLE → BORROWED` compare-and-set).
- `active_loans` counter must update atomically with loan insert.

## Extensions / Trade-offs / Pitfalls

- Reservations/holds queue when unavailable.
- Distinguish catalog `Book` vs `BookCopy` — classic modeling trap if you only have “Book”.
- Lost books: status + open loan + replacement fine policy.

## Interview Discussion Points

- Why repository interfaces in a 45-min round? (test seams, DIP signal)
- How do you search — indexes vs scan — and where does that live?
- Member types (student/faculty) with different limits — Strategy or data-driven config?

## Exercise

Model catalog + borrow/return with a 14-day loan and ₹5/day fine.

**Follow-ups**
1. Add max renewals (1) without duplicating borrow logic.
2. Implement `find_available` with in-memory maps; discuss DB unique constraint equivalent.
3. What invariant breaks if you delete a `Book` while copies are borrowed?
