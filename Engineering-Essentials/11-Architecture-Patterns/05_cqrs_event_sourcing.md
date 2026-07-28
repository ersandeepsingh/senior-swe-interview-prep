# CQRS & Event Sourcing

> **CQRS** splits read and write models. **Event sourcing** stores the truth as an append-only stream of events, rebuilding state by replay. Powerful — and easy to over-apply.

## Plain English

They pair well but are **independent**: you can CQRS without event sourcing; you can event-source without fancy CQRS. Don't default either for simple CRUD.

```text
  Command: PlaceOrder
      → validate → append events → update write model
      → async projection → Read DB / search index

  Query: GetOrderView(id)  → hit read model (not replay every time)
```

## Essentials (must-know for this topic)

### CQRS vs event sourcing (keep them straight)

| | **CQRS** | **Event sourcing** |
|---|----------|-------------------|
| Core idea | Split **write** model from **read** model | Source of truth = **append-only events** |
| Storage | Often different DBs for read vs write | Event log (+ snapshots); state = fold |
| Main win | Scale/shape reads independently | Audit, replay, temporal queries |
| Main cost | Dual models + sync lag | Complexity, event schema evolution |
| Required together? | **No** | **No** |

### CQRS pieces

| Piece | Role |
|-------|------|
| **Command** | Intent to change state (`PlaceOrder`) — validates, mutates write side |
| **Query** | Read from denormalized view (not the write model) |
| **Projection** | Async (or sync) updater of read models / search indexes |

### Event sourcing pieces

| Piece | Role |
|-------|------|
| **Event** | Immutable fact (`PaymentCaptured`) — never edit history |
| **Fold / replay** | Rebuild current state from events |
| **Snapshot** | Speed up replay so you don't fold forever |
| **Compensating event** | Fix mistakes without mutating old events |

**When to reach for each:** CQRS when read/write shapes diverge at scale; event sourcing when you need a ledger/audit/replay story.

## Simple example

Bank ledger:

- Events: `Deposited(100)`, `Withdrawn(30)`, `Withdrawn(20)`.
- Balance = 50 by folding.
- Read side: daily balances table for statements; fraud service consumes the same event stream.

Don't event-source your user profile CRUD unless you need the audit/replay story.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| CQRS | Independent scale/shape of reads vs writes | Dual models, sync lag |
| Event sourcing | Perfect audit, replay, temporal queries | Complexity, schema evolution of events |
| Sync read model update | Stronger read-after-write | Couples write latency to projections |
| Async projections | Faster writes | Stale reads; need UX for “eventual” |

## Pitfalls

- **Using both for a simple CRUD app** — ceremony without benefit.
- **Mutable event history** — events are immutable; fix with compensating events.
- **Event schema chaos** — need versioning/upcasters from day one.
- **Replaying forever without snapshots** — rebuilds get slow.
- **Expecting immediate read-your-writes** without a strategy (read write model, or wait for projection).

## Interview trigger phrase

> “I'd reach for **CQRS** when read and write shapes diverge at scale, and **event sourcing** when the business needs an audit/replayable ledger — not as a default for every service.”

## Exercise

For an inventory system, list one reason CQRS helps and one reason event sourcing might be overkill. What would you store as the source of truth instead?
