# 11 · Distributed Systems — Distributed Transactions & Data Patterns

> Keeping data correct across services that each own their own database.

---

## Saga pattern

**Definition:** A way to manage a transaction spanning multiple services as a sequence of local transactions, each with a compensating action to undo it if a later step fails.

**Simple explanation:** You can't run a single ACID transaction across many services' databases. A saga breaks the workflow into local steps; if step 4 fails, you run "compensations" to undo steps 1–3 (not a rollback, but a semantic reversal). Two flavors: **orchestration** (a central coordinator drives the steps) vs **choreography** (services react to each other's events).

**Example:** Booking a trip = reserve flight → reserve hotel → charge card. If charging fails, run compensations: cancel hotel, cancel flight. Orchestration: a "trip coordinator" service calls each step and triggers undos. Choreography: each service emits events (`FlightReserved`) that the next service listens for.

---

## Two-phase commit (2PC)

**Definition:** A blocking protocol for atomic commit across nodes: a coordinator runs a *prepare* phase then a *commit/abort* phase.

**Simple explanation:** 2PC gives true all-or-nothing across databases but is fragile: participants lock resources during "prepare" and, if the coordinator crashes, stay locked and blocked indefinitely. It also doesn't tolerate partitions well. Fine within one tightly-coupled datacenter; avoided across microservices in favor of sagas.

**Example:** Move inventory between two warehouse DBs. Coordinator: "prepare?" → both lock and reply "ready" → "commit" → both apply. If the coordinator dies after "ready," both DBs hold locks, unable to proceed — the classic blocking problem.

---

## Outbox pattern

**Definition:** A technique to reliably publish events by writing the event to an "outbox" table in the *same* database transaction as the business data, then relaying it to the message broker separately.

**Simple explanation:** It solves the **dual-write problem** (see below). Instead of writing to the DB and then to Kafka (two systems that can partially fail), you write the business change and the event to the DB atomically. A separate process reads the outbox table and publishes to Kafka, marking rows as sent. The event is never lost or emitted without the data being saved.

**Example:** Placing an order: in one DB transaction, insert into `orders` AND insert `OrderPlaced` into `outbox`. A relay polls `outbox` (or tails the DB log) and pushes `OrderPlaced` to Kafka. If the app crashes after commit, the event is still safely in the outbox to be sent later.

---

## Change Data Capture (CDC)

**Definition:** Capturing row-level changes from a database's transaction log and streaming them to other systems in near real-time.

**Simple explanation:** Instead of apps explicitly emitting events, CDC watches the database's write-ahead log and turns every insert/update/delete into an event stream. Great for keeping caches, search indexes, and data warehouses in sync with the source DB without changing app code. Debezium is the common tool.

**Example:** A `products` table changes. Debezium reads Postgres's WAL and emits a `product.updated` event to Kafka; a consumer updates the Elasticsearch index. The search index stays fresh automatically, and it's also a clean way to implement the outbox relay.

---

## Event sourcing

**Definition:** Storing the full sequence of state-changing *events* as the source of truth, and deriving current state by replaying them, instead of storing only the latest state.

**Simple explanation:** Rather than saving "balance = $50," you save every event ("deposited $100," "withdrew $50") and compute the balance by replaying them. You get a complete audit history, time-travel (rebuild state at any past point), and easy debugging — at the cost of more storage and complexity (you often keep snapshots to avoid replaying millions of events).

**Example:** A bank account stores events: `Opened`, `Deposited $100`, `Withdrew $30`. Current balance ($70) is derived by folding the events. Want the balance as of last Tuesday? Replay events up to that timestamp.

---

## CQRS (Command Query Responsibility Segregation)

**Definition:** Separating the write model (commands that change state) from the read model (queries), often using different data stores optimized for each.

**Simple explanation:** Reads and writes have different needs — writes want normalized consistency, reads want denormalized speed. CQRS splits them: commands update the write store and publish events; a separate read store is built from those events, shaped exactly for queries. Pairs naturally with event sourcing. Adds complexity and read-side lag, so use it only where the scale justifies it.

**Example:** An e-commerce app: the write side records `OrderPlaced` events; a projection builds a denormalized `order_summary` read table (and an Elasticsearch index) optimized for the "my orders" page. Writes and reads scale independently.

---

## Dual-write problem

**Definition:** The reliability hazard when an operation must update two systems (e.g., a database and a message queue) with no shared transaction — one can succeed while the other fails.

**Simple explanation:** If you write to the DB then publish to Kafka as two separate steps, a crash in between leaves them inconsistent: data saved but no event (downstream never learns), or event sent but data not saved (phantom event). There's no atomicity across two systems. The **outbox pattern / CDC** is the standard fix.

**Example:** `db.save(order); kafka.publish(OrderPlaced);` — the process crashes after `db.save` but before `publish`. The order exists but no email/shipping is triggered. Fixing it with an outbox makes the save and the event one atomic DB write.
