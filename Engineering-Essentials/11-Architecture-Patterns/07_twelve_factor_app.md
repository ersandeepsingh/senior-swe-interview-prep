# 12-Factor App

> A practical checklist for building **SaaS-friendly** apps: config outside code, disposable processes, logs as streams — so they run cleanly on modern platforms (Heroku-era ideas that still apply to containers/K8s).

## Plain English

Twelve-factor is a portability checklist for cloud/SaaS apps. Know the factors by name and *why* each exists — especially config, stateless processes, and disposability on Kubernetes.

```text
  Anti-12-factor:  secrets in Git, local disk sessions, SSH to prod to “fix”,
                   different MySQL in prod vs SQLite in dev with different SQL
```

## Essentials (must-know for this topic)

### The twelve (interview table)

| # | Factor | One-liner |
|---|--------|-----------|
| 1 | **Codebase** | One app ↔ one repo (or clear deployable); many deploys |
| 2 | **Dependencies** | Explicit declare/isolate (lockfiles, no implicit system pkgs) |
| 3 | **Config** | Env vars / secret store — **not** baked into image for secrets |
| 4 | **Backing services** | DB, queue, cache as attached resources (swap via URL) |
| 5 | **Build, release, run** | Strict stages; same artifact, different config per env |
| 6 | **Processes** | Stateless processes; sticky sessions are a smell |
| 7 | **Port binding** | App exports HTTP itself (self-contained) |
| 8 | **Concurrency** | Scale out via process model / replicas |
| 9 | **Disposability** | Fast start, graceful shutdown (`SIGTERM`) |
| 10 | **Dev/prod parity** | Keep environments close; same backing service types |
| 11 | **Logs** | Write to stdout/stderr; platform aggregates |
| 12 | **Admin processes** | One-off tasks as same codebase/release (`migrate`) |

### Highest-yield in interviews

| Factor | Common fail |
|--------|-------------|
| Config | Secrets in Git / `if env == prod` scattered |
| Processes | Sessions on local disk → broken on new pod |
| Disposability | Ignore `SIGTERM` → killed mid-write |
| Logs | Writing only to local files inside the container |
| Backing services | Hard-coded hostnames; can't swap Redis/DB |

## Simple example

Good: image `app:1.4.2` runs in staging and prod; only `DATABASE_URL`, `REDIS_URL`, `LOG_LEVEL` differ. On deploy, K8s sends `SIGTERM` → app stops taking work, drains in-flight requests, exits 0.

Bad: sessions on local disk → new pod doesn't know the user; need Redis session store (backing service).

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Env-based config | Portable deploys | Many knobs to document/validate |
| Stateless apps | Easy horizontal scale | Externalize all state (Redis/DB) |
| Strict build/release/run | Reproducible | Slightly heavier pipeline |
| Dev/prod parity | Fewer “works on my machine” | Heavier local/dev infra |

## Pitfalls

- **Config in code** (`if env == prod`) scattered everywhere.
- **Long shutdown** ignoring SIGTERM → killed mid-write.
- **Mutable servers** (“snowflakes”) instead of immutable releases.
- **Treating 12-factor as religion** — some desktop/batch apps differ; know *why* each factor exists.

## Interview trigger phrase

> “I'd keep the app **stateless**, push **config and secrets out of the image**, log to **stdout**, and honor **graceful shutdown** so we can scale and deploy safely on Kubernetes.”

## Exercise

Your web app stores uploaded files on the container filesystem and user sessions in memory. Name the two 12-factor fixes and the backing services you'd attach.
