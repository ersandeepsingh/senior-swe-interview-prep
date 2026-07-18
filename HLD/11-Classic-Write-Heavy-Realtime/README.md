# 11. Classic HLD — Write-Heavy / Real-Time

Write-heavy and connection-oriented designs: chat, notifications, rate limits, crawlers, metrics, and log pipelines. Interviewers probe **fan-out, ordering, distributed counters, work distribution, and high-ingest storage**.

| # | Problem | Crux | Difficulty |
|---|---------|------|------------|
| 01 | [Chat System (WhatsApp/Slack)](01_chat_system.md) | Connection mgmt + message fan-out + ordering | 🔴 |
| 02 | [Notification System](02_notification_system.md) | Async fan-out + delivery guarantees | 🟡 |
| 03 | [Distributed Rate Limiter](03_distributed_rate_limiter.md) | Distributed counters + consistency | 🟡 |
| 04 | [Web Crawler](04_web_crawler.md) | Work distribution + dedup at scale | 🔴 |
| 05 | [Metrics / Monitoring](05_metrics_monitoring.md) | High-write ingestion + time-series storage | 🔴 |
| 06 | [Logging / Analytics Pipeline](06_logging_analytics_pipeline.md) | Stream processing + storage tiering | 🔴 |

**How to use:** Clarify → estimate → API/data model → happy-path diagram → deep-dive the crux → trade-offs → failure modes. Say the interview trigger phrase out loud, then answer the Exercise without peeking.
