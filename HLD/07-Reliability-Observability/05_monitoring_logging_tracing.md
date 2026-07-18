# Monitoring, Logging & Tracing

> Observability’s **three pillars**: **metrics** (is it broken?), **logs** (what happened?), **traces** (where did time go across services?). You need all three — dashboards alone don’t debug distributed paths.

## Plain English

| Pillar | What it answers | Typical tools |
|--------|-----------------|---------------|
| **Metrics** | Rate, error, duration, saturation (RED/USE) | Prometheus, Datadog |
| **Logs** | Discrete events, errors, audit | ELK, Loki, CloudWatch |
| **Traces** | Request spans across services | Jaeger, Zipkin, OTel |

**RED:** Rate, Errors, Duration for request-driven services. **USE:** Utilization, Saturation, Errors for resources.

```text
  User request ──► Gateway ──► Order ──► Payment ──► DB
       │              │          │          │
       └────────── trace_id / span links ───┘
                      │
         metrics: qps, p99, error%
         logs:   payment declined code=...
         trace:  120ms in Payment, 5ms in DB
```

## Simple example

Checkout p99 spikes. Metrics show Payment error% ↑. Trace shows 2s wait on bank HTTP. Logs show timeouts. Without traces you’d SSH-guess which hop; without metrics you’d notice late; without logs you’d lack error reason.

```text
  Alert: SLO burn rate high on checkout_success
    → jump to service graph / traces
    → Payment span dominant
    → log: upstream bank 504
```

**SLI/SLO:** availability = successful requests / total; alert on **burn rate**, not raw CPU vanity graphs. Error budget ties releases to reliability.

## Why prefer one over the other

| Lean on **metrics** when… | Lean on **logs** when… | Lean on **traces** when… |
|---------------------------|------------------------|--------------------------|
| Alerting, capacity, SLO | Forensics, audit, rare bugs | Latency across microservices |
| Cheap, aggregated | Need payload / context | Tail latency attribution |
| Always-on | Sample high-volume logs | Sample traces if cost |

**Cardinality trap:** metric labels with `user_id` explode cost. High-cardinality identity → logs/traces with sampling, not infinite Prometheus series.

**Structured logs** (JSON) + `trace_id` / `request_id` beat grepping free text.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Full request logs | Perfect debug | Cost, PII risk |
| Aggressive sampling | Cheap | Miss rare paths |
| Many custom metrics | Detail | Cardinality / $$ |
| Trace every request | Max visibility | Ingest cost / overhead |

**Trap:** “We’ll check the logs” as the monitoring plan. Seniors: **RED metrics + SLO alerts + structured logs + distributed tracing** with a shared `trace_id`.

**Golden signals** (Google SRE): latency, traffic, errors, saturation — enough to start any design’s observability story before tool name-drops.

**PII:** scrub tokens/emails from logs; prefer hashes in trace attributes. Observability must not become a compliance incident.

## Interview trigger phrase

> “I’d instrument **RED metrics and SLOs**, structured logs with **trace_id**, and **OpenTelemetry traces** across checkout — alert on burn rate, debug with a single trace.”

## Exercise

**Observability for a 5-service ride-hailing trip start.**

1. Name 3 SLIs you’d put on a dashboard for the “request trip” path.
2. When do you sample traces at 1% vs 100%?
3. One sentence on correlating a user complaint (“trip didn’t start”) to a trace.
