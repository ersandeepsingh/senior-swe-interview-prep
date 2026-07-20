# Classic Interview Gotchas — Senior Go Prep

Memorize these. Each note is **broken → fixed** with the trigger phrase you’ll say out loud.

| # | Gotcha | File |
|---|--------|------|
| 1 | Loop variable capture | [01_loop_variable_capture.md](01_loop_variable_capture.md) |
| 2 | nil interface ≠ nil | [02_nil_interface.md](02_nil_interface.md) |
| 3 | Slice `append` aliasing | [03_slice_append_aliasing.md](03_slice_append_aliasing.md) |
| 4 | Map iteration order | [04_map_iteration_order.md](04_map_iteration_order.md) |
| 5 | `defer` in a loop | [05_defer_in_loop.md](05_defer_in_loop.md) |
| 6 | Range copies values | [06_range_copies_values.md](06_range_copies_values.md) |
| 7 | Comparing structs/slices/maps | [07_comparing_structs_slices_maps.md](07_comparing_structs_slices_maps.md) |
| 8 | Buffered vs unbuffered deadlocks | [08_buffered_vs_unbuffered_deadlocks.md](08_buffered_vs_unbuffered_deadlocks.md) |
| 9 | Goroutine leak from unread channel | [09_goroutine_leak_unread_channel.md](09_goroutine_leak_unread_channel.md) |
| 10 | `time.After` in `select` loops | [10_time_after_in_select.md](10_time_after_in_select.md) |

**How to study:** cover the fixed version → explain the bug from the broken snippet alone → recite the trigger phrase.
