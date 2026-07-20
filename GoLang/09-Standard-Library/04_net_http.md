# `net/http` — Servers, Clients & Middleware

> Build HTTP servers with **`Handler` / `ServeMux`**, wrap middleware, and call APIs with **`http.Client`** (timeouts required).

## Plain English

`net/http` is the production default. A `Handler` is `ServeHTTP(ResponseWriter, *Request)`. Route with `ServeMux` (improved patterns in Go 1.22+). Clients must set timeouts — the zero `http.Client` can hang forever.

## Why interviewers ask ⭐

Almost every Go service is HTTP. They probe middleware, context cancellation, graceful shutdown, and “why didn’t you set a client timeout?”

## Minimal server

```go
package main

import (
    "encoding/json"
    "log"
    "net/http"
    "time"
)

func hello(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    _ = json.NewEncoder(w).Encode(map[string]string{"msg": "hello"})
}

func main() {
    mux := http.NewServeMux()
    // Go 1.22+ method-aware patterns:
    mux.HandleFunc("GET /hello", hello)
    mux.HandleFunc("GET /users/{id}", func(w http.ResponseWriter, r *http.Request) {
        id := r.PathValue("id")
        _, _ = w.Write([]byte(id))
    })

    srv := &http.Server{
        Addr:              ":8080",
        Handler:           logging(mux),
        ReadHeaderTimeout: 5 * time.Second,
    }
    log.Fatal(srv.ListenAndServe())
}

func logging(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %s", r.Method, r.URL.Path, time.Since(start))
    })
}
```

## Client with timeouts

```go
var client = &http.Client{
    Timeout: 10 * time.Second, // covers dial + TLS + headers + body
    Transport: &http.Transport{
        MaxIdleConns:        100,
        MaxIdleConnsPerHost: 10,
        IdleConnTimeout:     90 * time.Second,
    },
}

func fetch(ctx context.Context, url string) ([]byte, error) {
    req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
    if err != nil {
        return nil, err
    }
    res, err := client.Do(req)
    if err != nil {
        return nil, err
    }
    defer res.Body.Close()
    if res.StatusCode >= 300 {
        return nil, fmt.Errorf("status %d", res.StatusCode)
    }
    return io.ReadAll(io.LimitReader(res.Body, 1<<20))
}
```

## Middleware shape

```go
type Middleware func(http.Handler) http.Handler

func chain(h http.Handler, mws ...Middleware) http.Handler {
    for i := len(mws) - 1; i >= 0; i-- {
        h = mws[i](h)
    }
    return h
}
```

## Pitfalls

- Default `http.Client` / `http.Get` — **no timeout**.
- Forgetting `defer res.Body.Close()` → connection leak.
- Writing headers after writing the body (too late).
- Not propagating `r.Context()` to downstream calls / DB.
- Blocking the handler goroutine on slow work without timeouts (use context + worker pools carefully).

## Interview trigger phrase

> “I’d wrap a `ServeMux` with middleware, set server and client timeouts, pass `r.Context()` down, and shut down with `Server.Shutdown`.”

## Exercise

Sketch middleware that rejects requests missing `Authorization`, and a handler that fetches a URL using the request context. Where do you put the 10s client timeout vs the request deadline?
