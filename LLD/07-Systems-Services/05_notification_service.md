# Notification Service

> Email/SMS/Push channels → **Strategy + Observer + Factory**. 🟡

## Scope / Requirements

**In scope**
- Send notification via one or more channels.
- Pluggable channel implementations; factory/registry by type.
- Optional: subscribers/observers for delivery events (sent/failed).
- Template + recipient + payload.

**Out of scope**
- Provider-specific SDKs, marketing campaigns, full preference center UI.

**Domain invariants**
- A notification has at least one channel target; send attempts are per channel.
- Channel failures shouldn’t necessarily fail others (policy: best-effort vs all-or-nothing — **state it**).
- User preferences may suppress a channel (check before send).
- Idempotency key optional for retries (mention).

## Core Entities & Responsibilities

| Entity | Responsibility |
|--------|----------------|
| `Notification` | Recipient, body/template, channels. |
| `Channel` | Strategy: `send(notification)`. |
| `ChannelFactory` | Create/lookup channel by name. |
| `NotificationService` | Orchestrate fan-out. |
| `DeliveryObserver` | On success/failure metrics/audit. |
| `PreferenceService` | Gate channels. |

## Key Interfaces / Patterns

- **Strategy — Channel.**
- **Factory / Registry** for channel types.
- **Observer** for metrics, audit log, webhooks.
- **Template Method (optional):** validate → render → send.

## End-to-End Flow

1. Client `notify(user, "order_shipped", channels=[EMAIL,SMS])`.
2. Service renders message; filters by preferences.
3. For each channel: `channel.send`; observers get `DeliveryEvent`.

## Python Skeleton

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable


class ChannelType(Enum):
    EMAIL = auto()
    SMS = auto()
    PUSH = auto()


@dataclass
class Notification:
    user_id: str
    subject: str
    body: str
    channels: list[ChannelType]


@dataclass
class DeliveryEvent:
    user_id: str
    channel: ChannelType
    ok: bool
    detail: str = ""


class Channel(ABC):
    @abstractmethod
    def send(self, n: Notification) -> None: ...


class EmailChannel(Channel):
    def send(self, n: Notification) -> None:
        print(f"EMAIL to={n.user_id} subject={n.subject} body={n.body}")


class SmsChannel(Channel):
    def send(self, n: Notification) -> None:
        print(f"SMS to={n.user_id} body={n.body}")


class PushChannel(Channel):
    def send(self, n: Notification) -> None:
        print(f"PUSH to={n.user_id} body={n.body}")


class ChannelFactory:
    def __init__(self):
        self._reg: dict[ChannelType, Channel] = {
            ChannelType.EMAIL: EmailChannel(),
            ChannelType.SMS: SmsChannel(),
            ChannelType.PUSH: PushChannel(),
        }

    def get(self, t: ChannelType) -> Channel:
        return self._reg[t]


Observer = Callable[[DeliveryEvent], None]


class NotificationService:
    def __init__(self, factory: ChannelFactory, preferences: dict[str, set[ChannelType]] | None = None):
        self.factory = factory
        self.preferences = preferences or {}
        self.observers: list[Observer] = []

    def subscribe(self, obs: Observer) -> None:
        self.observers.append(obs)

    def _emit(self, e: DeliveryEvent) -> None:
        for obs in self.observers:
            obs(e)

    def send(self, n: Notification) -> None:
        allowed = self.preferences.get(n.user_id)
        for ct in n.channels:
            if allowed is not None and ct not in allowed:
                self._emit(DeliveryEvent(n.user_id, ct, False, "suppressed"))
                continue
            try:
                self.factory.get(ct).send(n)
                self._emit(DeliveryEvent(n.user_id, ct, True))
            except Exception as ex:  # interview: narrow this
                self._emit(DeliveryEvent(n.user_id, ct, False, str(ex)))
```

## Go Skeleton

```go
package notify

import "fmt"

type ChannelType string

const (
    Email ChannelType = "email"
    SMS   ChannelType = "sms"
    Push  ChannelType = "push"
)

type Notification struct {
    UserID   string
    Subject  string
    Body     string
    Channels []ChannelType
}

type DeliveryEvent struct {
    UserID  string
    Channel ChannelType
    OK      bool
    Detail  string
}

type Channel interface {
    Send(n Notification) error
}

type EmailChannel struct{}

func (EmailChannel) Send(n Notification) error {
    fmt.Printf("EMAIL to=%s subject=%s\n", n.UserID, n.Subject)
    return nil
}

type SMSChannel struct{}

func (SMSChannel) Send(n Notification) error {
    fmt.Printf("SMS to=%s body=%s\n", n.UserID, n.Body)
    return nil
}

type Factory struct {
    reg map[ChannelType]Channel
}

func NewFactory() *Factory {
    return &Factory{reg: map[ChannelType]Channel{
        Email: EmailChannel{},
        SMS:   SMSChannel{},
    }}
}

type Observer func(DeliveryEvent)

type Service struct {
    Factory     *Factory
    Preferences map[string]map[ChannelType]bool
    Observers   []Observer
}

func (s *Service) Send(n Notification) {
    for _, ct := range n.Channels {
        if prefs, ok := s.Preferences[n.UserID]; ok && !prefs[ct] {
            s.emit(DeliveryEvent{n.UserID, ct, false, "suppressed"})
            continue
        }
        ch := s.Factory.reg[ct]
        if err := ch.Send(n); err != nil {
            s.emit(DeliveryEvent{n.UserID, ct, false, err.Error()})
            continue
        }
        s.emit(DeliveryEvent{n.UserID, ct, true, ""})
    }
}

func (s *Service) emit(e DeliveryEvent) {
    for _, obs := range s.Observers {
        obs(e)
    }
}
```

## Concurrency / Consistency

- Fan-out sends with worker pool; bound concurrency per provider.
- Retries with backoff + idempotency keys at provider.
- Observer should be non-blocking (queue) so metrics can’t stall sends.

## Extensions / Trade-offs / Pitfalls

- Priority channels; digest batching; template engine.
- Pitfall: hardcoding `if channel == email` in service.
- Dead-letter queue for permanent failures.

## Interview Discussion Points

- Strategy vs inheritance for channels?
- Where do user preferences live in the flow?
- Sync API vs async “accepted for delivery” — what do you return?

## Exercise

Send order confirmation via EMAIL+SMS; suppress SMS for a user via preferences; log DeliveryEvents.

**Follow-ups**
1. Register a new `SlackChannel` without editing `Send`.
2. Add retry once on failure inside channel decorator/proxy.
3. Discuss at-least-once vs exactly-once delivery claims.
