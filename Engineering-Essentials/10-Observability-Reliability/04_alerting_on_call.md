# Alerting & On-Call

> Page humans only when **user-facing health** is at risk — and give them a path to act. SLIs, SLOs, and error budgets turn “feelings” into policy.

## Plain English

Alerting should map to **user pain**, not machine vanity. On-call hygiene: runbooks, clear ownership, escalation, and a culture where waking someone at 3am is expensive — so alerts must be worth it.

```text
  Good alert:  checkout success SLO burning 2% of monthly budget in 1 hour
  Bad alert:   CPU > 70% on one replica for 1 minute
```

**Alert fatigue** kills on-call: too many noisy pages → people ignore the real ones.

## Essentials (must-know for this topic)

### SLI / SLO / SLA / error budget

| Term | Meaning |
|------|---------|
| **SLI** | Measurable signal of user happiness (e.g. successful checkouts / total) |
| **SLO** | Internal target on that SLI (e.g. 99.9% over 30 days) |
| **SLA** | Contractual promise (often looser than SLO); credits/money if broken |
| **Error budget** | Allowed failure = `100% − SLO` (at 99.9% you may “spend” 0.1%) |

Burn budget fast → freeze risky deploys / page harder. Budget healthy → ship faster.

### What to page on

| Page | Don't page (ticket / auto-scale) |
|------|----------------------------------|
| Fast **error-budget burn** on a user journey | CPU > 70% alone |
| Sustained high error rate / latency SLO breach | Single replica blip for 1 minute |
| Payment / auth completely broken | Disk filling with hours of headroom |

| Burn rate | Meaning | Action |
|-----------|---------|--------|
| Slow burn | Slightly over budget | Ticket, next sprint |
| Fast burn | Budget gone in hours/days | **Page** immediately |

### On-call essentials

| Practice | Why |
|----------|-----|
| **Runbook** linked in alert | Page without a path = panic |
| **Severity model** | Not everything is Sev-1 |
| **Hysteresis / “for 5m”** | Stops flapping alerts |
| Symptom-based over cause-based | Pages map to user pain |

## Simple example

SLO: 99.9% of `/checkout` return non-5xx within 2s over 30 days.

Alert rule idea: “error rate such that remaining budget exhausts in < 2 hours” → page. “CPU high” alone → ticket or auto-scale, don't page.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Symptom-based alerts (errors, latency) | Pages map to user pain | Need good SLIs first |
| Cause-based alerts (disk full) | Catch infra early | Noise if not user-impacting |
| Tight SLO (99.99%) | High bar | Tiny budget → constant pages |
| Loose SLO | Calm on-call | Worse user experience accepted |

## Pitfalls

- **Paging on every WARNING log** — unreadably noisy.
- **No runbook** — page fires, engineer stares at Grafana guessing.
- **SLO without ownership** — pretty dashboard, no deploy policy when budget burns.
- **Flapping alerts** — no “for 5 minutes” / hysteresis → sleep destruction.

## Interview trigger phrase

> “I'd define **SLIs that mirror user journeys**, set an **SLO + error budget**, and page only on **fast burn** — with a runbook — so on-call stays actionable.”

## Exercise

You have 0.1% monthly error budget and burned half of it in one afternoon. Name **two** concrete engineering responses (process + technical) for the next week.
