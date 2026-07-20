# Pointers & Memory — Senior Go Interview Prep

Seniors explain where values live and why. Escape analysis, pass-by-value headers, and nil semantics show up constantly next to concurrency.

| # | Topic | File |
|---|-------|------|
| 1 | Pointers | [01_pointers.md](01_pointers.md) |
| 2 | Stack vs heap | [02_stack_vs_heap.md](02_stack_vs_heap.md) |
| 3 | Escape analysis | [03_escape_analysis.md](03_escape_analysis.md) |
| 4 | Pass by value | [04_pass_by_value.md](04_pass_by_value.md) |
| 5 | Zero values & nil | [05_zero_values_and_nil.md](05_zero_values_and_nil.md) |
| 6 | `unsafe.Pointer` & `uintptr` | [06_unsafe_pointer_and_uintptr.md](06_unsafe_pointer_and_uintptr.md) |

**How to study:** read one file → sketch stack/heap for an example → say the trigger phrase out loud → do the exercise on a whiteboard (5–10 min). For memory topics, verify intuitions with `go build -gcflags='-m'`.
