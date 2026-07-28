# Webhooks

> Your system **POSTs an HTTP callback** to a customer’s URL when an event happens — “don’t call us, we’ll call you.”

## Plain English

Stripe charges a card → Stripe POSTs `invoice.paid` to `https://yourapp.com/webhooks/stripe`. You verify the signature, process the event, return `2xx` quickly. If you fail or time out, the provider **retries** with backoff. Webhooks invert polling: the producer pushes events to consumers you don’t control.

## Essentials (must-know for this topic)

### Delivery model

| Trait | Typical webhook reality |
|-------|------------------------|
| Direction | Provider → your HTTPS endpoint |
| Semantics | **At-least-once** (retries on timeout/5xx) |
| Ordering | **Not guaranteed** across events |
| Your job | Verify, ack fast, process async, **dedupe** |

### Must-have handler checklist

| Step | Why |
|------|-----|
| **Signature verify** (HMAC / public key) | Reject spoofed POSTs |
| **Idempotency** on `event.id` | Retries won’t double-apply |
| **Return 2xx quickly** | Heavy work → queue; else provider times out and retries |
| **Timeout awareness** | Providers often wait ~5–30s |
| **Replay / retention** | Many vendors offer event dashboards for missed deliveries |

### Webhooks vs polling vs queues

| | Webhooks | Consumer polling | Internal queue |
|--|----------|------------------|----------------|
| Who initiates | Producer | Consumer | Producer → broker |
| Public URL needed | Yes (receiver) | No | No |
| Best for | SaaS integrations | Firewalled receivers | Your own services |

**Secure inbound:** HTTPS only, rotate secrets, optional mTLS for high-trust partners.

## Why seniors get asked

Integrations, payments, CI, and SaaS platforms all use webhooks. Seniors must cover retries, idempotency, and signature verification — not just “POST JSON somewhere.”

## Simple example

```http
POST /webhooks/payments HTTP/1.1
Content-Type: application/json
X-Signature: t=1721...,v1=5f3c...

{"id":"evt_123","type":"payment.succeeded","data":{"order_id":"42"}}
```

```python
def handle_webhook(headers, body: bytes):
    if not verify_hmac(headers["X-Signature"], body, secret):
        return 401
    event = json.loads(body)
    if already_processed(event["id"]):  # idempotency
        return 200
    enqueue(event)           # work async
    return 200               # ack fast
```

## When to use / when not / trade-offs

| Use webhooks when… | Prefer pull/polling when… |
|--------------------|---------------------------|
| You notify external systems of events | Receiver can’t expose a public URL |
| Near-realtime integration without them polling you | Strict firewall; outbound-only consumers |
| Provider already supports signed callbacks | You need guaranteed ordered delivery (use a queue) |

**Trade-offs:** low latency fan-out to partners; you depend on their uptime/URL correctness; at-least-once delivery → must be idempotent.

## Common pitfalls

- Doing heavy work before returning 200 (timeouts → duplicate retries)
- No signature check (spoofed events)
- Not deduping by event id
- HTTP endpoints that aren’t reachable (localhost, firewall)

## Interview trigger phrase

> “Webhooks are at-least-once: verify signatures, ack quickly, process async, and dedupe on event id.”

## Exercise

Design receiving a `user.created` webhook from an identity provider. List: verification step, success response timing, retry behavior you assume, and how you avoid creating the user twice.
