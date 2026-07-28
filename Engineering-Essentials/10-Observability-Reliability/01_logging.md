# Logging

> Structured, searchable records of discrete events — the diary that answers *"why did this specific request fail?"*

## Plain English

A log line is one fact at one moment: who did what, with what IDs, and what happened. At scale you don't `tail` servers — you ship structured JSON (or key=value) to a central store (ELK, Loki, CloudWatch) and query by `request_id`, `user_id`, `error_code`.

```text
  Client → Gateway (sets request_id=abc)
         → Cart (logs request_id=abc)
         → Payment (logs request_id=abc)
  Grep request_id=abc → full story of one checkout
```

## Essentials (must-know for this topic)

### Log levels

| Level | Use for |
|-------|---------|
| **ERROR** | Something failed; needs attention |
| **WARN** | Unexpected but recovered / degraded |
| **INFO** | Business milestones (order placed, payment captured) |
| **DEBUG** | High-volume detail (only in non-prod or sampled) |

Levels are a **filter**, not decoration. Alert on metrics/SLIs — not every ERROR line.

### Structured vs unstructured

| | Unstructured | Structured |
|---|--------------|------------|
| Shape | Free-text sentence | JSON / key=value fields |
| Query | Grep / fragile regex | Filter by field (`error_code=card_declined`) |
| Cost | Cheap to write | Slightly more CPU/bytes |
| Interview take | Fine for local printf | **Required at scale** |

### Correlation / request ID

| Term | Meaning |
|------|---------|
| **Correlation ID / request ID** | One ID for one user action across services |
| **Where set** | Edge/gateway generates; every downstream hops it |
| **How passed** | Header (`X-Request-Id`) or W3C `traceparent` |
| **Where logged** | On **every** log line for that request |

Without it, microservices become a scavenger hunt.

## Simple example

Bad (unstructured, unsearchable):

```text
Error: something went wrong with payment
```

Good:

```json
{
  "ts": "2026-07-25T14:02:11Z",
  "level": "ERROR",
  "service": "payment",
  "msg": "charge_failed",
  "request_id": "abc-123",
  "user_id": "u42",
  "order_id": "o99",
  "provider": "stripe",
  "error_code": "card_declined"
}
```

Now you can filter: all `card_declined` for provider `stripe` in the last hour.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Structured JSON | Fast filters, dashboards from logs | Slightly more CPU/bytes |
| Log everything at DEBUG | Deep forensics | Cost, PII risk, noise |
| Sample high-volume paths | Cost control | Blind spots on rare bugs |
| Centralize (ELK/Loki) | One place to search | Ops cost, retention choices |

## Pitfalls

- **PII in logs** — emails, tokens, card numbers. Redact at the source.
- **String concatenation as the only format** — can't filter reliably.
- **No correlation ID** — microservices become a scavenger hunt.
- **Logging inside hot loops** — can outpace your disk/network and tank latency.
- **Using logs as metrics** — counting ERROR lines is fragile; prefer real metrics for alerts.

## Interview trigger phrase

> “I'd emit **structured logs** with a **correlation ID** propagated across services, ship them centrally, and keep PII out — logs answer *why*, not *is it broken*.”

## Exercise

A user says checkout failed at 3:17pm. List the **three fields** you'd require on every payment log line, and one thing you would **never** log.
