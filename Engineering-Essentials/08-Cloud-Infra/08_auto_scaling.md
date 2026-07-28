# Auto-Scaling

> **Auto-scaling** adds/removes capacity from metrics. **Horizontal** (more instances) is the cloud default; **vertical** (bigger instance) has ceilings and downtime risk. Good scaling needs the **right signal** and cool-downs.

## Plain English

| Type | Meaning |
|------|---------|
| **Horizontal (scale out/in)** | More/fewer replicas |
| **Vertical (scale up/down)** | Bigger/smaller machine |
| **Reactive** | Scale on CPU, RPS, queue depth, custom metrics |
| **Scheduled / predictive** | Scale before known peaks |

```text
  metric (CPU, lag, p95 latency)
           │
           ▼
  ASG / HPA / Lambda concurrency
           │
     add replicas ← warm-up time matters
```

## Essentials (must-know for this topic)

### Horizontal vs vertical

| Type | Meaning | Cloud default? |
|------|---------|----------------|
| **Horizontal (out/in)** | More/fewer replicas | Yes — HA-friendly |
| **Vertical (up/down)** | Bigger/smaller machine | Ceiling + often disruptive |

### What to scale on

| Signal | Best when |
|--------|-----------|
| **CPU / memory** | CPU-bound request handlers |
| **RPS / concurrency** | Request-driven APIs |
| **Queue depth / consumer lag** | Async workers (CPU can lie) |
| **Custom SLI** (p95 latency) | User-pain-aligned |
| **Schedule** | Known peaks (Black Friday prep) |

### Knobs that belong in answers

| Knob | Why |
|------|-----|
| Min / max replicas | Floor for latency; ceiling vs bill/DB meltdown |
| Cool-down / hysteresis | Stop flapping |
| Warm-up time | Caches/JIT/LB registration delay |
| Scale the bottleneck | App scale won’t fix a saturated DB |

## Simple example

**K8s HPA:** target CPU 70%, min 3, max 30 pods.

**Better for workers:** scale on **SQS ApproximateNumberOfMessages** or Kafka consumer lag — CPU may be idle while backlog grows (I/O wait).

**Scale-in caution:** drain connections; don’t drop to zero if cold start / attach time is painful (or accept scale-to-zero consciously).

## When to use / trade-offs

| Prefer **horizontal** when… | Prefer **vertical** when… |
|-----------------------------|---------------------------|
| Stateless services | Single-threaded legacy; licensed per box |
| Need HA across nodes | Short-term boost before re-architecture |

| Prefer **queue-depth scaling** when… | Prefer **CPU scaling** when… |
|--------------------------------------|------------------------------|
| Async workers | CPU-bound request handlers |
| Backlog is the truth | Simple default, roughly correlates |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Aggressive scale-out | Headroom | Cost; thundering herd on deps (DB) |
| Slow cool-down | Stability | Paying for idle longer |
| Scale to zero | Cheap idle | Cold latency |

## Pitfalls

- Scaling app tier until **DB** melts — scale the bottleneck.  
- Metrics that lag reality; flapping without hysteresis.  
- Ignoring **warm-up** (caches, JIT, LB registration).  
- Max replicas unbounded → bill shock / connection storms.  
- Vertical only → still one AZ failure domain.

## Interview trigger phrase

> “I’d scale **horizontally** on a metric that tracks **user pain or backlog** — not vanity CPU alone — with min/max bounds so we don’t DDoS our database.”

## Exercise

**Checkout API + payment worker.**

1. Pick scaling metrics for each.  
2. Black Friday 10× spike — what else must scale or be protected?  
3. Scale-in causes 5xx during deploys — what did you forget?
