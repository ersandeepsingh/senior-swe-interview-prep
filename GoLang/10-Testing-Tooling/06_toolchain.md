# Toolchain — `build`, `vet`, `fmt`, Modules & Linters

> The Go toolchain is the product: format with **`gofmt`**, sanity-check with **`go vet`**, build/test with **`go`**, lint with **`staticcheck`**.

## Plain English

Idiomatic Go style is machine-enforced. `gofmt`/`goimports` end style debates. `go vet` catches suspicious constructs. `staticcheck` goes further (unused code, bug patterns). Modules (`go.mod`) pin dependencies.

## Why interviewers ask

They expect you to live in this toolchain daily — not invent bespoke make magic for basics.

## Everyday commands

```bash
gofmt -w .
goimports -w .          # fmt + fix imports (needs golang.org/x/tools)

go vet ./...
staticcheck ./...

go build -o bin/app ./cmd/app
go install ./cmd/app    # to $GOBIN / $GOPATH/bin

go mod tidy
go mod download
go mod verify
```

## What `vet` catches (examples)

- Printf verb/arg mismatches
- Unreachable code
- Suspicious lock copy
- `cancel` function not called from context

## staticcheck

Industry-default advanced linter. Wire it in CI:

```bash
staticcheck ./...
```

Common findings: unused params, impossible type asserts, deprecated APIs, simple refactor opportunities (`S1000` style checks can be tuned).

## Pitfalls

- Committing without `gofmt` → noisy diffs.
- Ignoring `vet` in CI because “it’s annoying.”
- Vendoring vs proxy confusion (`GOPROXY`, `GOSUMDB`).
- Using `go get` randomly without understanding module versioning (see modules guide).

## Interview trigger phrase

> “I’d keep `gofmt`/`vet`/`staticcheck` in CI, `go mod tidy` clean, and treat toolchain warnings as defects.”

## Exercise

List the CI steps (in order) you’d run for a Go service PR, and why `-race` might be a separate nightly job.
