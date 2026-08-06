# 15 · Observability — Prometheus, Grafana, Loki & Fluent Bit

> The open-source “LGTM-ish” stack most seniors name in interviews: **Prometheus** (metrics), **Grafana** (UI/alerts), **Loki** (logs), **Fluent Bit** (log shipper). Together they answer: *is it broken → where → why?*

---

## Big picture (how the pieces fit)

```text
  Your services / pods / nodes
       │
       ├─ /metrics endpoint ──────────────► Prometheus (scrapes / pulls)
       │                                         │
       ├─ stdout / log files ──► Fluent Bit ──► Loki (stores log labels + chunks)
       │                                         │
       └─ traces (optional) ──► Tempo/Jaeger     │
                                                 ▼
                                            Grafana
                                      dashboards + Explore
                                      + alert rules / contact points
```

| Tool | Pillar | Job in one line |
|------|--------|-----------------|
| **Prometheus** | Metrics | Scrape, store, query time-series; fire alert rules |
| **Grafana** | UI | Dashboards, Explore (PromQL/LogQL), unified alerting |
| **Loki** | Logs | Cheap log store indexed by **labels** (not full-text like ES by default) |
| **Fluent Bit** | Agent | Collect/parse/filter logs (and sometimes metrics) and forward |

**Interview one-liner:**  
> “Prometheus scrapes metrics, Fluent Bit ships logs to Loki, Grafana is the pane of glass — I correlate a red metric panel with LogQL for the same `service`/`pod` labels.”

---

# 1. Prometheus

## Definition

Prometheus is a **pull-based** monitoring system. It periodically **scrapes** HTTP `/metrics` endpoints, stores samples as **time series** keyed by metric name + **labels**, and lets you query with **PromQL**. Alertmanager (often paired) routes alert notifications.

## Simple explanation

Instead of every app pushing stats into a central DB, Prometheus asks: “Hey service, how are you?” every 15–30s. Apps expose a text page of counters/gauges/histograms. You alert on expressions like “error rate > 1% for 5 minutes,” not on individual log lines.

```text
  Prometheus
     │ scrape :8080/metrics every 15s
     ▼
  checkout-service
     # HELP http_requests_total Total HTTP requests
     # TYPE http_requests_total counter
     http_requests_total{method="GET",code="200"} 12890
     http_requests_total{method="GET",code="500"} 42
```

## Metric types (quick)

| Type | Behavior | Example |
|------|----------|---------|
| **Counter** | Only increases | `http_requests_total` |
| **Gauge** | Up/down | `go_goroutines`, queue depth |
| **Histogram** | Buckets observations | `http_request_duration_seconds_bucket` |
| **Summary** | Client-side quantiles | Less common than histograms now |

## PromQL examples (easy)

```promql
# Requests per second by status
sum(rate(http_requests_total[5m])) by (code)

# Error ratio
sum(rate(http_requests_total{code=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))

# p99 latency from histogram
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)
)
```

## Labels & cardinality (the footgun)

**Good labels:** `service`, `method`, `status`, `region` (low/medium cardinality).  
**Bad labels:** `user_id`, `email`, `request_id` (explode series count → OOM / slow queries).

```text
  http_requests_total{service="pay",code="500"}     ✓
  http_requests_total{user_id="u_991823"}           ✗  (millions of series)
```

Put high-cardinality IDs in **logs/traces**, not metric labels.

## Pull vs push

| Mode | When |
|------|------|
| **Pull (default)** | Services with stable scrape targets (K8s service discovery) |
| **Pushgateway** | Short-lived batch jobs that die before scrape |
| **Remote write** | Long-term store (Thanos/Mimir/Cortex/Grafana Cloud) |

## Exporters (common name-drops)

- **node_exporter** — CPU, disk, memory on VMs  
- **kube-state-metrics** — Deployments, pods desired vs ready  
- **postgres_exporter / redis_exporter** — datastore internals  
- **blackbox_exporter** — probe URL/TCP/ICMP (synthetics)

## Example — RED metrics for checkout

```text
  Rate:     sum(rate(http_requests_total{service="checkout"}[5m]))
  Errors:   sum(rate(http_requests_total{service="checkout",code=~"5.."}[5m]))
  Duration: histogram_quantile(0.99, ...)
```

Alert: `error_ratio > 0.01 for 5m` → page on-call.

## Trade-offs

| Gain | Cost |
|------|------|
| Simple ops model, powerful PromQL | Single Prometheus doesn’t scale forever (need sharding/Thanos/Mimir) |
| Great for alerting on symptoms | Not a log store; bad for high-cardinality events |
| Pull + SD fits Kubernetes | Ephemeral jobs need Pushgateway |

---

# 2. Grafana

## Definition

Grafana is a **visualization and alerting frontend**. It connects to many data sources (Prometheus, Loki, Tempo, Elasticsearch, CloudWatch, …) and builds **dashboards**, **Explore** queries, and **unified alert rules**.

## Simple explanation

