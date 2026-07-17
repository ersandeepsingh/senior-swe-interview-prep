# Interface Segregation Principle (ISP)

> Clients should **not be forced to depend on methods they don’t use**.

## Plain English

Don’t ship one fat interface with `print`, `scan`, `fax`, `staple` if many callers only need `print`. Split into small, focused interfaces (or protocols).

Fat interface → empty methods, `NotImplementedError`, or fake no-ops — that’s a smell (and often LSP pain too).

## Why seniors get asked this

In LLD, someone dumps everything on `IDevice` / `IRepository`. Interviewers ask: “Does a read-only report really need `delete`?”

## Bad: one fat interface

### Python

```python
from abc import ABC, abstractmethod


class Machine(ABC):
    @abstractmethod
    def print(self, doc: str) -> None: ...

    @abstractmethod
    def scan(self) -> str: ...

    @abstractmethod
    def fax(self, number: str) -> None: ...


class SimplePrinter(Machine):
    def print(self, doc: str) -> None:
        print(f"Printing: {doc}")

    def scan(self) -> str:
        raise NotImplementedError("no scanner")  # forced by fat interface

    def fax(self, number: str) -> None:
        raise NotImplementedError("no fax")
```

### Go

```go
type Machine interface {
    Print(doc string)
    Scan() string
    Fax(number string)
}

type SimplePrinter struct{}

func (SimplePrinter) Print(doc string) { fmt.Println("Printing:", doc) }
func (SimplePrinter) Scan() string     { panic("no scanner") }
func (SimplePrinter) Fax(number string) { panic("no fax") }
```

## Good: small interfaces, compose as needed

### Python

```python
from abc import ABC, abstractmethod


class Printer(ABC):
    @abstractmethod
    def print(self, doc: str) -> None: ...


class Scanner(ABC):
    @abstractmethod
    def scan(self) -> str: ...


class Fax(ABC):
    @abstractmethod
    def fax(self, number: str) -> None: ...


class SimplePrinter(Printer):
    def print(self, doc: str) -> None:
        print(f"Printing: {doc}")


class MultiFunctionDevice(Printer, Scanner, Fax):
    def print(self, doc: str) -> None:
        print(f"MFD print: {doc}")

    def scan(self) -> str:
        return "scanned-page"

    def fax(self, number: str) -> None:
        print(f"Fax to {number}")


def send_to_office_printer(p: Printer, doc: str) -> None:
    p.print(doc)  # only needs Printer — no scan/fax required
```

### Go

```go
type Printer interface {
    Print(doc string)
}

type Scanner interface {
    Scan() string
}

type Faxer interface {
    Fax(number string)
}

type SimplePrinter struct{}
func (SimplePrinter) Print(doc string) { fmt.Println("Printing:", doc) }

type MultiFunctionDevice struct{}
func (MultiFunctionDevice) Print(doc string) { fmt.Println("MFD print:", doc) }
func (MultiFunctionDevice) Scan() string     { return "scanned-page" }
func (MultiFunctionDevice) Fax(number string) { fmt.Println("Fax to", number) }

func SendToOfficePrinter(p Printer, doc string) {
    p.Print(doc)
}
```

Go naturally encourages ISP: **accept the smallest interface the function needs**.

## Interview trigger phrase

> “I’d split this into role interfaces so implementers aren’t forced to stub methods they don’t support.”

## Exercise

Design a parking-lot system with: `Car`, `Bike`, and a `AdminConsole` that can `assignSpot`, `releaseSpot`, and `generateRevenueReport`.

1. What fat interface would a junior invent?
2. Split into 2–3 interfaces: who implements what?
3. Write a Go function signature that takes only what it needs for “park a vehicle.”
