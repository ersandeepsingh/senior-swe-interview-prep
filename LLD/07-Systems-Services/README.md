# Systems & Services — Senior LLD Prep

Machine-coding problems that look like **infra / platform services**. Focus on algorithms behind the API, pluggable policies, and concurrency.

| # | Problem | Difficulty | Critical patterns | File |
|---|---------|------------|-------------------|------|
| 1 | Rate Limiter | 🟡 | Strategy per algorithm | [01_rate_limiter.md](01_rate_limiter.md) |
| 2 | In-Memory Key-Value Store | 🟡 | Composition + eviction | [02_in_memory_kv_store.md](02_in_memory_kv_store.md) |
| 3 | LRU / LFU Cache | 🟡 | HashMap + list; Strategy | [03_lru_lfu_cache.md](03_lru_lfu_cache.md) |
| 4 | Logging Framework | 🟡 | Chain of Responsibility + Strategy | [04_logging_framework.md](04_logging_framework.md) |
| 5 | Notification Service | 🟡 | Strategy + Observer + Factory | [05_notification_service.md](05_notification_service.md) |
| 6 | Task Scheduler / Cron | 🔴 | Priority queue + Command | [06_task_scheduler.md](06_task_scheduler.md) |
| 7 | Job Queue / Message Broker | 🔴 | Producer–Consumer + Observer | [07_job_queue.md](07_job_queue.md) |
| 8 | Distributed ID Generator | 🟡 | Concurrency + bit packing | [08_distributed_id_generator.md](08_distributed_id_generator.md) |
| 9 | URL Shortener (LLD) | 🟡 | Strategy + repository | [09_url_shortener.md](09_url_shortener.md) |
| 10 | File System (in-memory) | 🟡 | Composite | [10_file_system.md](10_file_system.md) |
| 11 | Text Editor / Undo-Redo | 🟡 | Command + Memento | [11_text_editor.md](11_text_editor.md) |

**How to study:** state the API first (`allow()`, `get/put`, `log()`, …) → pick the load-bearing algorithm → code one path → discuss threads and failure modes.

**Priority if short on time:** Rate Limiter → LRU Cache → Notification Service → Job Queue.
