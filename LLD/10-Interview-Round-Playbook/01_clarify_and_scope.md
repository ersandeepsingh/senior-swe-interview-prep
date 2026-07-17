# Step 1 — Clarify & Scope (~5 min)

Nail functional requirements, then **explicitly cut scope**. Seniors who skip this either over-build or miss the real constraint.

## Minute budget

| Min | Do this |
|-----|---------|
| 0–1 | Restate the problem in one sentence |
| 1–3 | Ask clarifying questions (capacity, vehicle types, pricing, concurrency) |
| 3–5 | Propose MVP + explicit out-of-scope; get a nod |

## Exact phrases to say

- “I’ll restate: multi-level parking lot — park, unpark, issue ticket, charge on exit.”
- “Before I design: how many floors/spot types? Hourly vs flat pricing? One entry/exit or many?”
- “For this round I’ll **skip** real payments, DB, and UI — focus on domain model + allocation + pricing. Sound OK?”
- “I’ll assume single process in-memory first; I’ll call out locking for concurrent park if we have time.”

## Worked example — Parking Lot

**Ask (pick 4–5, don’t interrogate):**
1. Spot types: Compact / Large / Motorcycle?
2. Allocation rule: nearest to entry? any free of matching type?
3. Pricing: hourly by vehicle type? free first N minutes?
4. Concurrent park/unpark? (yes for senior signal)
5. Multi-gate / multiple attendants?

**Agree MVP:**
- Floors → spots with type + occupied flag
- `park(vehicle)` → ticket; `unpark(ticketId)` → fee
- Simple hourly pricing by vehicle type
- In-memory; one happy-path demo

**Explicitly cut:** payments gateway, reservations, EV charging, valet, persistence, distributed locks.

## Common mistakes

- Jumping into classes before confirming vehicle/spot types
- Building “enterprise” persistence on minute 2
- Never saying what’s out of scope (looks unfocused)
- Asking 15 questions — aim for 4–6 that change the design

## Interviewer signals

| Signal | Meaning |
|--------|---------|
| “Keep it simple” / “Whatever you prefer” | Pick defaults and state them |
| “What about two cars same spot?” | They want concurrency awareness later |
| Pushes pricing complexity early | Strategy is load-bearing — note it |

## Exercise / checklist

- [ ] One-sentence restatement said out loud
- [ ] ≥3 clarifying questions asked
- [ ] MVP listed in ≤5 bullets
- [ ] ≥2 items explicitly cut with “I’ll skip…”
- [ ] Interviewer confirmed or you stated defaults clearly
