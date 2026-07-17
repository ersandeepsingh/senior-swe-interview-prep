# Template Method

> Define the **skeleton of an algorithm** in a base class; let subclasses override specific steps without changing the structure.

## Plain English

“Import data” always: open → parse → validate → save. CSV and JSON share the skeleton but override `parse`. The base class owns the sequence; subclasses own the varying steps.

## Why seniors get asked this

Data pipelines, report generation, game turns — fixed workflow with customizable hooks. Interviewers check you don’t copy-paste the whole algorithm.

## Real-world analogy

A **cake recipe card**: same steps (mix → bake → cool); chocolate vs vanilla only changes the “mix ingredients” step.

## Example

### Python

```python
from abc import ABC, abstractmethod


class DataImporter(ABC):
    def import_file(self, path: str) -> None:  # template
        raw = self.read(path)
        rows = self.parse(raw)
        self.validate(rows)
        self.save(rows)

    def read(self, path: str) -> str:
        return f"content:{path}"

    @abstractmethod
    def parse(self, raw: str) -> list[dict]: ...

    def validate(self, rows: list[dict]) -> None:
        if not rows:
            raise ValueError("empty")

    def save(self, rows: list[dict]) -> None:
        print(f"saved {len(rows)} rows")


class CsvImporter(DataImporter):
    def parse(self, raw: str) -> list[dict]:
        return [{"line": raw, "fmt": "csv"}]


class JsonImporter(DataImporter):
    def parse(self, raw: str) -> list[dict]:
        return [{"line": raw, "fmt": "json"}]


CsvImporter().import_file("a.csv")
```

### Go

```go
// Go prefers composition: define the varying step as a function/strategy
// rather than classical inheritance. Template Method intent still holds.

type Parser func(raw string) []map[string]string

func ImportFile(path string, parse Parser) {
    raw := "content:" + path
    rows := parse(raw)
    if len(rows) == 0 {
        panic("empty")
    }
    fmt.Printf("saved %d rows\n", len(rows))
}

func ParseCSV(raw string) []map[string]string {
    return []map[string]string{{"line": raw, "fmt": "csv"}}
}

// ImportFile("a.csv", ParseCSV)
```

In Go, prefer passing the varying step (or a small interface) over deep class hierarchies — same “fixed skeleton” idea.

## When to use

- Algorithm structure is stable; a few steps vary.
- You want to enforce “don’t skip validate” in one place.
- Shared before/after hooks (logging, timing) around custom steps.

## When not to use / pitfalls

- Inheritance-heavy Template Method can get brittle; Strategy + a plain function pipeline may be clearer (especially Go).
- Subclasses needing to change the *order* of steps → wrong pattern.
- Too many protected hooks → fragile base class problem.
- Don’t confuse with **Strategy** (swap whole algorithm object) vs Template (inherit and override steps).

## Interview trigger phrase

> “The import pipeline is fixed — I’d put the skeleton in a template and only override parse for CSV vs JSON.”

## Exercise

Game turn: `rollDice → move → applyEffect → checkWin`. Human and AI differ only in `chooseMove`.

1. Sketch the template method and the hook.
2. Would Strategy for `chooseMove` be better? Why might yes?
3. How would you express this idiomatically in Go?
