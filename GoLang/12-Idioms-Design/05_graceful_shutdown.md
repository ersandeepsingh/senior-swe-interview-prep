# Graceful Shutdown — Signals, Context & `Server.Shutdown`

> On SIGTERM/SIGINT: **cancel context**, stop accepting work, drain in-flight requests, then exit — don’t hard-kill mid-write.

## Plain English

Orchestrators send SIGTERM before kill. A well-behaved service catches the signal, stops listeners, lets handlers finish (with a deadline), closes DBs, and exits 0. `context.Context` propagates cancellation to workers.

## Why interviewers ask 🔴⭐

K8s / systemd reality. Also pairs with worker pools and channel shutdown questions.

## Example (HTTP)

```go
func main() {
    ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
    defer stop()

    mux := http.NewServeMux()
    mux.HandleFunc("GET /healthz", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
    })

    srv := &http.Server{Addr: ":8080", Handler: mux}

    go func() {
        if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
            log.Fatal(err)
        }
    }()

    <-ctx.Done()
    log.Println("shutting down")

    shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()
    if err := srv.Shutdown(shutdownCtx); err != nil {
        log.Printf("shutdown: %v", err)
    }
}
```

## Worker pool drain

```go
ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGTERM, os.Interrupt)
defer stop()

jobs := make(chan Job)
var wg sync.WaitGroup
for i := 0; i < workers; i++ {
    wg.Add(1)
    go func() {
        defer wg.Done()
        for {
            select {
            case <-ctx.Done():
                return
            case j, ok := <-jobs:
                if !ok {
                    return
                }
                process(j)
            }
        }
    }()
}

// producer exits on ctx; then:
close(jobs)
wg.Wait()
```

Order matters: stop producers → close jobs → wait workers → close DB.

## Pitfalls

- Calling `os.Exit` immediately on signal — skips defers / flush.
- `Shutdown` with no timeout — can hang forever on a stuck handler.
- Not propagating ctx to DB/HTTP outbound calls — in-flight work ignores cancel.
- Closing channels from multiple goroutines / closing twice.
- Readiness vs liveness: fail readiness during drain so traffic stops, keep liveness until exit.

## Interview trigger phrase

> “I’d use `signal.NotifyContext`, `Server.Shutdown` with a deadline, cancel workers via context, then wait on a WaitGroup before closing dependencies.”

## Exercise

Add graceful shutdown to a service with HTTP + 4 background consumers reading from a channel. Specify the exact shutdown sequence and timeouts you’d choose.
