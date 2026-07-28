# Graceful Degradation

> When you can't serve the **full** experience, serve a **useful subset** instead of a blank error. Degradation is a product decision wired to reliability switches.

## Plain English

Full path fails → shed optional work, use cache, simplify ranking, disable non-critical features. Core journeys (view, pay, message) stay alive.

```text
  Healthy:   Request → Auth → Ranker → Ads → Personalized feed
  Degraded:  Request → Auth → Cache / chrono feed → (skip Ads)
  Critical:  Request → Auth → “try later” (only if even cache dies)
```

Wire to **feature flags / kill switches** and to circuit breakers that flip the degraded path automatically.

## Essentials (must-know for this topic)

### Fidelity tiers

| Tier | Example |
|------|---------|
| **Full** | Personalized ranked feed + ads + stories |
| **Degraded** | Chronological feed from cache, ads off |
| **Critical** | Static “service issue” only if auth/cache die |

### Must-work vs degradable

| Must work (protect) | Degradable (shed first) |
|---------------------|-------------------------|
| Auth / session | Recommendations / personalization |
| Cart + tax + inventory + payment | Ads, upsell, promo engine |
| Core read/write of primary product | Fancy ranking, A/B experiments |

### How you flip modes

| Mechanism | Role |
|-----------|------|
| **Circuit breaker open** | Auto-flip to fallback path |
| **Feature flag / kill switch** | Manual or progressive shed under load |
| **Cached / static fallback** | Warm data so degraded mode isn't empty |
| **Metric `mode=degraded`** | Ops sees soft failures, not silent UX rot |

**Interview line:** burn optional fidelity before you burn availability.

## Simple example

- Recommendations down → show **trending / continue watching** from cache.
- Promo engine down → allow checkout **without discount** (don't block payment).
- Maps traffic layer down → still show base map.

```text
  Must work:   cart + tax + inventory + payment
  Degradable:  promo / recommendations / upsell / personalization
```

Emit a metric like `feed_mode=degraded` so ops sees soft failures, not silent UX rot.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Cached / simpler UX | Availability | Stale or less relevant results |
| Kill optional features | Protect core capacity | Revenue / engagement dip |
| Always full fidelity | Best UX when healthy | Cascades when deps die |
| Many kill switches | Operability | Config + test matrix complexity |

## Pitfalls

- **Only designing the happy path** — interviewers listen for “if Ranker is down we still…”
- **Degrading money/auth incorrectly** — wrong balance or wrong permissions is worse than an error.
- **Silent degradation** — no metric/alert → you normalize a bad experience.
- **No warm cache** — degraded mode with nothing to fall back to is still an outage.

## Interview trigger phrase

> “I'd define a **degraded mode** up front — e.g. chronological feed from cache if ranking fails — so we burn optional fidelity before we burn availability.”

## Exercise

Design Instagram-like home under Ranker + CDN + Origin stress.

1. What do you still show if Ranker is down but cache is warm?
2. When would you refuse to degrade (show error instead)?
3. One sentence tying degradation to an SLO (availability vs freshness).
