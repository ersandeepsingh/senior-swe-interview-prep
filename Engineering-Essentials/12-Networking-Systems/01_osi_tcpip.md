# OSI / TCP-IP Model

> Mental map of **where** problems live: cables and IPs vs TCP connections vs HTTP apps. You don't memorize every PDU — you know which layer to blame.

## Plain English

**OSI** (7 layers) is the teaching model; **TCP/IP** (4 layers) is what the internet actually uses. You triage “site is down” by placing the failure on the stack.

```text
  Browser → HTTPS (app + TLS)
         → TCP port 443 (transport)
         → IP packets to 93.184.216.34 (internet)
         → Ethernet frames on your LAN (link)
```

## Essentials (must-know for this topic)

### OSI ↔ TCP/IP map

| OSI | TCP/IP | Examples |
|-----|--------|----------|
| 7 Application | Application | HTTP, gRPC, DNS, TLS* |
| 6 Presentation | (folded in) | Encoding, compression |
| 5 Session | (folded in) | Sessions / connection mgmt concepts |
| 4 Transport | Transport | TCP, UDP |
| 3 Network | Internet | IP, routing, ICMP |
| 2 Data link | Network access | Ethernet, Wi-Fi, MAC |
| 1 Physical | Network access | Fiber, copper, radio |

\*TLS is often discussed as “between transport and application.”

### TCP vs UDP

| | **TCP** | **UDP** |
|---|---------|---------|
| Model | Connection-oriented, reliable, ordered | Datagrams, no built-in reliability |
| Features | Handshake, retransmit, congestion control | Low overhead; app (or QUIC) handles reliability |
| Use | APIs, most request/response | DNS, video/games, QUIC/HTTP3 base, tunneling |

### Triage by layer

| Symptom | Likely layer |
|---------|--------------|
| No link light / Wi-Fi disconnect | Physical / link |
| Can't ping IP, traceroute dies | Network / routing |
| SYN sent, no handshake | Firewall or host down (transport path) |
| TCP OK, HTTP 502 | App / proxy / upstream |
| Certificate error | TLS |

## Simple example

“Site is down” triage by layer — use the table above. Fix at L7 is useless if the SYN never completes.

## Trade-offs

| Prefer **TCP** when… | Prefer **UDP** when… |
|----------------------|----------------------|
| Correctness & ordering matter | Latency / loss tolerance / custom reliability |
| Request/response APIs | Real-time media, gaming, some tunneling |
| You want the OS to retransmit | You implement reliability yourself (or QUIC does) |

## Pitfalls

- **Blaming “the network”** without saying which layer.
- **Assuming HTTP retries fix TCP resets** — sometimes you need connection pooling / keepalives / LB idle timeouts aligned.
- **Forgetting DNS is often UDP** (and a common outage root).
- **Mixing L4 vs L7 load balancing** vocabulary (see LB topic).

## Interview trigger phrase

> “I'd place the failure on the stack — IP routing vs TCP vs TLS vs HTTP — because the fix at L7 is useless if the SYN never completes.”

## Exercise

Users can `ping` the server IP but browsers show connection timeout on HTTPS. Which layers have likely succeeded, and what would you check next?
