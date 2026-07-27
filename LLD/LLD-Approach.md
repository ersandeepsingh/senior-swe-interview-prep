# How to Approach an LLD Problem in the Interview

A **45–60 minute** LLD / machine-coding round tests OOP modeling, the *right* pattern at the *right* seam, and clean extensibility — not memorized UML or a full production system.

Interviewers care that you: clarify, name entities, pick 1–2 load-bearing patterns, code a working skeleton, then call out concurrency / testing / extension points.

Use this as a fixed script. Rehearse it out loud on **Parking Lot**, **Rate Limiter**, or **Checkout**.

Deeper step guides: [10-Interview-Round-Playbook/](10-Interview-Round-Playbook/README.md)

---

## Minute budget (45–60 min)

| Step | Time | Goal |
|------|------|------|
| 1. Clarify & scope | ~5 min | Functional requirements; cut scope out loud |
| 2. Entities & relationships | ~8–10 min | Nouns → types; verbs → methods; invariants |
| 3. Pick load-bearing patterns | ~3–5 min | Name 1–2 patterns and *why* |
| 4. Code skeleton + one E2E flow | ~25–35 min | Interfaces + core classes + working happy path |
| 5. Concurrency, extensibility, testing | ~5–10 min | Senior signal even if not fully coded |
| Buffer | ~2 min | Follow interviewer redirects |

If they say “just code,” still spend 2 minutes stating MVP and entities — then code.

---

## Step 1 — Clarify & scope (~5 min)

### What to do

1. Restate the problem in one sentence.
2. Ask questions that **change the design** (not trivia).
3. Propose an **MVP**.
4. Explicitly cut: “I’ll skip real DB/payments/UI; focus on domain model + core flow.”

### Ask these (adapt per problem)

- Actors: who uses the system? (user, admin, system job)
- Core operations for MVP? (park/unpark, place order, get/put cache…)
- Rules / constraints? (spot types, pricing, capacity, expiry)
- Single machine in-memory OK? Persistence required?
- Concurrency expected? (two users book same seat)
- What can change tomorrow? (new payment method, new pricing, new notification channel)

### Phrases that sound senior

> “I’ll restate: multi-level parking lot — park, unpark, ticket, fee on exit.”

> “For this round I’ll **skip** real payments, DB, and UI — domain model + allocation + pricing. Sound OK?”

> “I’ll assume in-memory single process first; I’ll call out locking for concurrent park.”

### Tiny example (Parking Lot)

**MVP**
- Floors → spots (type + occupied)
- `park(vehicle)` → ticket; `unpark(ticketId)` → fee
- Hourly pricing by vehicle type

**Cut**
- Payment gateway, reservations, EV charging, distributed locks, persistence

---

## Step 2 — Entities & relationships (~8–10 min)

### What to do

1. List **nouns** → candidate types/structs.
2. List **verbs** → methods on the right owner.
3. State **relationships** (has-a / belongs-to).
4. State **invariants** (rules that must always hold).

### Template

```text
Entities: ParkingLot, Floor, Spot, Vehicle, Ticket, PricingStrategy
Relations: Lot has Floors; Floor has Spots; Ticket links Vehicle + Spot + entry time
Invariants: one vehicle per spot; fee ≥ 0; can’t unpark unknown ticket
```

### Ownership rule

Put behavior next to the data that owns the rule:

| Behavior | Owner |
|----------|--------|
| Is this spot free / matching type? | `Spot` / `Floor` |
| Find a free spot & issue ticket | `ParkingLot` (orchestrator) |
| Compute fee | `PricingStrategy` (not God-lot) |
| Ticket identity + timestamps | `Ticket` |

### Phrases

> “Nouns become types; verbs become methods. `ParkingLot` orchestrates; it shouldn’t know SMS templates.”

> “Progress/fee depends on *who* + *what* — so that state lives on Ticket/Enrollment, not on the catalog Course.”

### Don’t

- 20 tiny classes with no orchestration
- One God class that does validation, pricing, persistence, and notifications

---

## Step 3 — Pick load-bearing patterns (~3–5 min)

Name **1–2 patterns** that carry the design. Don’t pattern-stuff.

### Quick map (most common)

| If the problem has… | Reach for… |
|---------------------|------------|
| Swappable algorithms (pricing, payment, sort, assign) | **Strategy** |
| Lifecycle / allowed transitions (order, vending, ticket) | **State** |
| Notify many listeners on change | **Observer** |
| Create families / hide construction | **Factory** / Abstract Factory |
| Many optional fields / step-by-step build | **Builder** |
| Add behavior without rewriting core (log, retry, encrypt) | **Decorator** |
| Undo/redo or queued actions | **Command** (+ Memento) |
| Tree of same interface (files/folders) | **Composite** |
| Tomorrow’s new type shouldn’t edit a hub `if/else` | **OCP** via Strategy/Factory |
| Service must not depend on concrete Email/SMS | **DIP** + inject interfaces |

### Phrases

> “Pricing will change → **Strategy**. Spot allocation stays in the lot. Notifications → **Observer** if we fan out.”

> “I’m *not* using Visitor here — YAGNI for this scope.”

### Parking Lot

- **Strategy** — pricing (hourly / flat / premium)
- Optional later: **Factory** for vehicle/spot types; locking for concurrency

---

## Step 4 — Code skeleton + one E2E flow (~25–35 min)

### Goal

Interfaces + key classes + **one working happy path**. Stubs are fine if you say so.

### Coding order (reliable)

1. Interfaces / small protocols first (`PricingStrategy`, `PaymentMethod`, …)
2. Core entities (`Spot`, `Ticket`, `Vehicle`)
3. Orchestrator service (`ParkingLot.park` / `unpark`)
4. One concrete strategy
5. `main` / test that runs park → unpark → print fee
6. Then extend (second strategy, observer, concurrency note)

