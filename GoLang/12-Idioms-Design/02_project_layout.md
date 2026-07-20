# Project Layout & Package Design

> Organize by **responsibility**, keep packages cohesive, avoid import cycles; `internal/` for non-public code.

## Plain English

There is no single mandatory layout, but common patterns exist (`cmd/`, `internal/`, domain packages). Packages should mean something (a noun: `billing`, `auth`) — not layers alone (`models`, `utils` dumping grounds). Import cycles are compile errors — design ownership to prevent them.

## Why interviewers ask

“How would you structure this service?” — they want clear boundaries, not a 40-package explosion.

## Common layout

```text
module/
  cmd/
    paymentsd/          # main: wiring only
      main.go
  internal/
    httpapi/            # private HTTP adapters
    store/              # private persistence
  billing/              # importable domain package (if library)
  go.mod
```

- **`cmd/`** — binaries; thin `main` that wires deps.
- **`internal/`** — compiler-enforced private to this module.
- **Domain packages** — at module root or under `internal` depending on reuse.

## Package design rules of thumb

1. Name packages for what they provide (`http`, `sql`, `auth`).
2. Avoid `util`/`common` magnets — split by concept.
3. Keep `main` dumb: flags/env → constructors → `Run(ctx)`.
4. Put interfaces near consumers when small.
5. Break cycles by extracting a third package or inverting dependency (interface).

## Cycle example & fix

```text
Bad:  order → user → order
Fix:  order → user
      order → userapi.User (interface defined where needed)
      or extract accountid types into a small `account` package both import
```

## Pitfalls

- Treating [golang-standards/project-layout](https://github.com/golang-standards/project-layout) as official gospel — it’s popular, not std.
- `pkg/` directory cargo-cult when everything could be `internal/`.
- Circular imports “solved” by dumping types into `models`.
- Fat `main` with business logic.

## Interview trigger phrase

> “I’d keep `cmd` as wiring, put private code under `internal`, name packages by domain, and break cycles with small interfaces or extracted shared types.”

## Exercise

Sketch packages for an HTTP billing API with Postgres and a Stripe client. Where do interfaces live, and what stays in `internal`?
