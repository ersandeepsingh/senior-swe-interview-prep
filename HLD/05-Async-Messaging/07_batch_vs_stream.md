# Batch vs Stream Processing

> **Batch** processes data in chunks on a schedule (nightly ETL). **Stream** processes events continuously as they arrive. Pick based on **freshness needs**, cost, and how wrong a slightly stale answer is.

## Plain English

| | Batch | Stream |
|---|-------|--------|
| When | Window closes (hourly/nightly) | Event arrives (seconds/ms) |
| Typical job | ETL to warehouse, daily reports | Fraud flags, live dashboards, feed ranking features |
| Failure style | Rerun the job | Retry event; watch lag |
| Cost shape | Bursty compute on schedule | Always-on consumers |

```text
  Batch                              Stream
  ─────                              ──────
  Day's logs ──► nightly job         Each click ──► continuous job
                   │                      │
                   ▼                      ▼
              Warehouse table        Running aggregate / alert
              ready by 6am           updated within seconds
```

## Simple example

**Daily revenue report:** Finance needs numbers by 8am, not per-second. Nightly batch over order tables (or load from object storage) is enough and cheaper.

**Live “orders per minute” ops dashboard / fraud spike:** Waiting until tomorrow is useless. Stream aggregates from `order_placed` events.

```text
  Fraud:  stream  →  sliding window count by card  →  block if spike
  Finance: batch  →  sum(orders) GROUP BY day     →  spreadsheet
```

Same raw orders; different freshness SLAs.

## Why prefer one over the other

| Prefer **batch** when… | Prefer **stream** when… |
|------------------------|-------------------------|
| Freshness of hours/day is fine | Decisions need seconds |
| Heavy joins / full recompute simpler | Incremental updates are natural |
| Cost / simplicity over always-on | User-visible live metrics / blocking fraud |
| Backfills and reproducible runs matter | Lag SLOs and watermarking are acceptable ops cost |

**Lambda architecture / hybrids:** Batch for correct daily truth + stream for approximate real-time; or batch backfill + stream for ongoing. Seniors name *why* both exist.

**Watermarks / late data:** streaming windows must decide when a window “closes.” Say you’d pick an allowed lateness and a reconciliation batch if money is involved.

### Real systems (interview name-drops)

- **Batch:** Spark, BigQuery scheduled queries, Airflow/dbt nightly.
- **Stream:** Flink, Kafka Streams, Spark Structured Streaming, Kinesis Analytics.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Nightly ETL | Simple ops, cheap idle time, easy recompute | Stale data all day |
| Pure streaming | Low latency insights | Always-on cost; harder exactly-once aggregates |
| Micro-batches (every 1–5 min) | Middle ground | Neither pure simplicity nor pure real-time |
| Stream everything | One mental model | Overkill for monthly invoices |

**Common interview trap:** Defaulting to Kafka+Flink for a report that finance only opens once a day.

## Interview trigger phrase

> “I’d use **batch** for nightly finance ETL and **streaming** for fraud/live counters — freshness SLA drives the choice, not fashion.”

## Exercise

**Design analytics for a food-delivery app.**

1. Courier ETA accuracy dashboard for ops (minute-level) — batch or stream? Why?  
2. Monthly seller payout reconciliation — batch or stream? Why?  
3. One sentence: how you’d backfill a week of missed stream events after an outage (hint: batch reprocess or replay).
