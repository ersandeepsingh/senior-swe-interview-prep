# 05 · Observability — Alerting & SRE Practices

> Turning signals into the right amount of human attention.

---

## SLI / SLO / SLA

**Definition:**
- **SLI (Indicator):** a measured number reflecting service health (e.g., % of requests under 300ms).
- **SLO (Objective):** the internal target for that SLI (e.g., 99.9% under 300ms).
- **SLA (Agreement):** a contractual promise to customers with consequences if missed (e.g., refunds).

**Simple explanation:** SLI is *what you measure*, SLO is *the goal you set*, SLA is *the promise with penalties*. SLOs are usually stricter than SLAs so you catch problems before breaking a contract.

**Example:**
- SLI: successful-request ratio = 99.95% this month.
- SLO: keep it ≥ 99.9%.
- SLA: "if availability drops below 99.5%, customer gets a 10% credit."

---

## Error budgets

**Definition:** The allowed amount of failure derived from an SLO (100% − SLO), treated as a resource you can spend.

**Simple explanation:** If your SLO is 99.9% availability, you're *allowed* 0.1% downtime — that's your budget. Spend it on risk (shipping features fast, doing risky migrations). If you blow the budget, you freeze feature work and focus on reliability. It turns "reliability vs velocity" into a data-driven decision instead of an argument.

**Example:** 99.9% monthly SLO = ~43 minutes of allowed downtime. A bad deploy burned 30 of those minutes. With 13 left, the team slows risky releases for the rest of the month.

---

## Alerting philosophy (symptoms not causes)

**Definition:** Alert on user-visible symptoms rather than internal causes.

**Simple explanation:** Don't page a human for "CPU is 90%" — high CPU may be harmless. Page for "users are getting errors" or "checkout latency is above SLO." Symptom-based alerts catch real pain (including causes you never anticipated) without waking people for non-problems.

**Example:**
- ❌ Cause alert: "CPU > 90%" (fires constantly, often harmless).
- ✅ Symptom alert: "p99 checkout latency > 1s for 5 min" (means users are actually hurting).

---

## Alert fatigue

**Definition:** Desensitization caused by too many alerts, especially noisy or non-actionable ones.

**Simple explanation:** If the pager cries wolf 40 times a night, engineers start ignoring it — and miss the real fire. Every alert should be actionable ("a human must do something now") and urgent. Non-urgent things go to a ticket/dashboard, not a page.

**Example:** A team getting 200 alerts/week prunes to ~10 truly actionable ones tied to SLOs. On-call sleep improves and real incidents get faster response because the pager is trusted again.

---

## On-call & runbooks

**Definition:** A rotation of engineers responsible for responding to alerts, backed by **runbooks** — step-by-step guides for handling known issues.

**Simple explanation:** Someone is always designated to respond. A runbook is the "in case of fire" instructions linked from each alert, so a sleepy on-call engineer doesn't have to reinvent the fix at 3am. Ideally, common responses get automated away entirely.

**Example:** Alert "disk > 90%" links to a runbook: (1) check largest dirs, (2) rotate/compress old logs, (3) if still full, expand volume via this command. Later, steps 1–2 are automated.

---

## Availability math (nines)

**Definition:** Translating availability percentages ("nines") into concrete allowed downtime.

**Simple explanation:** Each extra nine cuts allowed downtime ~10x and costs disproportionately more to achieve. Knowing the numbers lets you set realistic targets.

**Example:**
| Availability | Downtime/year | Downtime/month |
|---|---|---|
| 99% (two nines) | ~3.65 days | ~7.2 hours |
| 99.9% (three nines) | ~8.77 hours | ~43 min |
| 99.99% (four nines) | ~52.6 min | ~4.3 min |
| 99.999% (five nines) | ~5.26 min | ~26 sec |

---

## MTTR / MTBF / MTTD

**Definition:** Reliability metrics — **MTTD** (mean time to detect), **MTTR** (mean time to recover/repair), **MTBF** (mean time between failures).

**Simple explanation:** MTTD = how fast you notice, MTTR = how fast you fix, MTBF = how often it breaks. Good observability lowers MTTD and MTTR; good engineering raises MTBF. Reducing MTTR is often the highest-leverage reliability win (you can't prevent all failures, but you can recover fast).

**Example:** Outage detected in 2 min (MTTD), fixed in 18 min (MTTR = 20 min total), and the service typically runs 30 days between incidents (MTBF).

---

## Incident response & blameless postmortems

**Definition:** A structured process for handling outages, followed by a blame-free written analysis of what happened and how to prevent recurrence.

**Simple explanation:** During an incident you triage, assign roles (incident commander, comms), mitigate, then resolve. Afterward you write a postmortem focused on *systems and process*, not punishing individuals — because blame makes people hide information, which makes systems less safe.

**Example:** After a 40-min outage, the postmortem documents timeline, root cause ("a deploy removed a required config"), impact, and action items ("add config validation to CI," "add a canary stage") — with zero finger-pointing at the deployer.
