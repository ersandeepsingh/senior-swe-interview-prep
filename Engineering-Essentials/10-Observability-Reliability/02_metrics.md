# Metrics

> Numbers over time — cheap to store, perfect for *"is it broken?"* and alerting. Not a replacement for logs or traces.

## Plain English

A metric is a measurement: request rate, error rate, latency percentiles, CPU, queue depth. Tools like **Prometheus** scrape or receive them; **Grafana** graphs them.

```text
  Alert path:
    http_requests_errors / http_requests_total  > 1% for 5m
         ↓
    Page on-call  (metric told you "broken")
         ↓
    Trace + logs  (find where / why)
```

Prefer **histograms/summaries** for latency (so you can compute percentiles), not a single average. Averages hide the p99 that users feel.

## Essentials (must-know for this topic)

### RED vs USE

| Lens | Stands for | Best for |
|------|------------|----------|
| **RED** | **R**ate, **E**rrors, **D**uration | Request-driven services (APIs, workers handling jobs) |
| **USE** | **U**tilization, **S**aturation, **E**rrors | Resources (CPU, disk, connection pools, queues) |

| RED signal | What you measure |
|------------|------------------|
| Rate | Requests/sec (or jobs/sec) |
| Errors | Failed requests/sec or % |
| Duration | Latency — prefer **p50 / p95 / p99**, not only avg |

| USE signal | What you measure |
|------------|------------------|
| Utilization | % busy (CPU, disk, pool in use) |
| Saturation | Queue depth / wait time / “how much extra work waiting” |
| Errors | Hardware/soft failures on that resource |

**Rule of thumb:** RED for “is the service OK?” · USE for “is the machine/pool the bottleneck?”

### Metric types & cardinality

| Type | Use |
|------|-----|
| **Counter** | Monotonically increasing (requests total) |
| **Gauge** | Up/down value (queue depth, goroutines) |
| **Histogram / summary** | Distributions → percentiles |

| Labels | Safe? |
|--------|-------|
| `service`, `route`, `status` | Yes — low cardinality |
| `user_id`, `order_id`, raw path with IDs | **No** — cardinality explosion |

## Simple example

```text
# Prometheus-style
http_requests_total{service="checkout", status="200"} 18420
http_requests_total{service="checkout", status="500"} 37
http_request_duration_seconds_bucket{le="0.1"} 12000
http_request_duration_seconds_bucket{le="0.5"} 18000
http_request_duration_seconds_bucket{le="1.0"} 18350
```

Dashboard: error rate = 500s / total. Latency panel shows p99 climbing while p50 is flat → few slow outliers, not “everything is slow.”

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Low-cardinality labels (`service`, `route`, `status`) | Cheap, stable series | Can't slice by user |
| High-cardinality (`user_id`, `order_id`) as labels | Fine-grained | Cardinality explosion, $$ / OOM |
| RED dashboards per service | Consistent on-call view | Still need traces for *where* |
| Alert on metrics only | Fast detection | No root-cause detail |

## Pitfalls

- **Average latency** as the only number — one slow 1% ruins UX while avg looks fine.
- **Unbounded labels** — `path=/users/12345` creates millions of time series.
- **Alerting on CPU alone** — CPU can be fine while error rate is on fire (and vice versa). Prefer **user-facing SLIs**.
- **No golden signals** — custom vanity graphs nobody pages on.

## Interview trigger phrase

> “I'd instrument **RED** for each service — rate, errors, duration percentiles — with **low-cardinality** labels, and alert on SLI burn, not raw CPU.”

## Exercise

Checkout p99 jumps from 200ms to 2s; p50 is unchanged. What does that suggest, and which **one** metric label would you check first on the latency histogram?
