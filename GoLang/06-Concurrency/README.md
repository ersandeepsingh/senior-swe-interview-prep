# Concurrency — Senior Go Interview Prep

Concurrency is the make-or-break section for senior Go interviews. Expect to write correct concurrent code *and* explain scheduling, happens-before, and failure modes (leaks, races, deadlocks).

| # | Topic | File |
|---|-------|------|
| 1 | Goroutines | [01_goroutines.md](01_goroutines.md) |
| 2 | Goroutine lifecycle & leaks | [02_goroutine_lifecycle_leaks.md](02_goroutine_lifecycle_leaks.md) |
| 3 | Channels | [03_channels.md](03_channels.md) |
| 4 | Channel semantics | [04_channel_semantics.md](04_channel_semantics.md) |
| 5 | `select` | [05_select.md](05_select.md) |
| 6 | `sync.WaitGroup` | [06_waitgroup.md](06_waitgroup.md) |
| 7 | `sync.Mutex` / `RWMutex` | [07_mutex_rwmutex.md](07_mutex_rwmutex.md) |
| 8 | `sync.Once` | [08_once.md](08_once.md) |
| 9 | `sync.Cond` | [09_cond.md](09_cond.md) |
| 10 | `sync/atomic` | [10_atomic.md](10_atomic.md) |
| 11 | `sync.Pool` | [11_pool.md](11_pool.md) |
| 12 | `context.Context` | [12_context.md](12_context.md) |
| 13 | Go memory model | [13_go_memory_model.md](13_go_memory_model.md) |
| 14 | Concurrency patterns | [14_concurrency_patterns.md](14_concurrency_patterns.md) |
| 15 | Race conditions & `-race` | [15_race_conditions.md](15_race_conditions.md) |
| 16 | Deadlocks / livelocks | [16_deadlocks_livelocks.md](16_deadlocks_livelocks.md) |
| 17 | Channels vs mutexes | [17_channels_vs_mutexes.md](17_channels_vs_mutexes.md) |

**How to study:** read one file → rewrite the example from memory → say the trigger phrase out loud → do the exercise on a whiteboard (5–10 min). For concurrency, always ask yourself: *who owns this data, who closes this channel, and how does every goroutine exit?*
