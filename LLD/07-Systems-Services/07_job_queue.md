# Job Queue / Message Broker

> Enqueue, dispatch, ack, retry → **Producer–Consumer + Observer**. 🔴

## Scope / Requirements

**In scope**
- Topics/queues; producers enqueue messages; consumers pull/push.
- Ack / nack; retry with backoff; dead-letter after max attempts.
- At-least-once delivery semantics (state clearly).

**Out of scope**
- Full Kafka partitions/ISR, exactly-once transactions, cross-DC replication.

**Domain invariants**
- Message stays invisible to other workers until ack, nack, or visibility timeout.
- Attempts increment on each delivery; > maxAttempts → DLQ.
- Ack of unknown/already-final message is idempotent no-op.
- Ordering: per-queue FIFO *best effort* in single-node in-memory broker (mention partitions for scale).

## Core Entities & Responsibilities

| Entity | Responsibility |
|--------|----------------|
| `Message` | Id, payload, attempts, visibleAt. |
| `Queue` | Storage + inflight set. |
| `Broker` | Enqueue, dequeue, ack, nack. |
| `Worker` / Consumer | Process + ack. |
| `DeadLetterQueue` | Failed messages. |
| `Observer` | Metrics on enqueue/ack/fail. |

## Key Interfaces / Patterns

- **Producer–Consumer** with bounded buffer.
- **Observer** for ops metrics.
- **Command** optional: message handler registry by type.

## End-to-End Flow

1. Producer `enqueue("emails", payload)`.
2. Worker `dequeue` → process → `ack`.
3. On failure `nack` → backoff → redeliver; eventually DLQ.

## Python Skeleton

```python
from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import Lock
from typing import Any, Callable, Optional
import itertools
import uuid


@dataclass
class Message:
    id: str
    queue: str
    payload: Any
    attempts: int = 0
    visible_at: datetime = field(default_factory=datetime.utcnow)


class Broker:
    def __init__(self, max_attempts: int = 3, visibility_sec: int = 30):
        self.max_attempts = max_attempts
        self.visibility = timedelta(seconds=visibility_sec)
        self._queues: dict[str, deque[Message]] = {}
        self._inflight: dict[str, Message] = {}
        self._dlq: deque[Message] = deque()
        self._mu = Lock()
        self.observers: list[Callable[[str, Message], None]] = []

    def _emit(self, event: str, msg: Message) -> None:
        for obs in self.observers:
            obs(event, msg)

    def enqueue(self, queue: str, payload: Any) -> str:
        msg = Message(id=str(uuid.uuid4()), queue=queue, payload=payload)
        with self._mu:
            self._queues.setdefault(queue, deque()).append(msg)
        self._emit("enqueue", msg)
        return msg.id

    def dequeue(self, queue: str, now: datetime | None = None) -> Optional[Message]:
        now = now or datetime.utcnow()
        with self._mu:
            q = self._queues.setdefault(queue, deque())
            # promote newly visible (simple scan for interview)
            for _ in range(len(q)):
                msg = q[0]
                if msg.visible_at > now:
                    break
                q.popleft()
                msg.attempts += 1
                msg.visible_at = now + self.visibility
                self._inflight[msg.id] = msg
                self._emit("dequeue", msg)
                return msg
        return None

    def ack(self, message_id: str) -> None:
        with self._mu:
            msg = self._inflight.pop(message_id, None)
        if msg:
            self._emit("ack", msg)

    def nack(self, message_id: str, now: datetime | None = None) -> None:
        now = now or datetime.utcnow()
        with self._mu:
            msg = self._inflight.pop(message_id, None)
            if not msg:
                return
            if msg.attempts >= self.max_attempts:
                self._dlq.append(msg)
                self._emit("dlq", msg)
                return
            # exponential backoff sketch
            delay = timedelta(seconds=2 ** msg.attempts)
            msg.visible_at = now + delay
            self._queues[msg.queue].append(msg)
            self._emit("nack", msg)


def worker_loop(broker: Broker, queue: str, handler: Callable[[Message], None]) -> None:
    msg = broker.dequeue(queue)
    if not msg:
        return
    try:
        handler(msg)
        broker.ack(msg.id)
    except Exception:
        broker.nack(msg.id)
```

## Go Skeleton

```go
package broker

import (
    "sync"
    "time"

    "github.com/google/uuid" // or use your own id
)

type Message struct {
    ID        string
    Queue     string
    Payload   any
    Attempts  int
    VisibleAt time.Time
}

type Broker struct {
    mu          sync.Mutex
    queues      map[string][]*Message
    inflight    map[string]*Message
    DLQ         []*Message
    MaxAttempts int
    Visibility  time.Duration
}

func New(maxAttempts int, vis time.Duration) *Broker {
    return &Broker{
        queues: map[string][]*Message{}, inflight: map[string]*Message{},
        MaxAttempts: maxAttempts, Visibility: vis,
    }
}

func (b *Broker) Enqueue(queue string, payload any) string {
    b.mu.Lock()
    defer b.mu.Unlock()
    m := &Message{ID: uuid.NewString(), Queue: queue, Payload: payload, VisibleAt: time.Now()}
    b.queues[queue] = append(b.queues[queue], m)
    return m.ID
}

func (b *Broker) Dequeue(queue string) *Message {
    b.mu.Lock()
    defer b.mu.Unlock()
    q := b.queues[queue]
    now := time.Now()
    for i, m := range q {
        if m.VisibleAt.After(now) {
            continue
        }
        b.queues[queue] = append(q[:i], q[i+1:]...)
        m.Attempts++
        m.VisibleAt = now.Add(b.Visibility)
        b.inflight[m.ID] = m
        return m
    }
    return nil
}

func (b *Broker) Ack(id string) {
    b.mu.Lock()
    defer b.mu.Unlock()
    delete(b.inflight, id)
}

func (b *Broker) Nack(id string) {
    b.mu.Lock()
    defer b.mu.Unlock()
    m, ok := b.inflight[id]
    if !ok {
        return
    }
    delete(b.inflight, id)
    if m.Attempts >= b.MaxAttempts {
        b.DLQ = append(b.DLQ, m)
        return
    }
    m.VisibleAt = time.Now().Add(time.Second * time.Duration(1<<m.Attempts))
    b.queues[m.Queue] = append(b.queues[m.Queue], m)
}
```

## Concurrency / Consistency

- Inflight map + queue mutations under one lock, or per-queue locks.
- Visibility timeout recovery: redeliver if ack never comes (crash safety).
- Consumers must be idempotent under at-least-once.

## Extensions / Trade-offs / Pitfalls

- Pub/sub topics with multiple subscriptions (fan-out copies).
- Partition keys for ordering.
- Pitfall: ack before side effects committed; pitfall: infinite retry without DLQ.
- Push vs pull consumers.

## Interview Discussion Points

- At-least-once vs at-most-once vs exactly-once — what can you actually guarantee?
- Why visibility timeout instead of lock forever?
- How does this relate to Kafka consumer offsets?

## Exercise

Enqueue 1 message; fail processing twice; succeed on third; then force DLQ path with maxAttempts=2.

**Follow-ups**
1. Add an Observer that counts acks/DLQ.
2. Implement visibility timeout reclaim in `dequeue`.
3. Sketch multi-consumer competing on one queue safely.
