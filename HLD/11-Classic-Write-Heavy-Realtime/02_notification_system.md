# Design a Notification System 🟡

> **Crux:** Async fan-out to many channels (push, email, SMS, in-app) with preferences, dedup, and clear delivery guarantees — without blocking the producer.

## Clarify (say this first)

**Functional**
- Trigger notifications from events (like, comment, payment, security)
- Channels: in-app, mobile push, email, SMS; user preferences + quiet hours
- Templates + localization; deep links
- Batching / digests for low-priority (optional)

**Non-functional**
- Producer API fast — enqueue and return
- At-least-once to workers; idempotent sends to providers
- High fan-out (one event → many users); priority lanes
- Respect unsubscribes / legal constraints (SMS)

## Back-of-envelope

```text
Assumptions: 50M notifiable events/day → ~600/s avg (peak 5–10K)
Fan-out: avg 3 recipients × 1.5 channels → ~3K provider calls/s peak higher
In-app inbox storage: 100 B × billions/year — TTL + archive
Provider SLAs: push fast; email/SMS slower + rate-limited by vendor
```

## API + data model

```text
POST /api/v1/notifications        { event_type, recipients[], payload, priority }
GET  /api/v1/users/:id/inbox
POST /api/v1/users/:id/preferences
POST /api/v1/notifications/:id/ack  (read/dismiss)
```

| Entity | Fields |
|--------|--------|
| `notification` | `id`, `user_id`, `type`, `payload`, `status`, `created_at` |
| `preference` | `user_id`, `type`, `channel`, `enabled`, `quiet_hours` |
| `delivery_attempt` | `notif_id`, `channel`, `provider_id`, `status`, `attempts` |
| Outbox / queue | event → fan-out tasks |

## High-level architecture

```text
Services → Notification API → Kafka/SQS (by priority)
                                  │
                            Fan-out workers
                                  │
              ┌───────────┬───────┴───────┬──────────┐
              ▼           ▼               ▼          ▼
           In-app DB   Push (FCM)      Email       SMS
              │           │               │          │
              └──────── dedup / prefs / rate limits ─┘
```

## Deep dive: the crux

**Async fan-out:** producer writes an event (or transactional outbox) → queue → workers expand recipients → per-channel tasks. Never call FCM/SES inline in the user request path.

**Delivery guarantees**
- Queue: at-least-once
- Idempotency key = `notif_id + channel` (or hash of event+user+channel)
- Providers: retries with exponential backoff + DLQ; SMS/email careful with duplicates

| Priority | Handling |
|----------|----------|
| Security / OTP | Dedicated high-priority topic; minimal batching |
| Social | Batch, coalesce “5 people liked,” digest |
| Marketing | Strict prefs + frequency caps |

**Preferences:** check before send; cache prefs in Redis. Quiet hours delay to local morning via delayed queue.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Fully async | Producer latency / isolation | End-to-end delay |
| At-least-once | Reliability | Rare duplicate notifications |
| Per-channel queues | Independent scaling | More moving parts |
| Digests | Less spam | Less immediacy |

## Failure modes & scale

- **Provider outage:** circuit breaker; retry later; in-app still written
- **Poison template / bad payload:** DLQ + alert; don’t block partition
- **Thundering fan-out** (celebrity like): expand async; rate-limit per user inbox
- **Preference race:** version prefs; safe default = don’t send marketing
- **Shard** inbox by `user_id`; topics by priority/channel

## Interview trigger phrase

> “I’d make notification a fan-out pipeline: enqueue the event, apply preferences in workers, send per-channel with idempotency keys and DLQs — at-least-once with dedup, never blocking the source service on FCM or SMTP.”

## Exercise

1. How do you **coalesce** 500 like events into one push without losing the last liker?
2. Design **exactly-once appearance** in the in-app inbox under at-least-once workers.
3. What changes for **transactional email** (receipts) vs **marketing push**?
