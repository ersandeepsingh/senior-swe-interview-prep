# HTTP/1.1 vs HTTP/2 vs HTTP/3 (QUIC)

> Same HTTP semantics (methods, status, headers) — different **how bytes move**, fixing head-of-line blocking step by step.

## Plain English

HTTP versions keep the same verbs and status codes; they change framing and transport. Knowing H1 → H2 → H3 is mostly about **multiplexing** and **head-of-line (HOL) blocking**.

## Essentials (must-know for this topic)

### Version comparison

| Version | Transport | Big idea | HOL issue |
|---------|-----------|----------|-----------|
| **HTTP/1.1** | TCP | Text; often one req at a time per conn (or few parallel conns) | Slow response blocks next on that conn |
| **HTTP/2** | TCP | Binary frames; **multiplex** many streams; HPACK headers | TCP packet loss stalls **all** streams |
| **HTTP/3** | **QUIC** (UDP) | Multiplex without TCP conn-wide HOL; faster setup | Loss isolated **per stream** |

### Vocab

| Term | Meaning |
|------|---------|
| **Multiplexing** | Many logical streams on one connection |
| **HOL blocking** | One stall blocks others sharing the pipe |
| **HPACK / QPACK** | Header compression (H2 / H3) |
| **QUIC** | UDP-based transport with its own reliability + TLS 1.3 integrated |
| **ALPN** | Negotiates `h2` / `h3` during TLS |

### Practical interview facts

| Fact | Implication |
|------|-------------|
| Same methods/status/headers | App code mostly unchanged |
| gRPC needs HTTP/2 (+ H3 where supported) | Check LB/mesh support |
| H3 needs UDP 443 | Corp firewalls may force H2 fallback |
| Many small assets | H2/H3 shine; one huge download may not |

## Why seniors get asked

Performance and infra interviews dig into “why is the site slow” and CDN/edge behavior. Knowing H2/H3 is a senior differentiator.

## Simple example

```bash
# See negotiated protocol
curl -sI --http2 https://example.com | head -5

# Chrome DevTools → Network → Protocol column: h2 or h3
```

Conceptual:

```
HTTP/1.1:  Conn1: req1 → resp1 → req2 → resp2
HTTP/2:    Conn1: stream1 + stream2 + stream3 interleaved frames
HTTP/3:    QUIC:  same multiplexing, loss on stream1 ≠ freeze stream2
```

## When to use / when not / trade-offs

| Reality | Implication |
|---------|-------------|
| Most browsers speak H2/H3 to public sites | Enable at load balancer / CDN |
| Some corp middleboxes break QUIC | Fall back to H2 |
| gRPC needs H2 (or H3 where supported) | Check LB HTTP/2 support |
| Tiny internal tools on H1 | Fine until concurrency hurts |

**Trade-offs:** H2/H3 cut latency for many small assets; debugging is harder (binary); H3 needs UDP 443 allowed.

## Common pitfalls

- Blaming “HTTP” when the issue is TCP congestion or huge payloads
- Assuming H2 always faster (one large download may not benefit)
- Load balancers that terminate H2 then open many H1 upstreams poorly
- Blocking UDP and wondering why H3 never sticks

## Interview trigger phrase

> “HTTP/2 multiplexes over TCP; HTTP/3 moves to QUIC so packet loss doesn’t stall every stream — same API semantics, better transport.”

## Exercise

A page loads 50 small JSON APIs. Explain why HTTP/1.1 browsers open multiple connections, how H2 helps, and when you’d still concatenate or BFF-aggregate those calls.
