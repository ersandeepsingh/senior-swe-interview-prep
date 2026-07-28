# Feature Flags

> Decouple **deploy** from **release**. Ship dark code, turn it on for 1% of users, and kill it instantly if it burns — without a rollback race.

## Plain English

A **feature flag** (toggle) is a runtime switch: `if flags.new_checkout { ... } else { ... }`. Controlled via config service / LaunchDarkly-style platform / even a DB row — not by redeploying.

```text
  Deploy Monday (flag OFF) → code in prod but dark
  Tuesday: 5% users ON → watch error budget
  Problem: flip OFF in seconds (no rebuild)
  Healthy: ramp to 100%, then remove flag + old path
```

Flags are **technical debt** until removed. Long-lived flags create combinatorial testing hell.

## Essentials (must-know for this topic)

### Flag types

| Use | Meaning |
|-----|---------|
| **Release toggle** | Gradual rollout 1% → 10% → 100% |
| **Experiment** | A/B test variants |
| **Ops / kill switch** | Disable expensive or broken path under load |
| **Permission** | Beta / allowlisted users only |

### Deploy vs release

| Term | Meaning |
|------|---------|
| **Deploy** | Code lands in prod (may be dark) |
| **Release** | Flag turns the feature on for users |
| **Kill switch** | Instant OFF without rollback race |

### Lifecycle (must ship the cleanup)

| Stage | Action |
|-------|--------|
| 1 | Deploy with flag **off** |
| 2 | Ramp on error-budget / SLI signal |
| 3 | Kill immediately if burning |
| 4 | Reach 100%, then **delete flag + old path** |

### Defaults when flag service is down

| Flag kind | Typical default |
|-----------|-----------------|
| New risky payment path | **Fail closed** → old path |
| Optional recommendations | Fail open to degraded/cached |
| Kill switch for expensive feature | Prefer “off” (protect capacity) |

## Simple example

New recommendation model behind `recs_v2`:

1. Deploy with flag off for everyone.
2. Enable for internal employees.
3. Enable for 5% of region `us-east`.
4. Error rate rises → kill switch off.
5. Fix, re-roll, then delete `recs_v1` code path and the flag.

Pair with observability: tag metrics/traces with `flag=recs_v2` so you can compare cohorts.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Flags for risky changes | Safe progressive delivery | Complexity, flag debt |
| Many fine-grained flags | Control | Test matrix explosion |
| Central flag service | Consistency, UI, audit | Another dependency (cache defaults!) |
| Hardcode / env-only toggles | Simple | Slow to change; coarse |

## Pitfalls

- **Flags that never die** — years of `if (legacy)`.
- **Flag service down → wrong default** — decide fail-open vs fail-closed per flag (payments: fail closed to old path).
- **Changing flag semantics** without versioning — “on” means different things over time.
- **No ownership** — nobody knows who can flip prod flags.
- **Using flags instead of fixing broken design** — permanent dual code paths.

## Interview trigger phrase

> “I'd ship behind a **feature flag**, ramp on an **error-budget** signal, keep a **kill switch**, and **delete the flag** once the rollout is done so we don't accumulate toggle debt.”

## Exercise

You roll out a new payment provider to 10%. List three signals that would make you kill the flag, and what the **default** should be if the flag service is unreachable.
