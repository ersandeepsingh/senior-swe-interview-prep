# Concurrency Patterns — Senior LLD Prep

These patterns are **often the deciding round** for senior loops. Interviewers want you to name races, deadlocks, and backpressure — not just spawn threads.

| # | Pattern | File |
|---|---------|------|
| 1 | Producer–Consumer | [01_producer_consumer.md](01_producer_consumer.md) |
| 2 | Thread Pool / Executor | [02_thread_pool_executor.md](02_thread_pool_executor.md) |
| 3 | Read-Write Lock | [03_read_write_lock.md](03_read_write_lock.md) |
| 4 | Future / Promise | [04_future_promise.md](04_future_promise.md) |
| 5 | Monitor / mutex / semaphore | [05_monitor_mutex_semaphore.md](05_monitor_mutex_semaphore.md) |
| 6 | Double-checked locking | [06_double_checked_locking.md](06_double_checked_locking.md) |
| 7 | Immutability for safety | [07_immutability_for_safety.md](07_immutability_for_safety.md) |
| 8 | Actor model | [08_actor_model.md](08_actor_model.md) |

**How to study:** read one file → explain the analogy out loud → spot the race/deadlock in the “bad” example → answer the exercise (3–5 min).

**GIL reminder (Python):** CPython’s GIL lets only one thread run Python bytecode at a time per process. It can make some *small* updates look atomic, but it does **not** remove data races — always protect shared mutable state.
