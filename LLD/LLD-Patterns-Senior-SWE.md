# LLD / Machine-Coding Pattern Playbook — Senior SWE Interview Prep

Organized by **category → sub-pattern → 1-line intent + where it shows up**.
LLD rounds test OOP modeling, design principles, and the *right* pattern applied at the *right* seam — not memorized UML. Each design problem is mapped to its **most critical** pattern (the one an interviewer is really probing), not every pattern it happens to touch.

Legend: 🟢 warm-up · 🟡 standard 45–60 min machine-coding · 🔴 hard / senior-signal

---

## 1. Design Principles (the "why" behind every choice)

- **SOLID — Single Responsibility** — A class has one reason to change → split a `God` service into focused collaborators.
- **SOLID — Open/Closed** — Extend behavior without editing existing code → add a new payment type via a new strategy, not an `if/else`.
- **SOLID — Liskov Substitution** — Subtypes must be swappable for their base → classic `Square extends Rectangle` violation.
- **SOLID — Interface Segregation** — No fat interfaces → split `Machine` into `Printer` / `Scanner` / `Fax`.
- **SOLID — Dependency Inversion** — Depend on abstractions → inject a `NotificationChannel` interface, not `EmailSender`.
- **DRY / KISS / YAGNI** — Don't repeat, keep simple, don't over-build → resist speculative generalization in an interview.
- **Composition over inheritance** — Favor has-a over is-a → model a `Character` with pluggable abilities, not a deep class tree.
- **Law of Demeter** — Talk to friends, not strangers → avoid `a.getB().getC().doX()` chains.
- **Encapsulation / immutability** — Hide state, prefer value objects → `Money`, `Coordinate` as immutable types.

## 2. Creational Patterns (how objects come into existence)

- **Singleton** — One shared instance, safely → thread-safe config / connection manager.
- **Factory Method** — Subclass decides which object to create → `NotificationFactory.create(type)`.
- **Abstract Factory** — Families of related objects → cross-platform UI widget kit (Mac vs Windows).
- **Builder** — Step-by-step construction of complex objects → build a `Pizza` / `HttpRequest` with optional parts.
- **Prototype** — Clone instead of re-construct → duplicate a configured game object.
- **Object Pool** — Reuse expensive objects → DB connection pool, thread pool.
- **Dependency Injection** — Supply collaborators from outside → constructor-inject repositories into a service.

## 3. Structural Patterns (how objects compose)

- **Adapter** — Make incompatible interfaces work together → wrap a 3rd-party payment SDK to your interface.
- **Decorator** — Add behavior at runtime without subclassing → add milk/sugar to a `Coffee`; add compression to a stream.
- **Facade** — Simple front over a complex subsystem → one `VideoConverter` hiding codecs/filters.
- **Composite** — Treat tree of objects uniformly → file-system files & folders; UI component tree.
- **Proxy** — Stand-in controlling access → lazy-loading / access-control / caching proxy.
- **Bridge** — Decouple abstraction from implementation → `Shape` × `Renderer` (vector vs raster).
- **Flyweight** — Share intrinsic state to save memory → glyph rendering, particles in a game.

## 4. Behavioral Patterns (how objects interact & delegate)

- **Strategy** — Interchangeable algorithms behind one interface → pluggable pricing / sorting / payment strategy.
- **Observer** — Notify subscribers on state change → pub/sub, stock-price tickers, event listeners.
- **State** — Behavior changes with internal state → vending machine, order lifecycle, traffic light.
- **Command** — Encapsulate a request as an object → undo/redo, job queue, remote-control buttons.
- **Chain of Responsibility** — Pass request along handlers → middleware pipeline, approval chain, ATM dispenser.
- **Template Method** — Fixed skeleton, overridable steps → data-import flow with custom parse step.
- **Iterator** — Traverse without exposing internals → custom collection iterator.
- **Mediator** — Centralize complex comms → chat room routing, air-traffic control.
- **Memento** — Capture/restore state → editor snapshots, game save points.
- **Visitor** — Add operations without changing classes → AST evaluation, tax calc over item types.
- **Interpreter** — Grammar → evaluator → simple rule/expression engine.
- **Null Object** — Neutral do-nothing default → avoid null checks with a no-op logger.

## 5. Concurrency Patterns (senior-critical — often the deciding round)

- **Producer–Consumer** — Decouple work via a bounded buffer → job queue with blocking queue.
- **Thread Pool / Executor** — Reuse worker threads → task scheduler / web server workers.
- **Read-Write Lock** — Many readers, one writer → cache with concurrent reads.
- **Future / Promise** — Async result placeholder → parallel fan-out then join.
- **Monitor / mutex / semaphore** — Guard critical sections & limit resources → bounded resource access.
- **Double-checked locking** — Lazy thread-safe init → safe singleton without locking every read.
- **Immutability for safety** — Share freely if never mutated → value objects across threads.
- **Actor model** — State owned by one actor, message-passing → each account processes its own txns.

## 6. Machine-Coding Problems — Core / Most-Asked