### Skeleton sketch (Go-flavored)

```go
type PricingStrategy interface {
	Calculate(ticket Ticket, exitTime time.Time) float64
}

type ParkingLot struct {
	floors  []Floor
	pricing PricingStrategy
	tickets map[string]Ticket
}

func (p *ParkingLot) Park(v Vehicle) (Ticket, error) { /* find spot, mark occupied, issue ticket */ }
func (p *ParkingLot) Unpark(ticketID string) (float64, error) { /* free spot, price, return fee */ }
```

### Rules while coding

- **Compile/run often** — a working thin slice beats a perfect unfinished design
- Prefer **composition** over deep inheritance
- Keep interfaces **small** (ISP)
- Inject dependencies in constructors (DIP) — wire concretes in `main`
- Speak as you type: “This is the strategy seam for tomorrow’s flat rate.”

### Phrases

> “I’ll get park/unpark working with hourly pricing, then add a second strategy to show OCP.”

> “Repository is an interface — in-memory now, DB later.”

---

## Step 5 — Concurrency, extensibility, testing (~5–10 min)

Even if time is short, **say these out loud**. This is the senior differentiator.

### Extensibility

> “New pricing → new `PricingStrategy` struct, no change to `ParkingLot`.”

> “New notifier → implement Observer / NotificationSender, register it.”

### Concurrency (when relevant)

| Situation | What to say / do |
|-----------|------------------|
| Two park calls, one spot | Mutex / synchronized allotment; check-then-act is a race |
| Booking seats / inventory | Hold/lock with TTL; idempotent confirm |
| Cache get/put | Mutex or concurrent map; define single-flight for stampede |

> “I’d guard spot allocation with a lock so two threads can’t take the same spot.”

### Testing

> “Pure domain fee calculation is unit-testable; I’d inject a fake clock and fake strategy.”

> “Table-driven tests for park when full / wrong vehicle type / happy path.”

### Error handling

- Fail fast at boundaries (invalid ticket, lot full)
- Domain errors vs panic (panic only for programmer bugs)

---

## SOLID checklist (use lightly, correctly)

| Principle | 10-second check |
|-----------|-----------------|
| **SRP** | Is this type doing two jobs (price + email)? |
| **OCP** | Can I add a payment type without editing a fat `switch`? |
| **LSP** | Can every implementer honor the interface contract? |
| **ISP** | Am I forcing Video to implement `Attempt()`? |
| **DIP** | Does the service depend on `Notifier` or `SmtpEmail`? |

Also: **DRY / KISS / YAGNI** — don’t invent AbstractFactoryProviderBuilder for one pricing rule.

---

## Communication tips (senior signal)

1. **Talk while designing** — narrate entities and seams.
2. **Drive, then check in** — “I’ll use Strategy for pricing — OK?”
3. **One E2E path before polish** — working demo > perfect class diagram.
4. **Trade-offs > pattern bingo** — say what you gain/give up.
5. **Follow the interviewer** — if they push concurrency, prioritize locking over a fourth pattern.
6. **Time-box** — at ~35 min you should be mid-happy-path, not still drawing boxes.

---

## Anti-patterns (avoid these)

| Anti-pattern | Do instead |
|--------------|------------|
| Code before clarifying MVP | 5 min scope + entities |
| Pattern stuffing (5 patterns, no flow) | 1–2 load-bearing patterns |
| God class service | Orchestrator + strategies/repositories |
| Fat interfaces | Split by role (Playable / Readable) |
| Ignoring “tomorrow we may add X” | Put a Strategy/Factory seam there |
| Never mentioning races | Call out lock/idempotency even if stubbed |
| Building full DB/UI framework | In-memory + clear interfaces |

---

## Problem → pattern cheat sheet

| Classic problem | Load-bearing ideas |
|-----------------|--------------------|
| Parking Lot | Strategy (pricing), allocation ownership, optional lock |
| Vending / ATM / Order lifecycle | **State** |
| Notification / stock alerts | **Observer** (+ Strategy for channel) |
| Payment / checkout | Strategy (pay/discount), State (order) |
| LRU / LFU cache | Hash map + list; Strategy for eviction |
| Rate limiter | Strategy (token bucket / sliding window) |
| Elevator | State + Strategy (scheduling) |
| Splitwise | Strategy (split types), balance graph |
| Chess / games | Strategy (rules), State (turn) |
| Logger | Chain of Responsibility + Strategy (format/append) |
| Undo editor | Command + Memento |

---

## One-page cheat sheet (memorize)

```text
1. Clarify + cut scope
2. Entities, relations, invariants
3. Name 1–2 patterns (Strategy / State / Observer / Factory…)
4. Interfaces → entities → orchestrator → one E2E demo
5. Say: extensibility seam, concurrency, how you’d test
```

---

## Interview-ready opener

> “I’ll clarify requirements and cut scope, identify entities and invariants, pick one or two patterns for the extension seams, implement a thin end-to-end flow, then call out concurrency, testing, and how we’d add the next variant without rewriting the core.”

---

## Practice loop

1. Pick: Parking Lot, Rate Limiter, LRU, Notification Service, Vending Machine, Checkout, BookMyShow seats.
2. Time-box 45–60 min with this script.
3. Grade yourself: Did you clarify? Working demo? Named seams? Mentioned races/tests?
4. Drill details in [10-Interview-Round-Playbook/](10-Interview-Round-Playbook/README.md) and patterns under [LLD-Patterns-Senior-SWE.md](LLD-Patterns-Senior-SWE.md).
