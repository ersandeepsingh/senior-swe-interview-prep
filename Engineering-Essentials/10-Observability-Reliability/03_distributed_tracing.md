# Distributed Tracing

> Follow **one request** across many services as a tree of timed spans — answers *"where did the time go?"*

## Plain English

Tracing shows the critical path of one request through many services. **OpenTelemetry** is the vendor-neutral instrumentation; **Jaeger**, Tempo, Zipkin, X-Ray are backends that store and show traces.

```text
  Trace checkout-abc (820ms)
  ├─ api-gateway           5ms
  ├─ cart-service         40ms
  ├─ payment-service     700ms  ← hotspot
  │   └─ bank HTTP       680ms
  └─ inventory            75ms
```

Sampling: you usually don't keep 100% of traces in prod (cost). Head-based (decide at start) vs tail-based (keep slow/error traces) — seniors mention the trade-off.

## Essentials (must-know for this topic)

### Trace vs span

| Term | Meaning |
|------|---------|
| **Trace** | One end-to-end request (the whole tree) |
| **Span** | One unit of work inside it (HTTP call, DB query, queue publish) with start/end + attributes |
| **Parent/child** | Spans nest: checkout → payment → bank API |
| **Span attributes** | Useful metadata (`http.status`, `db.statement` truncated) — not huge payloads |

### Context propagation

| Idea | Detail |
|------|--------|
| **Trace context** | IDs that must ride on every hop |
| **W3C `traceparent`** | Standard header: `00-<trace-id>-<span-id>-01` |
| **Broken propagation** | Each service starts a **new** trace → tree falls apart |
| **Async / queues** | Put context in **message headers**; consumers continue the same trace |

### Sampling (one-liners)

| Style | Idea |
|-------|------|
| **Head-based** | Decide at the start (e.g. keep 1%) — cheap, may miss rare failures |
| **Tail-based** | Keep slow/error traces after the fact — better signal, more collector complexity |

## Simple example

Without tracing: “checkout is slow” → SSH into five services, guess.

With tracing: open the slow trace → payment→bank is 680ms of 820ms → dig bank timeouts in payment logs for that `trace_id`.

Propagate context:

```text
  Incoming:  traceparent: 00-<trace-id>-<span-id>-01
  Outgoing:  same header on every downstream HTTP/gRPC/message
```

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Always-on tracing | Full visibility | Storage cost, slight overhead |
| Head sampling 1% | Cheap | May miss rare failures |
| Tail-based sampling | Keep errors/slow | More complex collector |
| Auto-instrumentation | Fast coverage | Noisy / missing business attributes |

## Pitfalls

- **Broken context propagation** — each service starts a new trace; the tree falls apart (especially async/queue workers).
- **Missing spans on message consumers** — extract and continue context from message headers.
- **Treating traces as logs** — don't dump huge payloads into span attributes.
- **No link from metrics → traces** — exemplars or “view traces for this spike” closes the loop.

## Interview trigger phrase

> “I'd use **OpenTelemetry** spans with W3C context propagation so one checkout shows the **critical path**; I'd sample carefully and always preserve context across queues.”

## Exercise

Order service publishes to Kafka; inventory consumes later. Why might the inventory work show as a **separate** trace, and what one change fixes it?
