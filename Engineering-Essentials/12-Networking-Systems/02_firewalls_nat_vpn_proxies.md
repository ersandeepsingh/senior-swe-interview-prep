# Firewalls, NAT, VPN, Proxies

> Tools that control **who can talk to whom** and **how addresses look** across network boundaries.

## Plain English

These are the common boundary tools in cloud and corp networks. In interviews, separate **jobs** (filter, rewrite, tunnel, middleman) — products often combine them.

```text
  Laptop (10.0.0.5) --NAT--> Public IP --Internet--> Website
  Laptop --VPN tunnel--> Corp network --access--> internal APIs
  Browser --forward proxy--> Internet
  Internet --reverse proxy--> App pods
```

**Security groups / NACLs** in cloud are firewalls with different scopes. **Zero trust** pushes identity-aware access beyond “inside VPN = trusted.”

## Essentials (must-know for this topic)

### Tool cheat sheet

| Tool | Job |
|------|-----|
| **Firewall** | Allow/deny traffic by rules (IP, port, protocol, sometimes app) |
| **NAT** | Rewrite addresses; many private IPs share one public IP |
| **VPN** | Encrypted tunnel; machine appears on another network |
| **Forward proxy** | Client-side middleman (corp proxy → internet) |
| **Reverse proxy** | Server-side middleman (nginx in front of apps) |

### NAT vs VPN vs proxy (quick compare)

| | NAT | VPN | Reverse proxy |
|---|-----|-----|---------------|
| Primary job | Address rewrite / egress | Encrypted remote network access | Front apps: TLS, route, buffer |
| Typical place | Edge of private subnet | Laptop ↔ corp/cloud | Internet → your services |
| Security alone? | No | No (still need authz) | No (still need authn/z) |

### Cloud deploy pattern (must-know)

| Piece | Role |
|-------|------|
| Private subnet | Apps, no public IPs |
| **NAT gateway** | Pods **egress** to internet (e.g. Stripe) |
| SG / firewall | Only LB → app on 443 |
| VPN / bastion | Humans reach admin endpoints |
| Reverse proxy / ingress | Terminate TLS, route to services |

## Simple example

Deploying an API:

1. Private subnet: app pods, no public IPs.
2. NAT gateway: pods can **egress** to Stripe.
3. Firewall / SG: only allow 443 from the load balancer SG to app SG.
4. Optional VPN/bastion for humans to reach admin endpoints.
5. Reverse proxy / ingress terminates TLS and routes to services.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| NAT egress | Private apps can call out | Asymmetric paths; IP allowlists hard (many tenants share NAT IP) |
| Flat VPN trust | Simple remote access | Lateral movement if laptop compromised |
| Strict firewall deny-by-default | Smaller blast radius | More rules to maintain; breakages |
| Forward corporate proxy | Control/audit egress | Breaks some protocols; TLS inspection pain |

## Pitfalls

- **Allow 0.0.0.0/0 on SSH** “temporarily.”
- **Hairpin / NAT confusion** — services can't reach themselves via public IP.
- **Assuming VPN = security** — still need authz inside.
- **Forgetting egress rules** — app can't pull images or call third parties.
- **Proxy buffering** surprising timeouts for long requests/WebSockets.

## Interview trigger phrase

> “I'd put apps in **private subnets**, control **ingress via LB/SG**, use **NAT for egress**, and treat VPN as remote access — not as the only security boundary.”

## Exercise

A service in a private subnet must call an external payment API allowlisted by IP. What networking piece do you need, and what's the operational downside of shared NAT IPs?
