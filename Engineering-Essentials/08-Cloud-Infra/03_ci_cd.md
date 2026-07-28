# CI / CD

> **CI** (continuous integration) automatically builds and tests every change. **CD** (continuous delivery/deployment) automatically ships validated artifacts to environments. The goal: small, frequent, reversible releases.

## Plain English

| Stage | Typical work |
|-------|----------------|
| **CI** | lint → unit/integration tests → build image/artifact → security scan |
| **CD** | deploy to staging → smoke tests → prod with strategy |

**Release strategies:**

| Strategy | Idea |
|----------|------|
| **Rolling** | Replace instances gradually |
| **Blue-green** | Two environments; flip traffic when green is healthy |
| **Canary** | Send a small % of traffic to new version, then ramp |

```text
  PR → CI pipeline → artifact (image:sha)
         │
         ▼
  CD → staging → canary 5% → 25% → 100% → done
                    │ fail
                    └── rollback / abort
```

## Essentials (must-know for this topic)

### CI vs CD

| Term | Meaning |
|------|---------|
| **CI** | On every change: lint, test, build, scan → produce artifact |
| **CD (delivery)** | Artifact is always deployable; promote with gates |
| **CD (deployment)** | Auto-ship to prod when gates pass |
| **Immutable artifact** | Built once, tagged by git SHA — same bits staging→prod |

### Release strategies

| Strategy | Idea | Rollback |
|----------|------|----------|
| **Rolling** | Replace instances gradually | Redeploy previous |
| **Blue-green** | Two full stacks; flip traffic | Flip back |
| **Canary** | Small % traffic to new version, ramp | Abort ramp |

### Pipeline stages (typical order)

| Stage | Work |
|-------|------|
| Verify | Unit / integration / lint |
| Secure | Dependency + image scan |
| Build | Image/binary `:gitsha` |
| Deploy | Staging → smoke → prod strategy |
| Observe | Metrics gate promote/rollback |

## Simple example

**GitHub Actions / GitLab CI sketch:**

```text
  on push to main:
    test
    docker build & push :$GIT_SHA
    deploy staging (k8s set image)
    integration tests
    manual or auto promote to prod canary
```

Artifact is **immutable** and identified by git SHA — never “build differently in prod.”

## When to use / trade-offs

| Prefer **canary** when… | Prefer **blue-green** when… |
|-------------------------|-----------------------------|
| Need real traffic signal | Want instant cutover / easy switch back |
| Enough traffic to be statistically meaningful | Stateful cutovers, simpler dual stack |

| Prefer **auto-deploy** when… | Prefer **manual approve** when… |
|------------------------------|----------------------------------|
| Strong tests + observability | Regulated / high-risk changes |
| Small services | Schema migrations needing care |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Fast CD | Feedback, smaller diffs | Requires discipline + feature flags |
| Many manual gates | Perceived control | Queues, large batch releases |
| Canary | Lower blast radius | Needs metrics + automation |

## Pitfalls

- Deploying **untested** “works on my machine” builds.  
- Config drift between staging and prod.  
- Canary without **metrics/alerts** → theater.  
- Migrations that aren’t backward compatible with rolling old+new.  
- Secrets in CI logs; overly privileged deploy credentials.

## Interview trigger phrase

> “I’d ship **immutable SHA-tagged artifacts** through CI, deploy with **canary or blue-green**, and require **metrics-based promote/rollback** — not hope.”

## Exercise

**API + DB column rename.**

1. Why can a naive CD rolling deploy break?  
2. Outline a 2–3 release expand/contract migration plan.  
3. Pick canary vs blue-green for a mobile BFF and defend in two sentences.
