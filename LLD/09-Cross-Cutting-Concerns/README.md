# Cross-Cutting Concerns — Senior LLD Prep

These are the **senior differentiators**. After the happy-path skeleton, interviewers listen for whether you name the seam, the race, and how you’d test it — even if you stub the implementation.

| # | Concern | File |
|---|---------|------|
| 1 | Extensibility seams | [01_extensibility_seams.md](01_extensibility_seams.md) |
| 2 | Concurrency & consistency | [02_concurrency_consistency.md](02_concurrency_consistency.md) |
| 3 | Error handling & validation | [03_error_handling_validation.md](03_error_handling_validation.md) |
| 4 | Pluggable persistence | [04_pluggable_persistence.md](04_pluggable_persistence.md) |
| 5 | Observability hooks | [05_observability_hooks.md](05_observability_hooks.md) |
| 6 | Testability | [06_testability.md](06_testability.md) |

**How to study:** for any domain problem in §8, add one sentence per concern: where the seam is, what races, how errors surface, what you’d inject, what you’d observe, how you’d unit-test.
