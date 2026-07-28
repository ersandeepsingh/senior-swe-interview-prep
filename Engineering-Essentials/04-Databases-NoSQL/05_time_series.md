# Time-Series

> Data **indexed primarily by time** — metrics, events, sensor readings — with retention, downsampling, and append-heavy writes.

## Plain English

Every point has a timestamp (+ tags/labels): `cpu_usage{host=web1} 0.72 @ 10:00:01`. TSDBs optimize range scans, compression, retention, and downsampling — not general CRUD.

## Essentials (must-know for this topic)

### Core concepts

| Concept | Meaning |
|---------|---------|
| **Measurement / metric** | Named series (`http_request_duration`) |
| **Tags / labels** | Dimensions (`route`, `status`) — indexed for filter/group |
| **Timestamp + value** | The point |
| **Retention** | Drop raw after N days |
| **Downsampling / rollup** | 1s → 1m averages for older data |
| **Cardinality** | Unique label combinations — **the** footgun |

### Engines you’ll name

| Engine | Flavor |
|--------|--------|
| **Prometheus** | Pull/scrape; PromQL; great short-term metrics |
| **InfluxDB** | Push points; Flux/InfluxQL |
| **TimescaleDB** | Postgres extension — SQL + time buckets |
| **OpenTSDB / VictoriaMetrics / …** | Variants; same ideas |

### Cardinality rules

| OK labels | Dangerous labels |
|-----------|------------------|
| `route`, `method`, `status_class` | `user_id`, `email`, raw `request_id` |
| Bounded enums | Unbounded IDs → memory bomb |

### Retention plan (say it)

| Tier | Example |
|------|---------|
| Raw | 15 days at 15s resolution |
| Downsampled | 1 year at 5m aggregates |
| Don’t | Infinite raw forever |

Append-heavy; avoid frequent updates to old points.

## Why seniors get asked

Observability and IoT designs need time-series literacy: cardinality explosions and retention are classic footguns.

## Simple example

```promql
# Prometheus: avg CPU by instance, last 5 minutes
avg by (instance) (rate(node_cpu_seconds_total[5m]))
```

```sql
-- TimescaleDB-ish
SELECT time_bucket('1 minute', ts) AS minute,
       avg(value)
FROM metrics
WHERE name = 'latency_ms' AND ts > now() - interval '1 hour'
GROUP BY minute
ORDER BY minute;
```

## When to use / when not / trade-offs

| Use time-series when… | Prefer regular SQL/KV when… |
|-----------------------|----------------------------|
| Metrics, logs sampling, IoT | Business entities (orders, users) |
| Need retention/downsample | Complex relational updates |
| Append-only high ingest | Frequent updates to old points |

**Trade-offs:** incredible ingest + compression vs high **cardinality** (too many unique label combos) melting memory; not a general app DB.

## Common pitfalls

- Unbounded labels (`user_id` on every metric) → cardinality bomb  
- No retention → disk fills  
- Using Prometheus as long-term durable warehouse without remote storage  
- Updating historical points heavily  

## Interview trigger phrase

> “I’d store metrics in a TSDB with retention and downsampling — and keep label cardinality under control.”

## Exercise

Design metrics for API latency per route. Which labels are OK? Which label would you refuse? Propose a 15d raw + 1y downsampled retention plan.
