# Functional Options Pattern

> Configure constructors with variadic **`Options`** funcs: readable call sites, backward-compatible defaults, optional knobs without telescoping params.

## Plain English

Instead of `New(a, b, c, d, e)` with many defaults, do `New(required, WithTimeout(t), WithLogger(l))`. Each `With*` returns a function that mutates an options struct. Dave Cheney / Rob Pike style — very common in Go libraries.

## Why interviewers ask 🔴⭐

It’s a signature senior API-design question. Know when it’s appropriate vs a plain config struct.

## Example

```go
package server

type Option func(*config)

type config struct {
    addr    string
    timeout time.Duration
    log     *slog.Logger
}

func WithAddr(addr string) Option {
    return func(c *config) { c.addr = addr }
}

func WithTimeout(d time.Duration) Option {
    return func(c *config) { c.timeout = d }
}

func WithLogger(l *slog.Logger) Option {
    return func(c *config) { c.log = l }
}

type Server struct {
    cfg config
}

func New(opts ...Option) *Server {
    cfg := config{
        addr:    ":8080",
        timeout: 10 * time.Second,
        log:     slog.Default(),
    }
    for _, opt := range opts {
        if opt != nil {
            opt(&cfg)
        }
    }
    return &Server{cfg: cfg}
}

// usage
// s := server.New(server.WithAddr(":9090"), server.WithTimeout(time.Second))
```

## When to use / not use

**Use:** multiple optional knobs; library APIs that must grow without breaking callers; clean call sites.

**Don’t use:** 1–2 simple params — a config struct or direct args are clearer; options that are actually required (make them parameters).

## Pitfalls

- Applying options after the object is “live” without sync — keep them constructor-only unless documented.
- Silent ignore of invalid combos — validate at end of `New` and return `(*T, error)` when needed.
- Nil option funcs in the slice — guard or document.
- Overusing for every type in an app — noise.

## Interview trigger phrase

> “I’d expose `New(required, opts ...Option)` with `With*` helpers so defaults stay stable and callers only set what they need.”

## Exercise

Design `NewClient(baseURL string, opts ...Option)` with `WithHTTPClient`, `WithRetries`, `WithUserAgent`. Return an error if `baseURL` is empty or retries < 0.
