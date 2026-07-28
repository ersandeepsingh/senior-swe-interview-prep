# Long Polling / Short Polling

> Approximate realtime by repeatedly asking the server — either often (**short poll**) or holding the request until something changes (**long poll**).

## Plain English

Both approximate push using plain HTTP. They’re the fallback when WebSockets/SSE aren’t available (old clients, strict corp proxies) — and a valid first step before investing in stateful streams.

## Essentials (must-know for this topic)

### Short vs long polling

| | **Short polling** | **Long polling** |
|--|-------------------|------------------|
| Behavior | Client asks every N seconds | Server **holds** request until event or timeout |
| Empty traffic | Many “nothing changed” responses | Fewer empties; response when ready |
| Lag | Up to N seconds | Near event time (plus reconnect gap) |
| Server cost | High QPS at scale | Ties up workers/connections while waiting |
| Complexity | Trivial | Need timeouts, notify path, client loop |

### Vs true push

| | Polling | SSE / WebSockets |
|--|---------|------------------|
| Model | Pull | Push |
| Infra | Stateless HTTP-friendly | Long-lived connections |
| At high fan-out | Request storm | Conn/memory + pub-sub |

### Design knobs interviewers expect

| Knob | Guidance |
|------|----------|
| Interval / timeout | Short poll: 5–30s typical; long poll: 15–60s hold |
| Backoff | On errors, exponential backoff — don’t DDOS yourself |
| `since` / cursor | Only return changes after last seen timestamp/id |
| Duplicates | At-least-once on retry → idempotent client handling |

**Rough load math:** `clients × (60 / interval_sec)` requests per minute for short poll.

## Why seniors get asked

System design “notification” questions often expect you to start simple (polling), then upgrade — and to quantify connection/load cost.

## Simple example

Short poll:

```bash
# every 5s
curl -s "https://api.example.com/orders/42" | jq .status
```

Long poll:

```http
GET /api/v1/orders/42/wait?since=2026-07-25T10:00:00Z&timeout=30
```

```json
// 200 when status changes, or 204/200 empty after timeout
{"status": "shipped", "updated_at": "2026-07-25T10:00:12Z"}
```

Pseudocode (server):

```python
def long_poll(order_id, since, timeout=30):
    deadline = now() + timeout
    while now() < deadline:
        order = db.get(order_id)
        if order.updated_at > since:
            return order
        sleep(0.5)  # or wait on pub/sub notify
    return None  # client retries
```

## When to use / when not / trade-offs

| Use polling when… | Prefer push (SSE/WS) when… |
|-------------------|----------------------------|
| Updates are rare or lag is OK | Sub-second UX, many clients |
| Infra can’t keep long-lived streams | Scale of open connections is planned |
| You need maximum HTTP compatibility | Battery/network cost of phones matters |

**Trade-offs:** short poll = simple + wasteful; long poll = fewer empty responses but ties up workers/connections; both scale worse than a proper push channel at high fan-out.

## Common pitfalls

- Short-polling too aggressively (DDOS yourself)
- Long-poll without timeouts → stuck workers
- No backoff on errors
- Forgetting “at-least-once” duplicates when client retries

## Interview trigger phrase

> “I’d start with short or long polling for simplicity, then move to SSE/WebSockets when latency and load justify the stateful push path.”

## Exercise

100k clients poll every 2s. Roughly how many requests/minute is that? Propose long polling or SSE and explain which cost you reduce.
