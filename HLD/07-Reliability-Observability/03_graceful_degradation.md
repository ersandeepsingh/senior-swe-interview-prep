# Graceful Degradation

> When you can’t serve the **full** experience, serve a **useful subset** instead of a blank error. Degradation is a **product decision** wired to reliability switches — not an afterthought.

## Plain English

Full path fails → shed optional work, use cache, simplify ranking, disable non-critical features. Core user journey (view content, pay, message) stays alive.

Think in **tiers of fidelity**:

| Tier | Example |
|------|---------|
| Full | Personalized ranked feed + ads + stories |
| Degraded | Chronological feed from cache, ads off |
| Critical | Static “service issue” only if auth/cache die |

```text
  Healthy:     Request → Auth → Ranker → Ads → Personalized feed
  Degraded:    Request → Auth → Cache / chrono feed → (skip Ads)
                      └─────────── Ranker OPEN ──┘
  Critical:    Request → Auth → “Something’s wrong, try later”
               (only if even cache/auth path dies)
```

## Simple example

Netflix-style: recommendation service down → show **trending / continue watching** from cache. Checkout: promo engine down → allow buy **without discount** rather than block payment. Maps: traffic layer down → still show base map.

```text
  Checkout path:
    cart + tax + inventory + payment   ← must work
    promo / recommendations / upsell   ← degradable
```

Feature flags / kill switches flip degradation from ops or from automated SLO burn (error budget).

## Why prefer one over the other

| Prefer **degrade** when… | Prefer **fail hard** when… |
|--------------------------|----------------------------|
| Partial value > error page | Wrong answer is dangerous (authz, money amount) |
| Optional personalization / ads | Consistency-critical commit |
| You have a warm cache / default | No safe fallback exists |

**Design for degradation early:** define the **minimum lovable path** per feature in the HLD, not after the outage postmortem. Pair with circuit breakers that **trigger** the degraded path.

**Capacity shedding:** under overload, drop low-priority work first (same family as degradation).

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Cached / simpler UX | Availability, lower blast radius | Stale or less relevant results |
| Kill optional features | Protect core capacity | Revenue / engagement dip |
| Always full fidelity | Best UX when healthy | Cascades when deps die |
| Many kill switches | Operability | Config complexity / testing matrix |

**Trap:** Only drawing the happy path. Interviewers listen for “if Ranker is down we still…”

**Wire it to observability:** degraded mode should emit a metric (`feed_mode=degraded`) so you don’t silently normalize bad UX. Pair with error-budget / burn alerts that flip kill switches automatically when safe.

**Cache as degradation fuel:** a warm CDN/edge or Redis snapshot of “last good feed” is often the difference between soft landing and hard outage.

## Interview trigger phrase

> “I’d define a **degraded mode** up front — chronological feed from cache if ranking fails — so we burn optional fidelity before we burn availability.”

## Exercise

**Design Instagram-like home under Ranker + CDN + Origin outages.**

1. What do you still show if Ranker is down but cache is warm?
2. When would you refuse to degrade (show error instead)?
3. One sentence tying degradation to an SLO (e.g. availability vs freshness).
