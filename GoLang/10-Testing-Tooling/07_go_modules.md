# Go Modules — `go.mod`, `go.sum` & Semantic Import Versioning

> Modules are Go’s dependency system: **`go.mod`** declares the module path & requirements; **`go.sum`** pins cryptographic checksums.

## Plain English

A module is a versioned unit of code identified by a path (`github.com/acme/pkg`). Semantic import versioning: major v2+ must end the module path with `/v2` (etc.). `go.sum` ensures everyone builds the same bits (supply-chain integrity with the checksum DB).

## Why interviewers ask ⭐

Dependency hell, breaking majors, replace directives, and private modules show up in real teams. Seniors can read a `go.mod` and explain it.

## Anatomy

```go
// go.mod
module github.com/acme/payments

go 1.22

require (
    github.com/google/uuid v1.6.0
    github.com/acme/billing/v2 v2.3.1
)

require (
    // indirect deps listed after tidy
    golang.org/x/sys v0.20.0 // indirect
)

replace github.com/acme/billing/v2 => ../billing // local fork; avoid in released tags
```

```bash
go mod init github.com/acme/payments
go get github.com/google/uuid@v1.6.0
go get github.com/acme/billing/v2@v2.3.1
go mod tidy          # add missing, remove unused; update go.sum
go mod vendor        # optional vendor/ copy
go mod why -m github.com/google/uuid
```

## Version selection (MVS)

Go uses **Minimal Version Selection**: pick the maximum of the minimums required by the build list — deterministic, boring (on purpose). No SAT solver drama like some other ecosystems.

## Private modules

```bash
# don't probe public proxy for private paths
go env -w GOPRIVATE=github.com/acme/*
# CI: GIT auth / netrc / GOPROXY=direct for those paths
```

## Pitfalls

- Forgetting `/v2` in the module path for major version 2+ → confusing import errors.
- Committing `replace` to a local path.
- Hand-editing `go.sum` — never; let `go` maintain it.
- Mixing `GOPATH` mode myths with modules (modules are default).
- Leaving unused requires — `go mod tidy` before merge.

## Interview trigger phrase

> “I’d declare deps in `go.mod`, trust MVS + `go.sum`, use `/vN` for majors, and keep `GOPRIVATE` set for internal modules.”

## Exercise

Your library is `github.com/acme/lib` at v1. You need a breaking API change. Walk through module path, tag, and how importers change their import lines.
