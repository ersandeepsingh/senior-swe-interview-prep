# Coverage & Fuzzing — `-cover` & Native Fuzz Tests

> Measure what tests execute with **coverage**; explore input space with **fuzzing** (Go 1.18+) to find panics and logic bugs.

## Plain English

Coverage tells you which statements ran — not whether they were asserted well. Fuzzing feeds mutated inputs into a harness and keeps interesting corpus entries. Great for parsers, decoders, and anything that must not panic on garbage.

## Why interviewers ask

They want healthy skepticism about “100% coverage” and awareness that fuzzing is free in the toolchain now.

## Coverage

```bash
go test -cover ./...
go test -coverprofile=cover.out ./...
go tool cover -html=cover.out   # browser UI
go tool cover -func=cover.out   # per-function %
```

Aim coverage at critical packages (auth, billing, parsers), not vanity globals.

## Fuzz example

```go
func FuzzParseToken(f *testing.F) {
    // seed corpus
    f.Add("ABC-1234")
    f.Add("")
    f.Add("!!!")

    f.Fuzz(func(t *testing.T, s string) {
        tok, err := ParseToken(s)
        if err != nil {
            return // expected for many inputs
        }
        // invariants for successful parses
        if !ValidToken(tok.String()) {
            t.Fatalf("parsed invalid token %q", s)
        }
        // round-trip invariant
        out, err := ParseToken(tok.String())
        if err != nil || out != tok {
            t.Fatalf("round-trip failed: %v", err)
        }
    })
}
```

Run:

```bash
go test -fuzz=FuzzParseToken -fuzztime=30s ./...
go test -fuzz=FuzzParseToken -fuzztime=30s -race ./...
```

Failing inputs are written under `testdata/fuzz/...` — commit them; they become regression tests.

## Pitfalls

- Chasing 100% coverage with useless tests.
- Fuzz targets that ignore errors and only check “no panic” — weak; add **invariants**.
- Non-deterministic fuzz bodies (time.Now, map iteration affecting assertions).
- Mutating global state inside fuzz → flaky corpus.

## Interview trigger phrase

> “I’d use coverage to find untested critical paths, and fuzz parsers with round-trip invariants — committing failing corpus as regressions.”

## Exercise

Write a fuzz test for a function that decodes a length-prefixed binary message. State two invariants you’d assert on successful decode.
