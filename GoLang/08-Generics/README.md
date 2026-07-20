# Generics — Senior Go Interview Prep

Generics (Go 1.18+) add type parameters to functions and types. Interviews focus less on syntax trivia and more on **when generics beat interfaces or duplication**, and on writing correct constraints.

| # | Topic | File |
|---|-------|------|
| 1 | Type parameters | [01_type_parameters.md](01_type_parameters.md) |
| 2 | Constraints | [02_constraints.md](02_constraints.md) |
| 3 | Type inference | [03_type_inference.md](03_type_inference.md) |
| 4 | When to use generics | [04_when_to_use_generics.md](04_when_to_use_generics.md) |
| 5 | Generic data structures | [05_generic_data_structures.md](05_generic_data_structures.md) |

**How to study:** implement a tiny generic `Set[T comparable]` and a `Map` helper; explain why `any` is a weak constraint and when an interface method set is enough without generics.
