# Config & Env Management — Twelve-Factor Style

> Configure via **environment** (and flags/files as needed); keep secrets out of images; validate at startup; fail fast on bad config.

## Plain English

Twelve-factor: config in the environment, not baked into code. In Go: read env/flags once at boot into a typed `Config`, validate, pass to constructors. Optional: YAML/JSON file for complex structures, still overridden by env in prod.

## Why interviewers ask

Ops reality — same artifact, many environments. Seniors validate and document knobs.

## Example

```go
type Config struct {
    Addr        string
    DatabaseURL string
    LogLevel    string
    Workers     int
}

func Load() (Config, error) {
    cfg := Config{
        Addr:     env("ADDR", ":8080"),
        LogLevel: env("LOG_LEVEL", "info"),
        Workers:  4,
    }
    cfg.DatabaseURL = os.Getenv("DATABASE_URL")
    if cfg.DatabaseURL == "" {
        return Config{}, errors.New("DATABASE_URL required")
    }
    if v := os.Getenv("WORKERS"); v != "" {
        n, err := strconv.Atoi(v)
        if err != nil || n < 1 {
            return Config{}, fmt.Errorf("invalid WORKERS: %q", v)
        }
        cfg.Workers = n
    }
    return cfg, nil
}

func env(k, def string) string {
    if v := os.Getenv(k); v != "" {
        return v
    }
    return def
}
```

## Layering (common)

```text
defaults → config file → flags → env (highest)
```

Document precedence. Libraries: `caarlos0/env`, `spf13/viper` (heavier) — or stdlib only for small services.

## Secrets

- Inject via env / mounted files / secret manager — not git.
- Don’t log config structs that contain passwords/tokens.
- Prefer short-lived credentials where possible.

## Pitfalls

- Silent defaults for required prod settings (e.g. empty Redis URL → “works” on laptop, pages in prod).
- Scattering `os.Getenv` deep in business code — hard to test; load once.
- Mutating global config at runtime without clear rules.
- Boolean env parsing (`"0"`, `"false"`, `"no"`) done inconsistently.

## Interview trigger phrase

> “I’d load a typed Config at startup from env with clear defaults, validate required fields, inject it into constructors, and never log secrets.”

## Exercise

Design `Config` for an API with DB URL, HTTP addr, TLS cert paths, and feature flag `ENABLE_BETA`. Show validation rules and a test that fails when DB URL is missing.
