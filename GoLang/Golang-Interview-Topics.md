# Go (Golang) Interview Topic Map — Basic → Advanced

Organized by **category → topic → 1-line "what to know."**
Ordered roughly basic → advanced. The ⭐ marks topics interviewers probe hardest (especially for senior roles) — concurrency, interfaces, memory, and the classic gotchas.

Legend: 🟢 basic · 🟡 intermediate · 🔴 advanced/senior-signal · ⭐ high-frequency

Deep-dives (plain English + Go examples + exercise) live in numbered folders next to this map:

| # | Section | Folder |
|---|---------|--------|
| 1 | Language Fundamentals | [01-Language-Fundamentals/](01-Language-Fundamentals/README.md) |
| 2 | Composite Types | [02-Composite-Types/](02-Composite-Types/README.md) |
| 3 | Functions & Closures | [03-Functions-Closures/](03-Functions-Closures/README.md) |
| 4 | Methods & Interfaces | [04-Methods-Interfaces/](04-Methods-Interfaces/README.md) |
| 5 | Pointers & Memory | [05-Pointers-Memory/](05-Pointers-Memory/README.md) |
| 6 | Concurrency | [06-Concurrency/](06-Concurrency/README.md) |
| 7 | Error Handling | [07-Error-Handling/](07-Error-Handling/README.md) |
| 8 | Generics | [08-Generics/](08-Generics/README.md) |
| 9 | Standard Library | [09-Standard-Library/](09-Standard-Library/README.md) |
| 10 | Testing & Tooling | [10-Testing-Tooling/](10-Testing-Tooling/README.md) |
| 11 | Runtime & Performance | [11-Runtime-Performance/](11-Runtime-Performance/README.md) |
| 12 | Idioms & Design | [12-Idioms-Design/](12-Idioms-Design/README.md) |
| 13 | Classic Gotchas | [13-Classic-Gotchas/](13-Classic-Gotchas/README.md) |

---

## 1. Language Fundamentals

Deep-dives: [01-Language-Fundamentals/](01-Language-Fundamentals/README.md)

