# Mediator

> Define an object that **centralizes complex communication** so components don’t refer to each other explicitly.

## Plain English

Chat users don’t message each other peer-to-peer in code; they talk to a `ChatRoom` that routes. Air-traffic control, UI form fields that update each other — the mediator sits in the middle and cuts the N² coupling.

## Why seniors get asked this

When every widget/service knows every other, graphs become spaghetti. Seniors propose a hub — carefully, without creating a God object.

## Real-world analogy

An **airport control tower**: planes don’t coordinate pairwise; they talk to the tower.

## Example

### Python

```python
from __future__ import annotations
from abc import ABC, abstractmethod


class ChatMediator(ABC):
    @abstractmethod
    def send(self, from_user: str, message: str) -> None: ...

    @abstractmethod
    def join(self, user: User) -> None: ...


class ChatRoom(ChatMediator):
    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    def join(self, user: User) -> None:
        self._users[user.name] = user
        user.mediator = self

    def send(self, from_user: str, message: str) -> None:
        for name, user in self._users.items():
            if name != from_user:
                user.receive(from_user, message)


class User:
    def __init__(self, name: str) -> None:
        self.name = name
        self.mediator: ChatMediator | None = None

    def send(self, message: str) -> None:
        assert self.mediator
        self.mediator.send(self.name, message)

    def receive(self, from_user: str, message: str) -> None:
        print(f"{self.name} got [{from_user}]: {message}")


room = ChatRoom()
a, b = User("Ada"), User("Bob")
room.join(a)
room.join(b)
a.send("hi")
```

### Go

```go
type Mediator interface {
    Send(from, msg string)
    Join(u *User)
}

type ChatRoom struct {
    users map[string]*User
}

func NewChatRoom() *ChatRoom {
    return &ChatRoom{users: map[string]*User{}}
}

func (c *ChatRoom) Join(u *User) {
    c.users[u.Name] = u
    u.Room = c
}

func (c *ChatRoom) Send(from, msg string) {
    for name, u := range c.users {
        if name != from {
            u.Receive(from, msg)
        }
    }
}

type User struct {
    Name string
    Room Mediator
}

func (u *User) Send(msg string) { u.Room.Send(u.Name, msg) }
func (u *User) Receive(from, msg string) {
    fmt.Printf("%s got [%s]: %s\n", u.Name, from, msg)
}
```

## When to use

- Many-to-many interactions create tangled references.
- You want reusable colleagues that only know the mediator interface.
- UI dialogs / workflow coordinators with interrelated fields.

## When not to use / pitfalls

- Few components with simple calls → mediator is overhead.
- Mediator becomes a **God class** that knows everything — split by subdomain.
- Don’t confuse with **Observer** (broadcast events) — Mediator *orchestrates* directed interactions; often both appear together.
- Harder to see call flow; keep methods intention-revealing.

## Interview trigger phrase

> “Components shouldn’t wire each other — I’d put routing in a ChatRoom mediator.”

## Exercise

A smart-home hub coordinates lights, thermostat, and alarms when “away mode” is set.

1. Sketch mediator methods vs peer-to-peer calls.
2. What’s the risk if the hub grows every feature?
3. Mediator vs Observer for “away mode activated”?
