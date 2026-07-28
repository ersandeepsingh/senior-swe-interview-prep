# Testing Strategy

> Tests are a **pyramid of confidence**, not a pile of E2E. Seniors choose the cheapest test that catches the risk — and use **contract tests** where services meet.

## Plain English

Also: **smoke** tests post-deploy; **snapshot** tests sparingly (easy to rubber-stamp). CI gate: unit + integration on PR; E2E on main/nightly if slow.

```text
         /\
        /E2E\         few, slow, brittle, high confidence on journeys
       /------\
      / Integr.\      middling: DB, queue, HTTP against real-ish deps
     /----------\
    / Unit tests \    many, fast, precise: pure logic
   /--------------\
```

## Essentials (must-know for this topic)

### Test pyramid layers

| Layer | What you test | Catch | Volume |
|-------|---------------|-------|--------|
| **Unit** | Functions/classes in isolation | Logic bugs | Many, fast |
| **Integration** | Your code + DB/Redis/HTTP | Wiring, SQL, serializers | Medium |
| **E2E / UI** | Full system through UI/API | Real user paths | Few, slow |
| **Contract** | Consumer expectations vs provider | Breaking API changes between services | At boundaries |
| **Load / chaos** | Perf and failure | Scale and resilience gaps | Periodic |

### Anti-pattern: ice-cream cone

| Shape | Meaning |
|-------|---------|
| **Pyramid** | Lots of units → some integration → thin E2E |
| **Ice-cream cone** | Tons of E2E, almost no units → slow/flaky CI |

### What belongs where (example)

| Risk | Cheapest layer |
|------|----------------|
| Fee calculation bug | Unit |
| Idempotency unique constraint | Integration (real DB) |
| Renamed JSON field between services | **Contract** (catches first) |
| “Buy item” happy path | One thin E2E |

**Interview line:** cheapest test that catches the risk; contracts enable independent deploys.

## Simple example

Payment charge:

1. **Unit:** fee calculation, idempotency key normalization.
2. **Integration:** handler + Postgres unique constraint on idempotency key (testcontainers).
3. **Contract:** Order service's expected `POST /charges` schema vs Payment's OpenAPI (Pact or similar).
4. **E2E:** one happy-path “buy item” in staging.
5. Don't E2E every validation error — units cover those.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Heavy unit focus | Speed, precision | Miss integration bugs |
| Heavy E2E focus | “Real” confidence | Slow CI, flaky fails |
| Contract tests | Safe independent deploys | Upfront consumer/provider discipline |
| Mocking everything | Fast units | Mocks lie; false green |

## Pitfalls

- **Ice-cream cone** — tons of E2E, almost no units.
- **Flaky E2E** ignored → culture of “re-run CI.”
- **Testing implementation details** (private methods) instead of behavior.
- **No test for idempotency / concurrency** where money/data races matter.
- **Skipping contract tests** in microservices → break consumers at runtime.
- **100% coverage as a goal** — incentivizes useless asserts.

## Interview trigger phrase

> “I'd keep a **pyramid**: fast units for logic, integration for DB/wiring, a **thin E2E** smoke path, and **consumer-driven contracts** at service boundaries so we can deploy independently.”

## Exercise

You own Order and Payment services. List one test at each layer (unit, integration, contract, E2E) for “place order and charge card,” and which layer catches a renamed JSON field first.
