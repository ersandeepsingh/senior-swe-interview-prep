# Interpreter

> Given a language, define a representation for its grammar along with an **interpreter** that uses the representation to evaluate sentences.

## Plain English

Build a tiny language: rules, filters, math expressions. Map grammar to classes (`And`, `Or`, `Literal`) and evaluate an expression tree. Not for full programming languages — for small DSLs.

## Why seniors get asked this

Rule engines, entitlement expressions, search filters (“status:open AND assignee:me”). Seniors scope it: simple grammar, or else use a real parser library.

## Real-world analogy

A **pocket calculator**: you enter an expression; the device interprets symbols according to fixed rules and returns a value.

## Example

### Python

```python
from abc import ABC, abstractmethod


class Expr(ABC):
    @abstractmethod
    def interpret(self, ctx: dict[str, int]) -> bool: ...


class NumberGT(Expr):
    def __init__(self, key: str, n: int) -> None:
        self.key, self.n = key, n

    def interpret(self, ctx: dict[str, int]) -> bool:
        return ctx.get(self.key, 0) > self.n


class And(Expr):
    def __init__(self, left: Expr, right: Expr) -> None:
        self.left, self.right = left, right

    def interpret(self, ctx: dict[str, int]) -> bool:
        return self.left.interpret(ctx) and self.right.interpret(ctx)


# age > 18 AND score > 70
rule: Expr = And(NumberGT("age", 18), NumberGT("score", 70))
print(rule.interpret({"age": 20, "score": 80}))  # True
print(rule.interpret({"age": 16, "score": 90}))  # False
```

### Go

```go
type Expr interface {
    Interpret(ctx map[string]int) bool
}

type NumberGT struct {
    Key string
    N   int
}

func (e NumberGT) Interpret(ctx map[string]int) bool {
    return ctx[e.Key] > e.N
}

type And struct {
    Left, Right Expr
}

func (e And) Interpret(ctx map[string]int) bool {
    return e.Left.Interpret(ctx) && e.Right.Interpret(ctx)
}

rule := And{Left: NumberGT{"age", 18}, Right: NumberGT{"score", 70}}
fmt.Println(rule.Interpret(map[string]int{"age": 20, "score": 80}))
```

## When to use

- Small, stable grammars evaluated often (feature flags, pricing rules, filters).
- You want rules as data/composable objects rather than hard-coded `if`s.
- Teaching/demo of expression trees in interviews.

## When not to use / pitfalls

- Real languages need proper parsers (ANTLR, etc.) — don’t hand-roll a language.
- Grammar growth → class explosion; consider a generic AST + Visitor.
- Security: interpreting user-supplied expressions needs sandboxing.
- Performance: naive trees on hot paths may need compilation/caching.
- Often “Interpreter” in interviews is just Composite + eval — say that.

## Interview trigger phrase

> “I’d model filter rules as an expression tree and interpret it against the context — a tiny DSL, not a full language.”

## Exercise

Support rules: `status == "OPEN"` and combine with `AND` / `OR`.

1. Sketch expression types.
2. Evaluate against `{"status": "OPEN"}`.
3. When would you stop and use a library instead?
