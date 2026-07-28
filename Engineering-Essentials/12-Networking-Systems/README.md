# 12. Networking & Systems Foundations — Senior SWE Prep

The boring layer that makes distributed systems hard: packets, boundaries, latency, and how retries behave when the network lies. Seniors use orders-of-magnitude latency intuition in design discussions.

| # | Topic | File | Depth |
|---|-------|------|-------|
| 1 | OSI / TCP-IP model | [01_osi_tcpip.md](01_osi_tcpip.md) | 🟡 |
| 2 | Firewalls, NAT, VPN, proxies | [02_firewalls_nat_vpn_proxies.md](02_firewalls_nat_vpn_proxies.md) | 🟡 |
| 3 | LB vs reverse proxy vs API gateway | [03_lb_reverse_proxy_api_gateway.md](03_lb_reverse_proxy_api_gateway.md) | 🟡⭐ |
| 4 | Latency numbers | [04_latency_numbers.md](04_latency_numbers.md) | 🔴⭐ |
| 5 | Idempotency & retries at network layer | [05_idempotency_retries_network.md](05_idempotency_retries_network.md) | 🟡 |
| 6 | Rate limiting algorithms | [06_rate_limiting_algorithms.md](06_rate_limiting_algorithms.md) | 🟡⭐ |

**How to study:** place each technology on a layer, then estimate whether a design is memory-bound, disk-bound, or network-bound using the latency table.
