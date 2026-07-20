# Goroutine Scheduler (GMP Model)

> Go multiplexes millions of **goroutines (G)** onto OS threads (**M**) using **processors (P)** — logical tokens that grant run rights — with work-stealing and preemption.

## Plain English

A goroutine is cheap user-space concurrency. The runtime parks and resumes Gs without always creating OS threads. A **P** holds a run queue; an **M** (thread) must hold a P to execute Go code. If a G blocks in a syscall, the M can detach and another M may take the P so other Gs keep running.

## Why interviewers ask 🔴⭐

They want the vocabulary (G/M/P), work-stealing, what happens on channel block / syscall / network poll, and async preemption (since Go 1.14) so tight loops can’t freeze STW forever.

## The three letters

| Letter | Name | Role |
|--------|------|------|
| **G** | Goroutine | Stack + state; the “green thread” |
| **M** | Machine | OS thread; executes Gs |
| **P** | Processor | Resource needed to run Go code; count ≈ `GOMAXPROCS` |

```text
  G G G G     local runqueue
       \ | /
        [P] ---- owned by ---- [M] ---- OS thread
       / | \
  global runqueue / network poller
```

## Key behaviors

1. **Work stealing:** idle P steals half the Gs from another P’s local queue (or takes from global).
2. **Syscalls:** blocking syscall → M releases P; G stays “syscall”; another M may bind the P.
3. **Network:** netpoller wakes Gs when sockets ready — no thread per connection.
4. **Preemption:** async safe-points / signals so long-running Gs yield; fair scheduling.
5. **Handoff:** spinning Ms reduce latency when work appears.

## Minimal intuition example

```go
func main() {
    runtime.GOMAXPROCS(2) // 2 Ps → up to 2 Gs running true parallel Go code
    var wg sync.WaitGroup
    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func(i int) {
            defer wg.Done()
            // CPU work shares 2 Ps; I/O would park G and free P
            _ = i * i
        }(i)
    }
    wg.Wait()
}
```

## Pitfalls / misconceptions

- “Goroutines are OS threads” — no; many Gs per M.
- “`GOMAXPROCS` limits goroutines” — no; it limits **parallel** Go execution (Ps).
- Blocking cgo / non-Go syscalls can create extra Ms (thread explosion risk if unbounded).
- Spinning forever without function calls historically delayed preemption — less true with async preemption, still avoid huge tight loops without care.

## Interview trigger phrase

> “Gs are multiplexed onto Ms via Ps; blocking parks the G and frees the P; idle Ps steal work; `GOMAXPROCS` sets the P count for parallelism.”

## Exercise

Explain step-by-step what the scheduler does when a goroutine blocks on an unbuffered channel send, and when it blocks in a disk `Read` syscall.
