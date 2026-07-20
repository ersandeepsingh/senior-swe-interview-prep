# Error Handling — Senior Go Interview Prep

Go treats errors as values: explicit returns, wrapping for context, and panic only for truly unrecoverable situations. Interviewers care that you check errors, wrap with stack/context, and choose sentinel vs typed errors deliberately.

| # | Topic | File |
|---|-------|------|
| 1 | `error` interface | [01_error_interface.md](01_error_interface.md) |
| 2 | Creating errors | [02_creating_errors.md](02_creating_errors.md) |
| 3 | Error wrapping | [03_error_wrapping.md](03_error_wrapping.md) |
| 4 | Sentinel vs typed errors | [04_sentinel_vs_typed_errors.md](04_sentinel_vs_typed_errors.md) |
| 5 | `panic` / `recover` | [05_panic_recover.md](05_panic_recover.md) |
| 6 | Error handling idioms | [06_error_handling_idioms.md](06_error_handling_idioms.md) |
| 7 | Custom error types | [07_custom_error_types.md](07_custom_error_types.md) |

**How to study:** for each topic, rewrite a small API that returns errors, then explain how a caller uses `errors.Is` / `errors.As` without string-matching.
