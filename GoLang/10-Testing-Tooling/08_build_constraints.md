# Build Constraints & Tags — Platform-Specific Code

> Conditionally compile files with **`//go:build`** lines (and legacy `// +build`) so OS/arch/features don’t pollute every binary.

## Plain English

Some code only works on Linux, or only in integration tests, or only when cgo is enabled. Build constraints exclude files from the build unless the tags match. Prefer the modern `//go:build` syntax (Go 1.17+).

## Why interviewers ask 🔴

Cross-compilation, syscall wrappers, and “how do you stub this on Windows?” — tags are the idiomatic answer.

## Syntax

```go
//go:build linux && amd64

package sys
```

```go
//go:build integration

package api_test
```

Legacy (still understood):

```go
// +build linux,amd64
```

## Common patterns

```text
foo_linux.go      // implied OS tag via filename
foo_windows.go
foo_amd64.s       // arch via filename
foo.go            // default / shared
foo_stub.go       //go:build !linux
```

Filename suffixes `_GOOS`, `_GOARCH`, `_GOOS_GOARCH` add implicit constraints.

## Integration tests

```bash
# file: server_integration_test.go
# //go:build integration

go test -tags=integration ./...
```

Keep slow tests out of the default `go test` path.

## Example: OS-specific open

```go
// file_posix.go
//go:build unix

package store

import "golang.org/x/sys/unix"

func syncDir(dir *os.File) error {
    return dir.Sync()
}
```

```go
// file_windows.go
//go:build windows

package store

func syncDir(dir *os.File) error {
    return dir.Sync() // or Windows-specific handling
}
```

## Pitfalls

- Forgetting both sides of a constraint (`linux` file + no `!linux` stub) → build fails on other OS.
- Using tags for feature flags that should be runtime config — prefer config when possible.
- Mixing old and new constraint syntax incorrectly (both must agree if both present).
- Underscore filename typos (`_linux` vs `_Linux`).

## Interview trigger phrase

> “I’d isolate OS-specific files with `//go:build` and filename GOOS suffixes, and gate integration tests behind a build tag.”

## Exercise

You have a package that uses `unix.EpollCreate1` on Linux and a kqueue stub on Darwin. Sketch the file names and build lines so `go test` works on both.