- **Parking Lot** — Multi-level lot: spot allocation, ticketing, pricing → State + Strategy + Factory. 🟡
- **Elevator System** — Multi-elevator scheduling & request dispatch → State + Strategy (scheduling). 🔴
- **Vending Machine** — Coin handling, dispense, refund → State pattern. 🟡
- **ATM Machine** — Auth, withdrawal, cash dispensing → State + Chain of Responsibility. 🟡
- **Library Management** — Books, members, borrow/return, fines → composition + repositories. 🟡
- **Movie Ticket Booking (BookMyShow)** — Seat locking, concurrency, payment → Concurrency + Strategy. 🔴
- **Splitwise** — Expense splitting, balances, settle-up → Strategy (split types) + graph settle. 🔴
- **Snake & Ladder / Board games** — Turn engine, dice, entities → composition + state. 🟡
- **Tic-Tac-Toe / Chess** — Board, moves, rules, win-check → Strategy (rules) + State. 🟡🔴

## 7. Machine-Coding Problems — Systems & Services

- **Rate Limiter** — Token bucket / sliding window / fixed window → Strategy per algorithm. 🟡
- **In-Memory Key-Value Store** — get/put with TTL & eviction → composition + eviction policy. 🟡
- **LRU / LFU Cache** — O(1) cache with eviction policy → hashmap + linked list; Strategy for policy. 🟡
- **Logging Framework** — Levels, appenders, formatters → Chain of Responsibility + Strategy. 🟡
- **Notification Service** — Email/SMS/Push channels → Strategy + Observer + Factory. 🟡
- **Task Scheduler / Cron** — Recurring & one-off jobs, priorities → priority queue + Command. 🔴
- **Job Queue / Message Broker** — Enqueue, dispatch, ack, retry → Producer–Consumer + Observer. 🔴
- **Distributed ID Generator** — Unique IDs (Snowflake-style) → concurrency + bit packing. 🟡
- **URL Shortener (LLD)** — Encode/decode, collision handling → Strategy (encoding) + repository. 🟡
- **File System (in-memory)** — Files/dirs, path ops → Composite pattern. 🟡
- **Text Editor / Undo-Redo** — Edit ops with history → Command + Memento. 🟡

## 8. Machine-Coding Problems — Domain / Product

- **Food Delivery (Swiggy/Zomato)** — Restaurants, orders, delivery assignment → Strategy + Observer. 🔴
- **Ride Hailing (Uber/Ola)** — Driver matching, pricing, trip state → State + Strategy (matching/pricing). 🔴
- **E-commerce Cart & Checkout** — Cart, discounts, payment, inventory → Strategy (discount/payment) + State (order). 🔴
- **Inventory / Warehouse** — Stock, reservations, replenishment → Observer + repository. 🟡
- **Hotel / Airline Booking** — Availability, reservation, cancellation → concurrency + State. 🔴
- **Online Coding Judge** — Submissions, verdicts, sandboxing → Command + State + Observer. 🔴
- **Stock Trading / Order Matching Engine** — Order book, match buy/sell → priority queues + Strategy. 🔴
- **Digital Wallet / Payment** — Balance, transactions, ledger → State + double-entry model + concurrency. 🔴
- **Card / Casino Games** — Deck, players, dealing, scoring → Factory + Strategy (game rules). 🟡
- **Coupon / Discount Engine** — Stackable rules & eligibility → Chain of Responsibility + Strategy. 🟡
- **Meeting Room / Calendar Scheduler** — Booking, conflicts, recurrence → interval logic + Observer. 🟡

## 9. Cross-Cutting Concerns to Model Well (senior signal)

- **Extensibility seams** — Where will requirements change? Put a Strategy/Factory there before you're asked.
- **Concurrency & consistency** — Seat/inventory locking, idempotency, race conditions → call these out proactively.
- **Error handling & validation** — Domain exceptions vs. return codes; fail fast at boundaries.
- **Pluggable persistence** — Repository interface so in-memory now, DB later (Dependency Inversion).
- **Observability hooks** — Events/observers for logging, metrics, notifications without coupling.
- **Testability** — Injected dependencies + pure domain logic so it's unit-testable.

---

## How to run an LLD round (senior playbook)

1. **Clarify & scope (5 min):** nail functional requirements, then explicitly cut scope ("I'll skip real payments/persistence, focus on the domain model").
2. **Identify entities & relationships (10 min):** nouns → classes, verbs → methods; state the core objects and how they relate out loud.
3. **Pick the load-bearing pattern(s):** name the 1–2 patterns that carry the design (usually **Strategy** for varying algorithms, **State** for lifecycle, **Observer** for notifications, **Factory** for creation) — don't pattern-stuff.
4. **Code the skeleton:** interfaces + key classes + one working flow end-to-end; leave stubs for the rest and say so.
5. **Call out concurrency, extensibility, and testing** even if you don't fully implement them — that's the senior differentiator.

Priority to drill if time is short: **Parking Lot, Elevator, Splitwise, Rate Limiter, LRU Cache, Notification Service, BookMyShow, Movie/Cart Checkout** — they exercise almost every pattern above and are the most repeated across senior loops.
