# 04 · Observability — Distributed Tracing

> Following one request across many services to see where time goes and where it breaks.

---

## Spans & traces

**Definition:** A **span** is a single timed unit of work (one operation in one service); a **trace** is the tree of spans that together represent one end-to-end request.

**Simple explanation:** Think of a trace as a project and spans as tasks with start/end times, nested under one another. Each span records its duration, service, and attributes. Together they form a timeline showing exactly how a request spent its time.

**Example:**
```
Trace ID: 7f3a...  (total 820ms)
 Span: gateway.handle        [0ms → 820ms]
   Span: cart.get            [10ms → 50ms]
   Span: payment.charge      [55ms → 755ms]   ← 700ms here
     Span: bank.api.call     [70ms → 750ms]
   Span: inventory.reserve   [760ms → 815ms]
```

---

## Trace context propagation

**Definition:** Passing the trace ID and current span ID from one service to the next (usually via HTTP headers) so spans can be linked into one trace.

**Simple explanation:** Each service must forward "which trace am I part of, and who's my parent span?" to whatever it calls. Without propagation, you'd get disconnected spans that can't be assembled. The **W3C Trace Context** standard (`traceparent` header) makes this interoperable across languages/vendors.

**Example:**
```
GET /charge HTTP/1.1
traceparent: 00-7f3a9b...-a1b2c3-01
             │  │          │        └ flags (sampled)
             │  │          └ parent span id
             │  └ trace id
             └ version
```
The receiving service reads this header and creates a child span under the same trace.

---

## OpenTelemetry (OTel)

**Definition:** A vendor-neutral, open-source standard and SDK set for generating and exporting traces, metrics, and logs.

**Simple explanation:** Before OTel, every vendor had its own instrumentation library, so switching tools meant re-instrumenting everything. OpenTelemetry is the common standard: instrument once with OTel, then export to Jaeger, Datadog, Honeycomb, etc. by config. It's now the industry default.

**Example:** You add the OTel SDK to your app; it auto-instruments HTTP and DB calls. An OTel Collector receives the data and you point it at Jaeger today, Datadog tomorrow — no code changes.

---

## Sampling (head vs tail)

**Definition:** Keeping only a subset of traces to control cost. **Head sampling** decides at the start of a request; **tail sampling** decides after the request completes.

**Simple explanation:** Storing every trace at scale is too expensive. Head sampling is cheap but blind — it might drop the one slow/error trace you needed. Tail sampling waits until the request finishes so it can keep *all* errors and slow traces and drop boring fast ones — smarter but needs buffering.

**Example:**
- **Head:** "keep 1% of all requests, decided upfront." Simple, but a rare error may not be sampled.
- **Tail:** "keep 100% of traces with errors or latency > 1s, plus 1% of the rest." Keeps the interesting ones.

---

## Tools (Jaeger, Zipkin, Tempo, APMs)

**Definition:** Backends that store traces and provide UIs to search and visualize them.

**Simple explanation:** After you generate traces, something has to store and display them. Open-source options include Jaeger, Zipkin, and Grafana Tempo; commercial APMs include Datadog, New Relic, and Honeycomb. They give you the waterfall view, service maps, and latency breakdowns.

**Example:** In Jaeger you search `service=payment error=true`, click a trace, and see the waterfall pinpointing that the `bank.api.call` span consumed 90% of the latency.

---

## What tracing solves

**Definition:** The core problems tracing addresses — latency attribution and dependency mapping in distributed systems.

**Simple explanation:** In a monolith, a stack trace tells you where time went. In microservices, no single stack trace spans all services — tracing rebuilds that end-to-end picture. It answers "which of my 15 downstream services made this request slow?" and "what actually calls what?"

**Example:** p99 latency jumped. A trace reveals a newly added call to a slow recommendation service inserted into the checkout path — something no single service's logs would have made obvious. Service maps built from traces also reveal that `orders` unexpectedly depends on `legacy-billing`.
