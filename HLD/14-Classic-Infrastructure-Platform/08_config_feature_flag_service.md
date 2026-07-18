# Design a Config / Feature-Flag Service 🟡

> **Crux:** **Ultra-fast reads** on every request path plus **reliable, quick propagation** of flag updates — push or short-poll, never a DB hit per check.

## Clarify (say this first)

**Functional**
- Boolean / multivariate flags; percentage rollouts
- Targeting: user, cohort, tenant, attrs
- Versioned changes; audit; kill switch
- SDK evaluate locally (preferred)

**Non-functional**
- Evaluate p99 ≪ 1 ms in-process
- Propagate updates in seconds (not minutes)
- High availability — flags must not take down apps
- Consistency: eventual OK; monotonic versions nicer

## Back-of-envelope

```text
10k flag definitions; 5k app instances
Evaluate: billions/day in-process (near zero network)
Update rate: tens–hundreds changes/hour (bursty launches)
Payload snapshot ~100 KB–2 MB compressed per env
Fan-out: 5k clients × push ≈ manageable with SSE/WebSocket or CDN poll
```

## API + data model

```text
PUT  /flags/{key}     {rules, rollout, version}
GET  /flags/snapshot?env=&since_version=
WS/SSE /stream?env=   → delta events
SDK:  bool evaluate(flag, userCtx)
```

| Entity | Fields |
|--------|--------|
| Flag | `key`, `type`, `rules[]`, `salt`, `version` |
| Rule | `attr`, `op`, `value`, `variation` |
| Audit | `actor`, `diff`, `ts` |

## High-level architecture

```text
  Admin UI ──► Flag Control Plane (API + store)
                      │
                      │ publish versioned snapshot / deltas
                      ▼
                 Pub/Sub or CDN
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       SDK cache   SDK cache   SDK cache   ← local evaluate
       (service A) (service B) (mobile)
```

## Deep dive: the crux

**Low-latency reads:** SDK holds full rule set in memory; **hash(user+salt)** for sticky bucketing; no network on evaluate.

**Propagation:**
| Mode | Latency | When |
|------|---------|------|
| **Push (SSE/WS/pubsub)** | Seconds | Default server fleets |
| **Short poll + ETag/CDN** | 5–30s | Simple; mobile-friendly |
| **Long poll** | Middle | Firewall-friendly |
| **Sync DB read per check** | Bad | Never on hot path |

**Pick:** versioned snapshots; push deltas to servers; poll fallback; **fail-safe defaults** if control plane unreachable (last-known-good). Percentage rollout with consistent hashing so users don’t flip-flop.

**Environments:** separate snapshots for dev/stage/prod; never let a staging SDK subscribe to prod stream. Audit every change with actor + diff for incident rollback.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| In-process SDK | Tiny evaluate latency | Stale until push |
| Push updates | Fast rollout / kill | Connection mgmt |
| Poll every 30s | Simple ops | Slower kill switch |
| Complex targeting | Fine-grained control | Bigger payloads; bugs |
| Strong central consistency | Same flags everywhere | Harder multi-region |

## Failure modes & scale

- **Control plane down:** serve last snapshot; alert; don’t block app start forever
- **Bad flag shipped:** instant kill switch + version pin; audit trail
- **Split brain versions:** include `version` in eval metrics; monotonic epochs
- **Huge targeting lists:** move large cohorts to segment service; keep SDK slim
- **Thundering poll:** jitter client polls; CDN-cache snapshots

## Interview trigger phrase

> “Flags are evaluated **in-process from a cached snapshot**; the control plane **pushes versioned updates** so we get millisecond reads and second-level propagation — with last-known-good if the plane is down.”

## Exercise

1. Kill switch must stop a bad feature in &lt;5s across 3k pods — push or poll? Sketch it.  
2. User should stay in the same 10% cohort all week — how do you bucket?  
3. Mobile app polls every 15 minutes — what’s an acceptable stale risk and how do you harden server flags differently?
