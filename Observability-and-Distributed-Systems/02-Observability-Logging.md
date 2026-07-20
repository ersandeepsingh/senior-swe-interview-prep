# 02 · Observability — Logging

> Recording discrete events with enough context to debug after the fact.

---

## Structured logging

**Definition:** Emitting logs as machine-parseable key-value data (usually JSON) instead of free-form text.

**Simple explanation:** Instead of a sentence you have to eyeball, you emit fields a machine can filter and aggregate. This lets you search "all ERROR logs for user_id=42 in the payment service" instantly, instead of writing fragile regex over prose.

**Example:**
```jsonc
// Unstructured (hard to query):
"User 42 failed payment of $50 due to insufficient funds"

// Structured (easy to query/filter/aggregate):
{"level":"error","user_id":42,"amount":50,"event":"payment_failed","reason":"insufficient_funds"}
```

---

## Log levels

**Definition:** Severity categories (DEBUG, INFO, WARN, ERROR, FATAL) that classify how important a log line is.

**Simple explanation:** Levels let you turn the volume up or down. In production you might only keep INFO and above; when debugging you flip on DEBUG. Using them correctly keeps signal high — an ERROR should mean "a human may need to act," not "something mildly interesting happened."

**Example:**
- `DEBUG` — "cache key computed: user:42:profile" (dev detail)
- `INFO` — "order 991 placed successfully" (normal milestone)
- `WARN` — "payment retry 2 of 3" (recoverable, worth noting)
- `ERROR` — "payment failed after 3 retries" (needs attention)
- `FATAL` — "cannot connect to database, shutting down" (process dying)

---

## Correlation / request IDs

**Definition:** A unique ID attached to every log line produced while handling a single request, propagated across all services.

**Simple explanation:** In microservices, one request creates logs scattered across many services. A correlation ID is the string you search to stitch them back into one story. Without it, you're staring at a pile of unrelated lines.

**Example:** Gateway generates `request_id=abc-123` and passes it downstream via a header. Every service logs it:
```
service=gateway  request_id=abc-123 msg="received checkout"
service=payment  request_id=abc-123 msg="charging card"
service=payment  request_id=abc-123 msg="bank timeout"
```
Searching `abc-123` reconstructs the entire request's journey.

---

## Centralized logging

**Definition:** Shipping logs from all machines to one searchable system instead of leaving them on individual servers.

**Simple explanation:** With hundreds of containers that come and go, you can't SSH into each one. You forward all logs to a central store (ELK/EFK stack — Elasticsearch + Logstash/Fluentd + Kibana, or Grafana Loki) where you search everything in one place.

**Example:** Fluentd runs on each node, tails container logs, and ships them to Elasticsearch. Engineers open Kibana and query `level:ERROR AND service:payment` across the whole fleet from one search bar.

---

## Log sampling & volume control

**Definition:** Deliberately keeping only a fraction of logs (or dropping noisy ones) to control cost and storage.

**Simple explanation:** At scale, logging everything is prohibitively expensive. You sample — keep, say, 1% of successful requests but 100% of errors. You get statistical visibility into the normal path while never losing failures.

**Example:** A service handling 1B requests/day logs every 5xx error fully, but only 1-in-1000 successful 200s. Storage drops ~1000x while errors stay fully visible.

---

## PII & security in logs

**Definition:** Preventing sensitive data (passwords, tokens, credit cards, personal info) from being written to logs.

**Simple explanation:** Logs get copied, shipped, and retained widely — so a password in a log is a leaked password. You redact or mask sensitive fields at the source, and never log secrets or full card numbers. This is also a compliance requirement (GDPR, PCI-DSS).

**Example:**
```jsonc
// BAD:  {"card_number":"4111111111111111","cvv":"123"}
// GOOD: {"card_number":"************1111","cvv":"[REDACTED]"}
```

---

## Logs vs metrics cost

**Definition:** The principle that logs are far more expensive per unit of insight than metrics, so you shouldn't alert directly on raw logs at scale.

**Simple explanation:** A metric is one small number aggregated over millions of events; a log is a full record of each event. Counting errors via a metric is cheap; scanning terabytes of logs to count errors is slow and expensive. Use metrics for detection/alerting, logs for after-the-fact detail.

**Example:** To alert "error rate > 5%," don't grep logs every minute. Instead increment a counter metric `errors_total` and alert on its rate — then only dive into logs once the alert fires.
