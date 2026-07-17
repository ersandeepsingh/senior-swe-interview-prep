# Mock Interview Rubric — 45–60 min LLD Round

Use this to self-grade Parking Lot (or Checkout) after a timed run. Score each row **0 / 1 / 2** (missing / partial / strong). Target **≥ 16 / 24** before looping harder problems.

## Timing (choose one)

| Mode | Clarify | Entities | Patterns | Code | Senior call-outs |
|------|---------|----------|----------|------|------------------|
| **45 min** | 4 | 8 | 4 | 24 | 5 |
| **60 min** | 5 | 10 | 5 | 30 | 10 |

Buffer 1–2 min for demo narration and Q&A.

## Rubric

| Area | 0 | 1 | 2 |
|------|---|---|---|
| **Clarify & scope** | Jumps to code | Some questions, fuzzy MVP | Clear MVP + explicit cuts + confirmed defaults |
| **Entities & relationships** | Vague nouns | List of classes, weak ownership | Ownership + APIs stated; ticket/spot/lot clear |
| **Load-bearing patterns** | Pattern salad or none | Names a pattern weakly | 1–2 patterns at the right seam; rejects YAGNI |
| **Working E2E flow** | Doesn’t run | Partial park or unpark | park→unpark with fee demoable |
| **Code quality** | God class / no types | Some structure | Interfaces, SRP-ish split, readable names |
| **Failure paths** | Happy path only | Mentions full lot | Codes or clearly handles ≥1 error |
| **Concurrency** | Silent | Vague “use locks” | Names race + critical section / approach |
| **Extensibility** | “Add ifs later” | Mentions Strategy | Points to concrete seam for next req |
| **Testing** | None | “I’d write tests” | ≥3 concrete cases + DI/clock note |
| **Communication** | Silent coding | Occasional updates | Narrates decisions; time-aware stubs |
| **Trade-offs** | Never | One shallow trade-off | States 2 trade-offs (e.g. first-free vs nearest) |
| **Senior composure** | Panics / rewrites all | Recovers slowly | Freezes scope under time pressure; finishes demo |

**Max 24.** Banding: **0–11** rebuild process · **12–15** passable mid · **16–19** senior-ready · **20–24** strong.

## Self-review checklist (post-mock)

**Process**
- [ ] Stayed inside the minute budget (±3 min OK)
- [ ] Said “I’ll skip …” at least twice
- [ ] Named ≤2 patterns before coding
- [ ] Had a runnable happy path before polish

**Domain (Parking Lot)**
- [ ] Spot types + ticket + fee path exist
- [ ] Pricing not hard-coded inside `unpark` body (or you noted the smell)
- [ ] Double-booking race called out

**Signals you missed** (note for next drill)
- [ ] Interviewer hint ignored? _____
- [ ] Overbuilt component? _____
- [ ] Under-communicated for ___ minutes

**One improvement for next mock** (write one sentence):

> _______________________________________________

## Alternate domain — Checkout (same rubric)

If you swap domains: Cart → Order (State) + Discount/Payment (Strategy) + inventory reserve race. Same five steps and scoring rows apply; only entity names change.

## How to use

1. Record yourself or pair for 45/60 min.
2. Score immediately with the table (be harsh on communication and races).
3. Re-run **only** the weakest step (often clarify or concurrency talk) for 10 min.
4. Full remock after reviewing [01](01_clarify_and_scope.md)–[05](05_concurrency_extensibility_testing.md).
