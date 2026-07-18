# Design a Logging / Analytics Pipeline 🔴

> **Crux:** Stream-ingest massive logs, process (parse/enrich/aggregate) in near real time, then **tier storage** (hot → warm → cold) for cost-efficient query.

## Clarify (say this first)

**Functional**
- Collect logs from services/apps; ship to central pipeline
- Parse/structure (JSON), enrich (geo, service meta), filter PII
- Real-time dashboards + ad-hoc search (Kibana-style) + long-term analytics
- Alerts on error-rate patterns optional

**Non-functional**
- Huge write volume; bursty (incidents)
- Durability: at-least-once collect; searchable within seconds–minutes
- Cost: cannot keep all raw forever on SSD/ES
- Multi-tenant isolation if SaaS

## Back-of-envelope

```text
Assumptions: 5K hosts × 2 KB/s logs ≈ 10 MB/s ≈ 1 TB/day
Larger: 100 TB/day enterprise common
Index everything in ES: expensive — typically hot 7d, warm 30d, cold object store
Peak 5–10× avg during outages — buffer must absorb
Query: recent search ≫ historical scan
```

## API + data model

```text
Agents → OTLP / syslog / HTTP ingest
GET  /search?q=&from=&to=&service=
GET  /analytics/aggregate?dims&metric
Admin retention policies per index / tenant
```

| Tier | Store | Retention | Query |
|------|-------|-----------|-------|
| Buffer | Kafka | days | Replay |
| Hot | ES / ClickHouse | 3–7d | Full-text / fast agg |
| Warm | Cheaper disks / fewer replicas | 30d | Slower search |
| Cold | Object store (S3) + Parquet | months–years | Batch / Athena |

## High-level architecture

```text
Apps → Collector agents → Kafka (topics by service/env)
                              │
                     Stream processors
                     (parse, enrich, drop, sample)
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
         Hot search      Real-time agg    Cold lake
         (ES/CH)         (alerts)         (S3/Parquet)
```

## Deep dive: the crux

**Stream processing**
- Consumers parse/validate; schema registry optional
- Enrich from side inputs (service catalog); redact PII early
- Split paths: **index subset** for search vs **all structured events** to lake
- Sampling: keep 100% errors, sample debug

**Storage tiering**

| Strategy | When |
|----------|------|
| ILM on Elasticsearch | Already on ELK |
| Hot ClickHouse + S3 cold | Analytics-heavy, cheaper agg |
| Kafka → lake only + sparse index | Cost-first; weaker “grep last hour” |

**Query routing:** UI picks hot store for recent; federate or “restore from cold” for old ranges. Don’t pretend cold is as fast as hot.

**Backpressure:** agents buffer to disk; Kafka retains; drop lowest-priority debug if pipeline saturated — say it explicitly.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Index all fields | Flexible search | Exploding index cost |
| Structured + cold lake | Cheap history | Slow ad-hoc grep on old data |
| Heavy sampling | Survive peaks | Blind spots in debug |
| Exactly-once processing | Clean counts | Complexity (usually at-least-once + dedup) |

## Failure modes & scale

- **Incident log storm:** auto-sample; priority topics for `error`/`fatal`
- **Bad parser / poison message:** DLQ; don’t block partition forever
- **ES cluster meltdown:** ingest to Kafka/S3 first; pause indexing
- **PII leak:** redact at collector; audit enrichment
- **Schema chaos:** require `service`, `level`, `ts`; evolve fields carefully

## Interview trigger phrase

> “I’d buffer logs in Kafka, run stream jobs to parse/enrich and fan out to a hot search store plus a cheap cold lake, with ILM/tiering so recent logs are greppable and history is Parquet on object storage — sampling under storm to protect the pipeline.”

## Exercise

1. How do you keep **p99 ingest agent** latency low when Kafka is slow?
2. Design a policy: **100% payment-service logs** vs **1% debug** for a chatty edge service.
3. Compare **ELK** vs **ClickHouse + S3** for this problem — what would you pick for a metrics-adjacent analytics team?
