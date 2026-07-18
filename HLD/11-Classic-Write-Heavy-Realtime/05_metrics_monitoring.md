# Design a Metrics / Monitoring System 🔴

> **Crux:** Absorb enormous write QPS of time-series points, store them efficiently in a TSDB (rollups + retention), and evaluate alerts without drowning the ingest path.

## Clarify (say this first)

**Functional**
- Agents/SDKs push metrics (counters, gauges, histograms); label/tag dimensions
- Query: graph ranges, top-K, aggregate by tags; dashboards
- Alerting: threshold / anomaly → notify (reuse notification system)
- Multi-tenant optional (SaaS monitoring)

**Non-functional**
- Write-heavy: millions of points/s; ingest must not block apps long
- Query latency seconds OK for dashboards; alerts need low detection lag
- Retention: raw short, rollups long; cost-sensitive
- High availability of ingest; drop/sample under overload better than crash

## Back-of-envelope

```text
Assumptions: 1M series, 1 point / 10s → 100K points/s
Larger shop: 10M series × 1/s = 10M points/s
Point ~100 B compressed ~15–20 B → 10M/s ≈ 150–200 MB/s raw path
Cardinality explosion (unbounded labels) is the silent killer
Alerts: evaluate on rollup stream, not every raw point scan
```

## API + data model

```text
POST /v1/metrics/write   { series[], points[] }   // Prometheus remote-write style
GET  /v1/metrics/query   ?promql / range
POST /v1/alerts/rules
GET  /v1/alerts/firing
```

| Store | Role |
|-------|------|
| Ingest buffer | Kafka / agent WAL |
| TSDB | Time-partitioned + series index (labels → id) |
| Rollups | 1m / 5m / 1h aggregates |
| Alert state | Firing / pending in KV |

## High-level architecture

```text
Apps/Agents → Ingest gateway → Kafka
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
                 TSDB write    Rollup jobs   Alert evaluator
                    │             │             │
                 Query API ◄──────┘             ▼
                                           Notification
```

## Deep dive: the crux

**High-write ingest**
- Buffer in Kafka; batch writes to TSDB; backpressure / load-shed low-priority tenants
- Hash-shard by `metric_name + labels` hash so one series sticks to one writer (ordering)

**TSDB design ideas**
- Separate **series metadata index** (labels) from **chunks** of samples by time
- Compression (delta-of-delta, Gorilla-style) — name-drop OK
- Downsample: raw 7d → 1m for 90d → 1h for 1y

| Alerting approach | Pros | Cons |
|-------------------|------|------|
| Query TSDB on interval | Simple | Load on TSDB; lag |
| Stream evaluate on ingest/rollup | Faster, scalable | More pipeline complexity |

**Cardinality:** enforce label allowlists; drop or aggregate high-cardinality labels at ingest; hard limits per tenant.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Kafka buffer | Durability + spike absorb | Lag before queryable |
| Aggressive rollup | Cost / fast long-range query | Lose raw resolution |
| Exact every point | Fidelity | Cost; fail under storm |
| Sample under load | Survive | Blind spots |

## Failure modes & scale

- **Cardinality bomb:** detect new series rate; quarantine tenant
- **Hot series / hot partition:** split; isolate noisy metrics
- **Alert flapping:** for/pending windows; hysteresis
- **Query of death:** timeout, max series scanned, pre-agg
- **Region HA:** dual-write or replicate Kafka+TSDB; accept brief gaps

## Interview trigger phrase

> “I’d treat metrics as a write-ahead stream into a TSDB sharded by series, with rollups for retention and alerts evaluated on a stream/rollup path — and I’d hard-cap label cardinality so one bad deploy can’t take down ingest.”

## Exercise

1. How do **histograms / percentiles** change storage vs storing every raw latency sample?
2. Design multi-tenant **noisy neighbor** protection on ingest.
3. Compare pull (Prometheus scrape) vs push for a 100K-node fleet.
