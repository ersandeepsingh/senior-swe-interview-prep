# `os` / `flag` — Env, Files & CLI Flags

> Talk to the OS: env vars, args, files, processes; parse CLI with **`flag`** (or a thin wrapper).

## Plain English

`os` is the bridge to the operating system: `Getenv`, `Args`, `Open`/`Create`, `Exit`, signals (via `os/signal`). `flag` is the stdlib CLI parser — simple, enough for many services’ `-addr`, `-config` knobs.

## Why interviewers ask

Twelve-factor config, CLI tools, and “how does your binary start?” — env vs flags vs files. Know when `flag` is enough vs when you’d use something richer (`cobra`, `ff`, etc.) without dogma.

## Examples

```go
package main

import (
    "flag"
    "fmt"
    "os"
)

func main() {
    addr := flag.String("addr", ":8080", "listen address")
    workers := flag.Int("workers", 4, "worker count")
    verbose := flag.Bool("v", false, "verbose")
    flag.Parse()

    // Env overrides are a common pattern
    if v := os.Getenv("ADDR"); v != "" {
        *addr = v
    }

    fmt.Printf("addr=%s workers=%d verbose=%v args=%v\n",
        *addr, *workers, *verbose, flag.Args())

    data, err := os.ReadFile("config.json")
    if err != nil {
        if os.IsNotExist(err) {
            fmt.Fprintln(os.Stderr, "config.json missing")
            os.Exit(1)
        }
        panic(err)
    }
    _ = data

    // Working directory / executable path
    wd, _ := os.Getwd()
    fmt.Println("wd:", wd)
}
```

## Files & permissions

```go
f, err := os.OpenFile("out.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o644)
if err != nil {
    return err
}
defer f.Close()
```

Prefer `os.ReadFile` / `os.WriteFile` for small blobs; streams for large files.

## Pitfalls

- Calling `flag.Parse()` twice or after reading `os.Args` manually inconsistently.
- Using `os.Exit` in library code — skips `defer` in the calling function… actually `os.Exit` skips **all** defers in the process. Prefer returning errors from `main`.
- Ignoring `IsNotExist` / permission errors — poor UX for CLIs.
- Hard-coding secrets in flags (visible in `ps`); prefer env or secret managers.
- Relative paths depending on launch cwd — document or resolve vs executable.

## Interview trigger phrase

> “I’d parse flags for operator knobs, allow env overrides, treat config files as data, and avoid `os.Exit` outside `main` so defers still run.”

## Exercise

Build a tiny CLI: `-config path` (default `./app.yaml`) and env `APP_CONFIG` wins if set. Print the resolved path and exit `2` if the file is missing.