Prometheus/Loki store data; Grafana is the TV screen + alarm panel. You don’t “run Grafana instead of Prometheus” — you point Grafana *at* Prometheus.

```text
  Grafana dashboard "Checkout SLO"
    Row 1: Stat panels — RPS, error %, p99
    Row 2: Time series — latency heatmap
    Row 3: Logs panel — Loki query filtered by $service
    Variables: service, env, region  ← dropdowns at top
```

## What a good dashboard shows

1. **Golden signals / RED** at the top (user pain)  
2. **Saturation** next (CPU, queue depth, pool wait)  
3. **Dependencies** (DB, Redis, payment latency)  
4. Links to **logs/traces** for the same labels  
5. Sparse graphs — not 40 random panels

## Alerting (modern Grafana)

```text
  Alert rule (Grafana or Prometheus)
       │ evaluates PromQL / LogQL
       ▼
  Alertmanager or Grafana Contact points
       │
       ├── PagerDuty (page)
       ├── Slack (ticket / warn)
       └── email
```

**Philosophy:** Alert on **symptoms** (high error rate, SLO burn) more than causes (CPU high alone).

## Example — debug path in Grafana Explore

1. Prometheus: error rate spiked at 14:02 for `service=checkout`.  
2. Switch Explore → Loki: `{service="checkout"} |= "ERROR"` around 14:02.  
3. See `payment_timeout` messages + `trace_id`.  
4. Jump to Tempo/Jaeger with that trace_id → payment span is 3s.

## Trade-offs

| Gain | Cost |
|------|------|
| One UI for metrics + logs + traces | Dashboards rot if nobody owns them |
| Easy sharing / folders / permissions | Alert spam if every panel becomes a page |
| Huge plugin ecosystem | Still need solid data sources underneath |

---

# 3. Loki

## Definition

Loki is a **log aggregation system** inspired by Prometheus. It indexes **labels** (metadata), not the full log text by default, and stores compressed log chunks in object storage. Query language: **LogQL**.

## Simple explanation

Elasticsearch indexes every word → expensive and powerful full-text search.  
Loki indexes labels like `namespace`, `app`, `pod` → **cheap**, then searches content inside matching streams.

```text
  Think: "Prometheus for logs"
  Metric:  http_requests_total{app="checkout"}
  Logs:    {app="checkout"} |= "payment_failed"
```

## How logs get in

```text
  App logs to stdout (JSON)
       │
  Fluent Bit / Promtail / Alloy DaemonSet
       │ adds labels: app, namespace, pod, level
       ▼
  Loki distributor → ingester → object storage (S3/GCS)
       │
  Grafana LogQL queries
```

## LogQL examples (easy)

```logql
# All logs from checkout in prod
{app="checkout", env="prod"}

# Only lines containing timeout
{app="checkout"} |= "timeout"

# JSON field filter (structured logs)
{app="checkout"} | json | status >= 500

# Count errors per minute (logs → metric-ish)
sum(rate({app="checkout"} |= "ERROR" [1m])) by (pod)
```

## Labels for Loki (same cardinality lesson)

| Good | Bad |
|------|-----|
| `app`, `namespace`, `level`, `env` | `user_id`, `order_id`, full `path` with IDs |
| Low-cardinality `status_class=5xx` | Unique request IDs as labels |

High-cardinality labels create too many **streams** → Loki slows down / costs spike. Keep IDs **inside** the log line; filter with `|=` or `| json`.

## Loki vs ELK/EFK

| | Loki | Elasticsearch (ELK) |
|--|------|---------------------|
| Index model | Labels (+ optional more) | Full-text inverted index |
| Cost at volume | Usually cheaper | Usually higher |
| Ad-hoc text search | Good enough for many cases | Stronger / richer |
| Ops mental model | Prometheus-like | Search-cluster-like |
| Best with | Grafana + K8s stdout | Heavy search/analytics on logs |

## Example — find why checkout failed

```logql
{app="checkout", env="prod"}
  | json
  | level="error"
  | line_format "{{.ts}} {{.msg}} order={{.order_id}} trace={{.trace_id}}"
```

Correlate `trace_id` with Tempo → see payment dependency timeout.

## Trade-offs

| Gain | Cost |
|------|------|
| Cost-efficient log storage | Not a drop-in ES replacement for complex search |
| Label model aligns with Prom/Grafana | Mis-labeled streams hurt badly |
| Multi-tenant designs exist | Need retention + compaction discipline |

---

# 4. Fluent Bit

## Definition

Fluent Bit is a lightweight **telemetry agent** (CNCF). It **collects** logs (and can do metrics/traces), **parses/filters** them, and **forwards** to backends like Loki, Elasticsearch, S3, Kafka, CloudWatch.

## Simple explanation

Apps shouldn’t know about Loki URLs and retries. They write to **stdout**. Fluent Bit runs as a DaemonSet on each node, tails container logs, adds K8s metadata labels, and ships reliably.

```text
  INPUT → FILTER → OUTPUT

  tail container logs → parse JSON → nest k8s labels → output loki
```

