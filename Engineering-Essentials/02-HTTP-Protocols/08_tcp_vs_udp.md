# TCP vs UDP

> **TCP** = reliable, ordered byte stream with connection setup. **UDP** = fire-and-forget datagrams — fast, no built-in reliability.

## Plain English

Transport-layer choice: do you need a reliable stream (TCP) or lightweight packets you’ll handle yourself (UDP)? HTTP/1.1 and HTTP/2 ride TCP; **HTTP/3/QUIC** rides UDP and rebuilds reliability in userspace.

## Essentials (must-know for this topic)

### Head-to-head

| | **TCP** | **UDP** |
|--|---------|---------|
| Connection | Handshake (SYN → SYN-ACK → ACK) | None |
| Delivery | Reliable, retransmit | Best-effort |
| Order | Ordered byte stream | No order guarantee |
| Congestion control | Built-in | App / library (e.g. QUIC) |
| Message boundaries | **None** — you must frame | One datagram ≈ one message |
| Typical uses | HTTP/1.1, HTTP/2, SSH, DBs | DNS, video/VoIP, games, **QUIC/HTTP/3** |

### TCP handshake (say it out loud)

```
Client --SYN--> Server
Client <--SYN-ACK-- Server
Client --ACK--> Server
→ connected stream
```

### Why HTTP/3 uses UDP

| Problem on TCP+H2 | QUIC/H3 answer |
|-------------------|----------------|
| Packet loss blocks **all** multiplexed streams | Loss isolated per stream |
| TCP+TLS handshake cost | Combined crypto/transport setup |

### Pick for these (interview drill)

| Workload | Prefer | Why |
|----------|--------|-----|
| File download / API | TCP (or H3/QUIC) | Correctness |
| Live video/audio | UDP (+ codecs/jitter buffer) | Occasional loss OK |
| DNS lookup | UDP (TCP if truncated/large) | Tiny query |
| Player positions (lossy OK) | UDP | Latency |

## Why seniors get asked

Foundational systems question. Also explains why HTTP/3 uses UDP and why games don’t use raw TCP for everything.

## Simple example

```bash
# TCP check
nc -vz example.com 443

# UDP DNS
dig @8.8.8.8 example.com   # DNS typically uses UDP (TCP for large responses)
```

Pseudocode intuition:

```text
TCP.send(data)  // OS ensures delivery or errors out
UDP.send(packet) // OS sends once; app must handle loss if needed
```

## When to use / when not / trade-offs

| Prefer TCP when… | Prefer UDP when… |
|------------------|------------------|
| Correctness > micro-latency | Occasional loss OK (media) |
| You want a simple reliable stream | You implement custom reliability (QUIC) |
| Request/response APIs | Latency-sensitive fan-out |

**Trade-offs:** TCP head-of-line and handshake cost; UDP shifts complexity to the application (or QUIC library).

## Common pitfalls

- “UDP is always faster” without measuring or handling loss
- Assuming TCP messages preserve app-level message boundaries (it’s a byte stream — you must frame)
- Blocking UDP/443 and breaking HTTP/3
- Using TCP for realtime voice without tuning (latency spikes on retransmit)

## Interview trigger phrase

> “TCP gives reliable ordered streams; UDP is best-effort — HTTP/3 runs QUIC over UDP to keep multiplexing without TCP’s HOL blocking.”

## Exercise

For each, pick TCP or UDP and say why: file download, video call audio, HTTP/2 API, DNS lookup, multiplayer player positions (lossy OK).
