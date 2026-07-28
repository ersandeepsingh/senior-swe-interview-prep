# Saga / Distributed Transactions

> Across services you usually **can't** have one ACID transaction. A **saga** is a sequence of local transactions with **compensations** (or orchestration) to keep the business consistent enough.

## Plain English

Classic 2PC (two-phase commit) across microservices is slow, fragile, and often unavailable. Instead: each service commits locally; if a later step fails, run **compensating** actions to undo earlier work (or use a coordinator to drive the flow).

```text
  Place order saga:
    1. Create Order (pending)
    2. Reserve Inventory
    3. Charge Payment
    4. Mark Order confirmed
  On fail at 3: Release Inventory + Cancel Order (compensations)
```

Sagas give **eventual consistency**, not immediate global ACID. Design UX for “pending” states.

## Essentials (must-know for this topic)

### Choreography vs orchestration

| | **Choreography** | **Orchestration** |
|---|------------------|-------------------|
| Control | Services emit/react to events | A **coordinator** tells each step what to do |
| Coupling | Looser | Coordinator knows the flow |
| Visibility | Harder to see whole saga | Clear state machine |
| Failure debugging | Emergent spaghetti risk | One place to inspect |
| Hotspot | Distributed | Coordinator can be a bottleneck |
| Sweet spot | Simple, few steps | Complex flows with many branches |

### Saga vs 2PC

| | Saga | 2PC |
|---|------|-----|
| Consistency | Eventual | Strong (while it works) |
| Availability | Services stay autonomous | Participants blocked/coupled |
| Failure handling | **Compensations** | Rollback of prepare phase |
| Interview default | Prefer saga across services | Rarely available / too fragile |

### Compensation reality

| Remember | Example |
|----------|---------|
| Compensations must be **idempotent** | Cancel charge twice → still one cancel |
| Not always perfect reverse | Can't “unsend” email → apology / ticket |
| Need saga ID + timeouts | Stuck “pending” needs recovery jobs |

## Simple example

Booking a flight + hotel:

1. Reserve flight (local commit).
2. Reserve hotel.
3. Charge card.
4. If charge fails → cancel hotel reservation, cancel flight hold.

Compensation isn't always perfect reverse (can't “unsend” email) — make compensations **business-meaningful** (send apology, open support ticket, mark refund pending).

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Saga | Autonomy, no distributed locks | Temporary inconsistency, complex failure modes |
| 2PC | Strong consistency | Latency, availability coupling |
| Orchestration | Visible state machine | Single place to scale/care for |
| Choreography | Loose coupling | Emergent spaghetti; hard debugging |

## Pitfalls

- **Compensations that aren't idempotent** — retrying cancel charges twice.
- **No timeout / stuck “pending”** — sagas need deadlines and recovery jobs.
- **Assuming compensation = rollback** — money and emails need explicit policies.
- **Chatty choreography** with no correlation ID / saga ID.

## Interview trigger phrase

> “I'd model the cross-service flow as a **saga** with **idempotent compensations** — orchestration when the flow is complex — and accept **eventual consistency** with clear pending states.”

## Exercise

Checkout: create order → reserve stock → charge → email. Payment fails after stock reserved. Write the compensation steps and one invariant you must still enforce (e.g. never oversell permanently).
