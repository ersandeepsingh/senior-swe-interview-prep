# Incident Response & Postmortems

> When production hurts: **mitigate first**, then find root cause, then write a **blameless** postmortem so the system (not the person) gets fixed.

## Plain English

Incidents are practiced theater: detect → triage → mitigate → communicate → resolve → learn. Humans will always err; systems should absorb mistakes (safer deploys, better alerts, guardrails).

```text
  Bad:  "Alice pushed bad config"
  Good: "Config change had no canary; rollback took 40m; alert was on CPU not error rate"
```

## Essentials (must-know for this topic)

### Response playbook (order matters)

| Step | Action |
|------|--------|
| 1. **Detect** | Alert / user report |
| 2. **Triage** | Severity, blast radius, ownership |
| 3. **Mitigate** | Restore service first (rollback, kill switch, scale, failover) |
| 4. **Communicate** | Status page / channel; clear **incident commander** |
| 5. **Resolve** | Confirm SLIs healthy |
| 6. **Learn** | Blameless postmortem + owned action items |

**Mitigate before deep debug** while users are burning.

### Severity & roles

| Idea | Meaning |
|------|---------|
| **Sev model** | Sev-1 user-facing outage ≠ Sev-3 cosmetic bug |
| **Incident commander (IC)** | Owns decisions/comms — not everyone debugs at once |
| **Rollback / kill switch** | Preferred mitigate over “fix forward” under pressure |

### Blameless postmortem

| Include | Avoid |
|---------|-------|
| Timeline of facts | Naming/shaming individuals |
| Contributing **system** factors | “Be more careful” as the only fix |
| Action items with **owner + date** | Orphan TODOs / theater |

Ask *what conditions allowed this*, not *who screwed up*.

## Simple example

3am: checkout error rate 15%.

| Step | Action |
|------|--------|
| Declare | Sev-1, IC assigned, bridge opened |
| Mitigate | Rollback last deploy **or** flip flag off new payment path |
| Verify | Error rate < 0.1%, p99 back |
| Comms | "Checkout degraded 14:02–14:18 UTC; mitigated by rollback" |
| Postmortem | Timeline, contributing factors, 3 concrete follow-ups with dates |

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Mitigate before deep debug | Faster user recovery | May destroy forensic state (log carefully first) |
| Blameless culture | Honest writeups | Feels soft if leadership still punishes |
| Heavy process for every blip | Consistency | Fatigue on Sev-3s |
| Fast rollback culture | Safe deploys | Need good feature flags / migrations |

## Pitfalls

- **Debugging forever while the site is down** — mitigate first.
- **Blame-heavy postmortems** — people hide facts next time.
- **Action items with no owner/date** — postmortem theater.
- **No severity model** — everything is “urgent” or nothing is.

## Interview trigger phrase

> “I'd **mitigate first** — rollback or kill switch — then run a **blameless postmortem** with owned action items that harden detection and prevent the same failure mode.”

## Exercise

A bad feature flag default took payments offline for 25 minutes. Write three **system** action items (not “be more careful”) you'd put in the postmortem.
