# 01 · Observability — The Three Pillars

> How you understand what a running system is doing from the outside.

---

## Logs

**Definition:** Immutable, timestamped records of discrete events that happened in a system.

**Simple explanation:** A log is a diary entry — "at 10:03:22, user 42 tried to log in and failed." Each line describes one thing that occurred. They're great for answering *"why did this specific thing happen?"* because they carry rich detail, but they're expensive to store and slow to aggregate at scale.

**Example:**
```
2026-07-20T10:03:22Z level=ERROR service=auth user_id=42 msg="login failed" reason="bad_password" request_id=abc-123
```
When a customer says "I couldn't log in at 10am," you grep logs for their `user_id` and see exactly what failed.

---

## Metrics

**Definition:** Numeric measurements captured over time as a time-series (a number + timestamp + labels).

**Simple explanation:** A metric is a gauge on a dashboard — "requests per second," "error rate," "CPU %." Because they're just numbers, they're cheap to store, easy to graph, and perfect for alerting and spotting trends. They tell you *"is something wrong?"* but not the detailed *why*.

**Example:**
```
http_requests_total{service="auth", status="500"} = 1423
```
A graph of this over time shows a sudden spike at 10am — telling you errors jumped, but not which user or why.

---

## Traces

**Definition:** A record of a single request's journey as it flows through multiple services, broken into timed spans with parent-child relationships.

**Simple explanation:** A trace is a "track my package" view for one request. It shows every service the request touched and how long each step took, so you can see *where* time was spent or where it failed. Essential in microservices where one user click fans out to 20 backend calls.

**Example:** A checkout request produces a trace:
```
Trace: checkout (820ms)
 ├─ api-gateway         (5ms)
 ├─ cart-service        (40ms)
 ├─ payment-service     (700ms)  ← the slow one
 │   └─ bank-api call   (680ms)
 └─ inventory-service   (75ms)
```
Instantly you see the payment→bank call is the bottleneck.

---

## The Three Pillars vs "Observability"

**Definition:** Observability is the *property* of being able to understand a system's internal state from its outputs — logs, metrics, and traces are the *data* that enable it, not observability itself.

**Simple explanation:** Having the three signals doesn't automatically make you observable. Monitoring answers *known* questions ("is CPU high?"); observability lets you answer *unknown* questions you didn't predict ("why are only Android users in Germany seeing slow checkouts?"). True observability needs high-cardinality, correlated data you can slice arbitrarily.

**Example:** You get paged for high latency. Metrics show *that* it's slow. You didn't have a pre-built dashboard for "slow only for one payment provider," but because your traces carry a `payment_provider` attribute, you can group by it on the fly and discover provider X is the culprit — that's observability.

---

## When to use which signal

**Definition:** A workflow for choosing the right pillar for the question you're asking.

**Simple explanation:**
- **Metric** → *"Is it broken? Is it getting worse?"* (detection & alerting)
- **Trace** → *"Where in the request path is the problem?"* (localization)
- **Log** → *"Why exactly did it fail?"* (root cause detail)

**Example:** The debugging flow for a latency spike:
1. **Metric** alert fires: p99 latency > 1s.
2. **Trace** for a slow request shows `payment-service` is taking 700ms.
3. **Logs** for that service at that time show `msg="bank API timeout, retrying 3x"`.

You moved from *what* → *where* → *why* using all three in order.