- **Program structure** — `package`, `import`, `func main`, exported vs unexported (capitalization). 🟢
- **Variables & declaration** — `var`, `:=`, zero values, `const`, `iota` for enums. 🟢
- **Basic types** — int/int64, float, bool, byte, rune, string; type sizes & platform ints. 🟢
- **Type conversion vs casting** — explicit conversions only; no implicit numeric promotion. 🟢⭐
- **Operators & control flow** — `if`, `for` (Go's only loop), `switch` (no fallthrough default), labeled break/continue. 🟢
- **`switch` power features** — type switch, expression-less switch, `case` lists. 🟡
- **`defer`** — LIFO execution, argument evaluation at defer time, common cleanup use. 🟡⭐
- **`iota` patterns** — bit-flag enums, skipping values, expressions. 🟡

## 2. Composite Types & Data Structures

Deep-dives: [02-Composite-Types/](02-Composite-Types/README.md)

- **Arrays vs slices** — fixed vs dynamic; arrays are values, slices are references. 🟢⭐
- **Slice internals** — pointer + length + capacity; how `append` grows & reallocates. 🔴⭐
- **Slice gotchas** — shared backing array, aliasing after slicing, `append` mutating originals. 🔴⭐
- **`make` vs `new`** — `make` for slice/map/chan, `new` returns pointer to zeroed value. 🟡⭐
- **Maps** — creation, comma-ok lookup, deletion, iteration order is random. 🟢⭐
- **Map gotchas** — not concurrency-safe, can't take address of map element, nil map writes panic. 🔴⭐
- **Strings, bytes, runes** — immutability, UTF-8, `[]byte` vs `[]rune`, iterating with range. 🟡⭐
- **`strings` / `bytes` / `strconv` / `unicode`** — common manipulation utilities. 🟢
- **Structs** — fields, tags, anonymous/embedded fields, comparability. 🟢
- **Struct embedding** — composition, promoted fields/methods, ambiguity resolution. 🟡⭐

## 3. Functions & Closures

Deep-dives: [03-Functions-Closures/](03-Functions-Closures/README.md)

- **Function values & first-class functions** — pass/return functions. 🟢
- **Multiple return values** — idiomatic `(result, error)`. 🟢⭐
- **Named return values** — naked returns and their pitfalls. 🟡
- **Variadic functions** — `...T`, spreading a slice. 🟢
- **Closures** — capturing variables by reference; loop-variable capture bug. 🔴⭐
- **`defer`/`recover` in functions** — recovering from panics cleanly. 🟡

## 4. Methods & Interfaces ⭐

Deep-dives: [04-Methods-Interfaces/](04-Methods-Interfaces/README.md)

- **Method declaration** — receivers on any named type. 🟢
- **Value vs pointer receivers** — when to use which, method set implications. 🔴⭐
- **Interfaces** — implicit satisfaction (structural typing), no `implements`. 🟢⭐
- **Interface internals** — `(type, value)` pair; how dynamic dispatch works. 🔴⭐
- **Empty interface / `any`** — holding any value; when to avoid it. 🟡
- **Type assertions & type switches** — safe extraction with comma-ok. 🟡⭐
- **nil interface vs nil pointer** — the classic "why isn't my err nil?" trap. 🔴⭐
- **Interface composition** — embedding interfaces (e.g. `io.ReadWriter`). 🟡
- **Common std interfaces** — `error`, `Stringer`, `io.Reader`/`Writer`, `sort.Interface`. 🟡⭐
- **Accept interfaces, return structs** — idiomatic API design. 🔴

## 5. Pointers & Memory Model

Deep-dives: [05-Pointers-Memory/](05-Pointers-Memory/README.md)

- **Pointers** — `&`, `*`, no pointer arithmetic. 🟢⭐
- **Stack vs heap** — where values live; escape analysis basics. 🔴⭐
- **Escape analysis** — why a variable escapes to the heap. 🔴
- **Pass by value** — everything is copied (slices/maps/chans copy the header). 🟡⭐
- **Zero values & nil** — nil slice vs empty slice, nil map, nil channel behavior. 🟡⭐
- **`unsafe.Pointer` & `uintptr`** — low-level access, when it's justified. 🔴

## 6. Concurrency ⭐ (the make-or-break area)

Deep-dives: [06-Concurrency/](06-Concurrency/README.md)

- **Goroutines** — lightweight threads, `go` keyword, scheduling model. 🟢⭐
- **Goroutine lifecycle & leaks** — how goroutines leak and how to prevent it. 🔴⭐
- **Channels** — unbuffered vs buffered, send/receive, direction types. 🟢⭐
- **Channel semantics** — blocking rules, closing, receiving from closed/nil channels. 🔴⭐
- **`select`** — multiplexing, default case, timeouts with `time.After`. 🟡⭐
- **`sync.WaitGroup`** — waiting for goroutines to finish. 🟢⭐
- **`sync.Mutex` / `RWMutex`** — protecting shared state; read vs write locks. 🟡⭐
- **`sync.Once`** — one-time initialization (safe singleton). 🟡
- **`sync.Cond`** — condition variables (rarely needed, good to know). 🔴
- **`sync/atomic`** — lock-free counters, CAS operations. 🔴
- **`sync.Pool`** — object reuse to reduce GC pressure. 🔴
- **`context.Context`** — cancellation, deadlines, request-scoped values. 🔴⭐
- **Go memory model** — happens-before, when writes are visible across goroutines. 🔴⭐
- **Concurrency patterns** — worker pool, fan-in/fan-out, pipeline, semaphore, rate limiting. 🔴⭐
- **Race conditions & `-race` detector** — detecting and fixing data races. 🔴⭐
- **Deadlocks / livelocks** — causes and how the runtime detects "all goroutines asleep." 🔴⭐
- **Channels vs mutexes** — "share memory by communicating" vs shared-state locking. 🔴⭐

## 7. Error Handling ⭐

Deep-dives: [07-Error-Handling/](07-Error-Handling/README.md)

- **`error` interface** — errors are values, explicit checking. 🟢⭐
- **Creating errors** — `errors.New`, `fmt.Errorf`. 🟢
- **Error wrapping** — `%w`, `errors.Is`, `errors.As`, unwrapping chains. 🟡⭐
- **Sentinel errors vs typed errors** — `io.EOF` vs custom error types. 🟡⭐
- **`panic` / `recover`** — when panic is appropriate vs returning errors. 🟡⭐
- **Error handling idioms** — early return, don't ignore errors, wrap with context. 🟡
- **Custom error types** — implementing `error`, adding fields/behavior. 🟡

## 8. Generics (Go 1.18+)

Deep-dives: [08-Generics/](08-Generics/README.md)

- **Type parameters** — `func F[T any](...)`, generic types. 🟡
- **Constraints** — `comparable`, `constraints` package, custom constraint interfaces. 🔴
- **Type inference** — when the compiler infers type args. 🟡
- **When to use generics** — vs interfaces vs code duplication; trade-offs. 🔴⭐
- **Generic data structures** — writing a type-safe stack/set/linked list. 🔴

## 9. Standard Library Essentials

Deep-dives: [09-Standard-Library/](09-Standard-Library/README.md)

- **`fmt`** — formatting verbs, `Sprintf`, `Stringer`. 🟢
- **`io` / `bufio`** — Reader/Writer, buffering, `io.Copy`. 🟡⭐
- **`encoding/json`** — marshal/unmarshal, struct tags, `omitempty`, custom marshalers. 🟡⭐
- **`net/http`** — server, handlers, `ServeMux`, middleware, client. 🟡⭐
- **`time`** — durations, timers, tickers, formatting (reference date). 🟡
- **`os` / `flag`** — env, args, file ops, CLI flags. 🟢
- **`sort` / `slices` / `maps`** — sorting and the newer generic helpers. 🟡
- **`regexp`, `strings.Builder`** — efficient string building & matching. 🟡
- **`reflect`** — runtime reflection; use sparingly, know the cost. 🔴

## 10. Testing & Tooling

Deep-dives: [10-Testing-Tooling/](10-Testing-Tooling/README.md)

- **`testing` package** — table-driven tests, `t.Run` subtests. 🟢⭐
- **Benchmarks** — `Benchmark*`, `b.N`, `testing.B`. 🟡
- **Test doubles** — interfaces for mocking, `httptest`. 🟡⭐
- **Coverage & fuzzing** — `-cover`, native fuzzing (1.18+). 🟡
- **`go test` / race flag** — running with `-race`, `-run`, `-v`. 🟡
- **Toolchain** — `go build`, `go vet`, `gofmt`, `go mod`, linters (staticcheck). 🟢
- **Go modules** — `go.mod`, `go.sum`, semantic import versioning, vendoring. 🟡⭐
- **Build constraints & tags** — platform-specific builds. 🔴
- **Profiling** — `pprof` (CPU/heap/goroutine), `trace`. 🔴⭐

## 11. Runtime, Memory Management & Performance 🔴

Deep-dives: [11-Runtime-Performance/](11-Runtime-Performance/README.md)

- **Goroutine scheduler (GMP model)** — G, M, P; work-stealing, preemption. 🔴⭐
- **Garbage collector** — concurrent tri-color mark-sweep, write barriers, GC tuning (`GOGC`). 🔴⭐
- **Escape analysis & allocation** — reducing heap allocs, stack allocation. 🔴⭐
- **Memory optimization** — struct field alignment/padding, reducing allocations, `sync.Pool`. 🔴
- **`GOMAXPROCS`** — parallelism vs concurrency. 🟡⭐
- **Inlining & compiler optimizations** — what the compiler does for you. 🔴
- **Performance profiling workflow** — find hot paths, benchmark, optimize, verify. 🔴⭐

## 12. Idioms, Best Practices & Design

Deep-dives: [12-Idioms-Design/](12-Idioms-Design/README.md)

- **Idiomatic Go** — simplicity, small interfaces, composition over inheritance. 🟡⭐
- **Project layout & package design** — cohesion, avoiding cyclic imports. 🟡
- **Dependency injection** — constructor injection, no framework needed. 🟡
- **Functional options pattern** — configurable constructors. 🔴⭐
- **Graceful shutdown** — signal handling + `context` cancellation. 🔴⭐
- **Config & env management** — twelve-factor style. 🟡

## 13. Classic Interview Gotchas (memorize these) ⭐

Deep-dives: [13-Classic-Gotchas/](13-Classic-Gotchas/README.md)

- **Loop variable capture in goroutines/closures** — the #1 Go trap (pre-1.22 behavior). 🔴⭐
- **nil interface != nil** — typed nil stored in an interface is non-nil. 🔴⭐
- **Slice `append` aliasing** — mutating a shared backing array unexpectedly. 🔴⭐
- **Map iteration order** — intentionally randomized. 🟡⭐
- **`defer` in a loop** — deferred calls pile up until function returns. 🟡⭐
- **Range copies values** — modifying the range variable doesn't change the slice. 🟡⭐
- **Comparing structs/slices/maps** — slices & maps aren't comparable with `==`. 🟡
- **Buffered vs unbuffered channel deadlocks** — send on full/unbuffered blocks. 🔴⭐
- **Goroutine leak from unread channel** — sender blocks forever. 🔴⭐
- **`time.After` in `select` loops** — leaks timers under load. 🔴

---

## Study priority (senior SWE)

1. **Non-negotiable, expect deep questions:** Concurrency (goroutines, channels, select, sync, context, memory model, patterns), Interfaces (value vs pointer receivers, nil-interface trap), Slices/Maps internals, Error handling & wrapping, the classic gotchas.
2. **Strong differentiators:** Runtime (GMP scheduler, GC), escape analysis/memory optimization, profiling with pprof, generics trade-offs, functional options & graceful shutdown.
3. **Round out:** stdlib fluency (`io`, `net/http`, `encoding/json`), testing (table-driven, `-race`, benchmarks), modules & tooling.

How senior Go interviews usually go: a **coding task** (often concurrent — worker pool, rate limiter, or a channel-based problem), a **language-internals grill** (slices, interfaces, GC, scheduler), and a **debug/gotcha** segment ("why does this leak / why isn't this nil / why is this a race"). Be ready to write concurrent code cleanly *and* explain what the runtime does underneath.
