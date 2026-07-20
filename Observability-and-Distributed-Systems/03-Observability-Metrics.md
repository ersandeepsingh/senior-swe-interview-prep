# 03 · Observability — Metrics

> Cheap numeric time-series for detection, trends, and alerting.

---

## Metric types

**Definition:** The four fundamental shapes of a metric — counter, gauge, histogram, summary.

**Simple explanation:**
- **Counter** — only goes up (or resets to 0). Count of things. "total requests."
- **Gauge** — goes up and down. A snapshot value. "current memory in use."
- **Histogram** — buckets observations to compute distributions/percentiles. "request latency."
- **Summary** — like a histogram but computes percentiles client-side.

**Example:**
```
requests_total            (counter)   → 45,200 and climbing
memory_bytes_in_use       (gauge)     → 512MB right now
request_duration_seconds  (histogram) → buckets: <0.1s, <0.5s, <1s, ...
```

---

## RED method

**Definition:** A metrics framework for request-driven services: **R**ate, **E**rrors, **D**uration.

**Simple explanation:** For any service that handles requests, track three things: how many requests (Rate), how many failed (Errors), and how long they took (Duration). These three answer "is my service healthy?" for almost any API.

**Example:** For the auth service:
- Rate: 1,200 req/s
- Errors: 12 req/s (1% error rate)
- Duration: p99 = 250ms

A spike in Errors or Duration is your first sign of trouble.

---

## USE method

**Definition:** A framework for resources: **U**tilization, **S**aturation, **E**rrors.

**Simple explanation:** Where RED is for services, USE is for the *resources* underneath (CPU, disk, memory, network). Utilization = how busy, Saturation = how much extra work is queued/waiting, Errors = hardware/resource errors.

**Example:** For a disk:
- Utilization: 80% busy
- Saturation: I/O queue depth of 15 (requests waiting)
- Errors: 0 read errors

High saturation with moderate utilization warns you a resource is about to become a bottleneck.

---

## Four Golden Signals

**Definition:** Google SRE's four key signals for user-facing systems: latency, traffic, errors, saturation.

**Simple explanation:** A superset framing that combines RED-like and USE-like ideas. If you can only monitor four things, monitor these.
- **Latency** — how long requests take (split success vs failure!).
- **Traffic** — how much demand (req/s).
- **Errors** — rate of failed requests.
- **Saturation** — how "full" the system is (the resource closest to its limit).

**Example:** A dashboard with exactly these four panels gives an at-a-glance health read for any service, and is the standard answer to "what would you monitor?"

---

## Percentiles (p50/p95/p99)

**Definition:** Values below which a given percentage of measurements fall — used instead of averages for latency.

**Simple explanation:** Averages hide pain. If 99 requests take 10ms and 1 takes 5s, the average looks fine (~60ms) but 1% of users had a terrible experience. p99 = "99% of requests were faster than this" captures the *tail* — the slow experiences that matter.

**Example:**
```
avg latency = 60ms   ← looks great, misleading
p50 = 10ms           ← typical request
p99 = 4,900ms        ← 1 in 100 users waited ~5s! 🚨
```
Always alert on p95/p99, not the mean.

---

## Prometheus model

**Definition:** A pull-based metrics system: it scrapes numeric metrics from HTTP endpoints your services expose, stores them as time-series with labels, and queries them via PromQL.

**Simple explanation:** Each service exposes a `/metrics` page. Prometheus periodically "pulls" (scrapes) those numbers and stores them. You query with PromQL and graph in Grafana. Pull-based means Prometheus controls timing and easily detects a target that's down (scrape fails).

**Example:**
```
# Service exposes at /metrics:
http_requests_total{method="GET",status="200"} 8734

# PromQL query for error rate over 5 min:
rate(http_requests_total{status=~"5.."}[5m])
```

---

## Cardinality explosion

**Definition:** The blow-up in stored time-series caused by labels with too many unique values.

**Simple explanation:** Every unique combination of label values is a separate stored series. A label like `user_id` (millions of values) multiplies your series count into the millions and can crash your metrics backend. Keep labels low-cardinality (status codes, service names) — never put IDs, emails, or URLs-with-params in metric labels.

**Example:**
```
# BAD: one series per user → millions of series
http_requests_total{user_id="42"}

# GOOD: bounded set of label values
http_requests_total{status="200", endpoint="/checkout"}
```
(High-cardinality data like user_id belongs in traces/logs, not metric labels.)

---

## Aggregation & rollups

**Definition:** Downsampling high-resolution metrics into coarser summaries over time, and reducing retention granularity as data ages.

**Simple explanation:** You don't need per-second data from 6 months ago. You keep fine-grained data recently, then roll it up (e.g., to 5-minute averages) for older data to save storage while keeping long-term trends.

**Example:** Retention tiers: raw 15s resolution for 7 days → 1-minute rollups for 30 days → 1-hour rollups for 1 year.

---

## Dashboards

**Definition:** Visual displays (e.g., Grafana) that plot metrics over time for at-a-glance system health.

**Simple explanation:** A good dashboard tells a story top-to-bottom: overall health (golden signals) at the top, then drill-down panels. It should let an on-call engineer answer "is it broken and roughly where?" in seconds — not overwhelm with 50 random graphs.

**Example:** A service dashboard: row 1 = latency/traffic/errors/saturation; row 2 = per-endpoint breakdowns; row 3 = dependencies (DB, cache) health.

---

## Push vs pull metrics

**Definition:** Whether services *push* metrics to a collector (StatsD, push gateway) or a collector *pulls* them (Prometheus scraping).

**Simple explanation:** Pull (Prometheus) lets the monitoring system control cadence and instantly know when a target is down. Push (StatsD) suits short-lived jobs that finish before they'd be scraped, and cases where the collector can't reach the target. Many stacks use both.

**Example:** A long-running web server → pull (Prometheus scrapes `/metrics`). A 5-second batch cron job → push (it sends metrics to a push gateway before exiting, since Prometheus would never catch it live).
