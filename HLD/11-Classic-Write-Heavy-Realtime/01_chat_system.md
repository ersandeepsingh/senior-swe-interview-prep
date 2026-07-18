# Design a Chat System (WhatsApp / Slack) 🔴

> **Crux:** Millions of sticky realtime connections, fan-out of messages to online recipients, and **ordering / delivery semantics** (at-least-once + idempotency, read receipts).

## Clarify (say this first)

**Functional**
- 1:1 and group messaging; delivery + read receipts; presence (online/typing) optional
- Media via object store + URL; history sync on reconnect
- Slack-style channels vs WhatsApp groups — pick one primary
- Push notifications when offline

**Non-functional**
- Low latency online path (p99 tens–low hundreds ms)
- Ordering per conversation (causal / total order in a channel)
- At-least-once delivery + client dedup; no silent loss
- Connection scale: millions of concurrent WebSockets/long-polls

## Back-of-envelope

```text
Assumptions: 100M DAU, 50 msgs/user/day → ~60K msgs/s avg (peak ~300K)
Group avg size 10 → fan-out amp on groups; large channels worse
Concurrent connections: 20–30% online → tens of millions WS
Storage: msg ~200 B × 6B/day ≈ 1.2 TB/day text (media separate)
History: retain recent in hot store; cold in object/DB
```

## API + data model

```text
WS   /chat                     connect, send, ack, presence
POST /api/v1/channels/:id/messages
GET  /api/v1/channels/:id/messages?cursor
POST /api/v1/channels          create DM/group
```

| Entity | Fields |
|--------|--------|
| `message` | `msg_id`, `channel_id`, `sender_id`, `body`, `ts`, `seq` |
| `channel_member` | `channel_id`, `user_id`, `role` |
| `receipt` | `msg_id`, `user_id`, `delivered_at`, `read_at` |
| `device_session` | `user_id`, `conn_id`, `gateway_node` |

## High-level architecture

```text
Clients ⇄ WS Gateway fleet (sticky / conn registry)
              │
              ▼
         Chat service → append message (channel log / DB)
              │
              ├──► fan-out to online members via gateway lookup
              ├──► push service (offline)
              └──► history store (channel_id, seq)
```

## Deep dive: the crux

**Connections:** WS gateways are stateful for sockets but store **conn → user** and **user → gateway** in Redis. Scale gateways horizontally; reconnect with backoff + resume from last `seq`.

**Fan-out**
- 1:1 / small group: push to each online connection
- Large Slack channel: publish to channel pub/sub partition; gateways subscribed by membership — or write to channel log and notify online readers

**Ordering**
- Per-channel monotonic `seq` (or Snowflake `msg_id`) assigned by channel leader / single-writer partition
- Clients render by `seq`; gaps → fetch hole-fill from history API

**Delivery:** store durable first, then fan-out (or dual-write carefully). Client ACKs; retries use idempotent `client_msg_id`. Read receipts async, eventual.

| Choice | When |
|--------|------|
| Kafka/log per channel partition | Slack-scale channels, replay |
| Cassandra/Dynamo by channel | Simple history queries |
| WS only, no store | Toys — not interview senior answer |

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Sticky WS + registry | Efficient push | Registry consistency on node death |
| Total order per channel | Simple UX | Throughput ceiling / single writer |
| At-least-once | No silent loss | Dedup on client |
| Sync receipts | Accurate ticks | Extra write QPS |

## Failure modes & scale

- **Gateway crash:** clients reconnect; registry TTLs expire; replay from `last_ack_seq`
- **Partition split brain on seq:** single-writer via Kafka partition key = `channel_id`
- **Large group fan-out storm:** async queue + batch push; backpressure
- **Unread history:** cursor pagination; don’t load entire channel
- **Multi-device:** fan-out to all sessions; per-device ACK

## Interview trigger phrase

> “I’d make message append durable with a per-channel sequence first, then fan-out through a connection registry to WebSocket gateways — at-least-once with client idempotency keys, and hole-fill from history on gaps.”

## Exercise

1. How do **read receipts** work for a 10K-member channel without writing 10K rows synchronously on every read?
2. Design **multi-device** sync when phone is offline and desktop is online.
3. What happens to ordering if you allow **offline send** from two devices at once?
