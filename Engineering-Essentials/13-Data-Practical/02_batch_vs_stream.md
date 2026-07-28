# Batch vs Stream Processing

> **Batch** processes bounded data on a schedule (hours of logs nightly). **Stream** processes unbounded events continuously (click → update dashboard in seconds). Many systems are **both** (Lambda architecture / unified engines).

## Plain English

Don't force everything into streaming — nightly reconciliations and large joins are often cheaper and clearer as batch. Hybrid is common: stream into a lake; batch curated models.

```text
  Batch:   S3 logs (daily) → Spark job → warehouse tables → BI
  Stream:  Kafka clicks → Flink aggregate → Redis dashboard + sink to lake
  Hybrid:  stream into lake continuously; batch jobs build curated models
```

## Essentials (must-know for this topic)

### Batch vs stream

| | **Batch** | **Stream** |
|---|-----------|------------|
| Input | Finite files/tables/partitions | Unbounded event feed |
| Latency | Minutes–hours (OK) | Seconds–ms (goal) |
| Tools | Spark, dbt, BigQuery scheduled jobs | Kafka + Flink/Spark Streaming/Kafka Streams, Kinesis |
| Classic | ETL / ELT overnight | Fraud, alerts, personalization |

### ETL vs ELT

| | ETL | ELT |
|---|-----|-----|
| Order | Extract → **Transform** → Load | Extract → **Load** → Transform in warehouse |
| Modern default | Older warehouses | Cloud warehouses with cheap storage/compute |

### Stream concepts interviewers expect

| Term | Meaning |
|------|---------|
| **Event time vs processing time** | When it happened vs when you saw it |
| **Watermark** | Heuristic “how late can data still be?” |
| **Micro-batch** | Process every 1–5 min — middle ground |
| **Exactly-once sink** | Still need idempotent writes in practice |

**Rule:** stream when SLA needs seconds; batch when optimizing throughput and complex joins.

## Simple example

Fraud detection:

- **Stream:** score each payment as it happens; block in < 1s.
- **Batch:** nightly retrain model on yesterday's labeled fraud; recompute risk features for reporting.

Don't force everything into streaming — nightly reconciliations and large joins are often cheaper and clearer as batch.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Batch | Simple ops, efficient big joins | High latency; stale decisions |
| Stream | Low latency reactions | State, exactly-once sinks, ops complexity |
| Micro-batch (every 1–5 min) | Middle ground | Still not true event-time edge cases |
| Unified engine (Spark/Flink both) | One skillset | Deep expertise still needed per mode |

## Pitfalls

- **Streaming for vanity** when a 15-minute batch meets the SLA.
- **Ignoring event-time vs processing-time** — late events break naive windows.
- **No watermark / late-data policy**.
- **Dual pipelines that diverge** (Lambda) without reconciliation.
- **Exactly-once sink assumptions** — idempotent writes still needed.

## Interview trigger phrase

> “I'd stream when the **SLA needs seconds**, and batch when I'm optimizing **throughput and complex joins** — often stream into a lake and batch the curated warehouse models.”

## Exercise

Product analytics wants “active users last 5 minutes” and “monthly retention cohorts.” Which is stream, which is batch, and what storage would you sink each into?
