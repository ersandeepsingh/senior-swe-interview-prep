# 1. Foundational Concepts

The vocabulary every HLD answer leans on. Read these before diving into classic design problems — interviewers expect you to **name the trade-off out loud**, not just draw boxes.

| # | Concept | One-line intent |
|---|---------|-----------------|
| 01 | [CAP theorem](01_cap_theorem.md) | Under a partition, pick Consistency **or** Availability |
| 02 | [PACELC](02_pacelc.md) | Even without partitions: Latency vs Consistency |
| 03 | [Consistency models](03_consistency_models.md) | Strong / eventual / causal / session guarantees |
| 04 | [Latency vs throughput](04_latency_vs_throughput.md) | Optimize p99 vs QPS — they pull apart |
| 05 | [Availability math](05_availability_math.md) | Nines, SLA/SLO/SLI, downtime budget |
| 06 | [Back-of-envelope estimation](06_back_of_envelope.md) | QPS, storage, bandwidth → justify later choices |
| 07 | [Vertical vs horizontal scaling](07_vertical_vs_horizontal.md) | Scale up vs scale out / sharding |
| 08 | [Stateless vs stateful services](08_stateless_vs_stateful.md) | Push state to stores → easy horizontal scale |

**How to use:** For each file — read Plain English → diagram → trade-offs → say the interview trigger phrase out loud → do the Exercise without peeking at notes.