## Why Fluent Bit (vs Fluentd / Logstash / Promtail)

| Tool | Character |
|------|-----------|
| **Fluent Bit** | Tiny memory footprint; great as node agent |
| **Fluentd** | Heavier, huge plugin ecosystem |
| **Logstash** | JVM; powerful pipelines; more resource-heavy |
| **Promtail** | Purpose-built Loki shipper (Grafana ecosystem) |
| **Grafana Alloy** | Newer all-in-one collector (metrics+logs+traces) |

**Interview tip:** “DaemonSet Fluent Bit → Loki” is a standard K8s log path; Promtail is the Loki-native alternative.

## Example pipeline (conceptual config)

```ruby
[SERVICE]
    Flush         5
    Daemon        Off
    Log_Level     info

[INPUT]
    Name              tail
    Tag               kube.*
    Path              /var/log/containers/*.log
    Parser            docker
    Mem_Buf_Limit     50MB
    Skip_Long_Lines   On

[FILTER]
    Name              kubernetes
    Match             kube.*
    Merge_Log         On
    Keep_Log          Off
    K8S-Logging.Parser On

[FILTER]
    Name              parser
    Match             kube.*
    Key_Name          log
    Parser            json
    Reserve_Data      On

[OUTPUT]
    Name              loki
    Match             kube.*
    Host              loki.monitoring.svc
    Port              3100
    Labels            job=fluentbit, app=$kubernetes['labels']['app']
```

## Useful filters (what to say you do)

1. **Parse JSON** so `level`, `msg` are fields  
2. **Drop DEBUG** in prod to cut cost  
3. **Redact** `password`, `authorization`, card fields  
4. **Add** `env`, `cluster` labels  
5. **Buffer + retry** so Loki blips don’t lose everything  

## Example — drop noisy logs

```text
  Before: 40% of volume is health-check INFO
  Filter: drop if path="/healthz" OR msg matches "health ok"
  Result: lower Loki bill, clearer signal
```

## Trade-offs

| Gain | Cost |
|------|------|
| Low resource usage on every node | Complex nesting of filters can get messy |
| Decouples apps from log backend | Misconfig → silent drops or label explosions |
| Multi-output (Loki + S3 archive) | Need care with backpressure / buffer limits |

---

# 5. End-to-end example (easy story for interviews)

**System:** `checkout` and `payment` microservices on Kubernetes.

### Setup

```text
  1. Each service exposes /metrics (Prometheus client library)
  2. Logs JSON to stdout: {"level":"info","msg":"...","order_id":"...","trace_id":"..."}
  3. Fluent Bit DaemonSet → Loki (labels: app, namespace, level)
  4. Prometheus scrapes via PodMonitor / annotations
  5. Grafana datasources: Prometheus + Loki (+ Tempo)
```

### Incident

User reports “payments failing.”

```text
  Step 1 — Grafana / Prometheus
    error rate payment service ↑ at 18:40
    p99 latency ↑ to 2.5s

  Step 2 — Grafana Explore / Loki
    {app="payment"} |= "ERROR" | json
    → "connection reset by stripe-proxy"

  Step 3 — Trace (if enabled)
    trace_id=abc → checkout 50ms, payment 2400ms on HTTP client span

  Step 4 — Fix / mitigate
    circuit breaker + retry with jitter; scale proxy; page based on SLO burn
```

### Minimal alerts

| Alert | Expression idea | Severity |
|-------|-----------------|----------|
| High 5xx | error ratio > 1% for 5m | Page |
| Laggy p99 | p99 > 1s for 10m | Ticket |
| Log burst | rate of ERROR logs > threshold | Ticket |
| Fluent Bit failing | agent up / output errors | Ticket |

---

# 6. How to choose / combine

| Need | Use |
|------|-----|
| “Is checkout broken right now?” | **Prometheus** + Grafana alert |
| “Why did this order fail?” | **Loki** LogQL (+ trace_id) |
| “Ship container logs cheaply” | **Fluent Bit** or Promtail → Loki |
| “Pretty graphs for standup” | **Grafana** dashboards |
| “Full-text log analytics / SIEM” | Often **Elastic** (or Loki + careful design) |
| “Long-term metrics retention” | Thanos / Mimir / Cortex + Grafana |

---

# 7. Interview trigger phrases

> “I’d scrape RED metrics with **Prometheus**, ship stdout logs through **Fluent Bit** to **Loki** using low-cardinality labels, and use **Grafana** to jump from a red panel to LogQL for the same `app` label.”

> “Cardinality belongs in logs and traces — never as Prometheus/Loki labels for user IDs.”

> “Loki is cheaper because it indexes labels, not every word like Elasticsearch.”

---

# 8. Exercise

1. Draw the path of one log line from a Go service to a Grafana panel.  
2. Why is `user_id` a bad Prometheus label *and* a bad Loki stream label? Where should it live?  
3. Write a PromQL error-rate query and a LogQL query that you’d open together during an incident.  
4. Fluent Bit vs Promtail — when would you pick each?
