# `go test` & `-race` — Running Tests Under the Race Detector

> Drive tests with `go test` flags; use **`-race`** to find data races (instrumented runtime + shadow memory).

## Plain English

`go test` compiles test binaries and runs them. Flags filter packages/tests, add verbosity, and enable the race detector. `-race` instruments memory accesses; concurrent unsynchronized read/write on the same location → FAIL with a stack dump.

## Why interviewers ask

Race bugs are the silent production killers. Saying “I’d run `-race` in CI” is table stakes for senior Go.

## Common flags

```bash
go test ./...                        # all packages
go test -v -run TestAdd$ ./calc      # verbose, regex filter
go test -count=1 ./...               # disable cache
go test -short ./...                 # skip long tests that check testing.Short()
go test -timeout 30s ./...
go test -race -count=1 ./...         # race detector
go test -race -parallel 4 ./...
go test -list . ./mypkg              # list tests
```

## Race example

```go
func TestRace(t *testing.T) {
    var x int
    var wg sync.WaitGroup
    wg.Add(2)
    go func() { defer wg.Done(); x = 1 }()
    go func() { defer wg.Done(); _ = x }()
    wg.Wait()
}
```

```bash
go test -race -run TestRace .
# WARNING: DATA RACE
```

Fix with mutex, channel, or atomic — depending on the design.

## CI advice

- Run `-race` on every PR for critical services (slower ~2–20×, more memory).
- Use `-count=1` when debugging flaky cached passes.
- Separate unit vs integration with build tags or `-short`.

## Pitfalls

- Assuming “no race report” means “no concurrency bugs” — deadlocks, logic races on higher-level invariants, and timing bugs still exist.
- Race detector doesn’t run on all architectures/OS combos equally (widely available on amd64/arm64).
- Sharing test fixtures across `t.Parallel()` without sync.
- Ignoring races as “test-only” — often real.

## Interview trigger phrase

> “I’d gate merges on `go test -race ./...`, filter with `-run`, and treat every race report as a production bug until proven otherwise.”

## Exercise

Explain how you’d find a race that only appears under load. Which flags, how many times (`-count`), and what you’d look for in the race stack?
