# Serverless / FaaS

> **Serverless functions** (AWS Lambda, etc.) run your code on demand without you managing servers. Pay per invocation + duration. Great for **spiky**, **event-driven**, or low-ops workloads — with **cold start** and limits in mind.

## Plain English

| Trait | Meaning |
|-------|---------|
| **Event-driven** | Triggered by HTTP, queue, cron, storage event, … |
| **Scale to zero** | No traffic → no instances (cost win) |
| **Cold start** | First request after idle pays startup latency |
| **Stateless** | Don’t rely on local disk/memory across invokes |
| **Limits** | Timeouts (e.g. 15 min), payload sizes, concurrency caps |

```text
  S3 upload → Lambda → write thumbnail → DynamoDB
  API Gateway → Lambda → RDS (via proxy) → response
```

## Essentials (must-know for this topic)

### Serverless traits you must define

| Trait | Meaning |
|-------|---------|
| **FaaS** | Function-as-a-Service — upload code, provider runs it |
| **Event-driven** | Triggered by HTTP, queue, cron, storage event, … |
| **Scale to zero** | Idle → no instances (cost win) |
| **Cold start** | First invoke after idle pays startup latency |
| **Stateless** | No sticky local memory/disk across invokes |
| **Concurrency limit** | Max parallel executes (throttle risk) |

### Serverless vs containers (decision table)

| Prefer **Lambda/FaaS** when… | Prefer **containers** when… |
|------------------------------|-----------------------------|
| Spiky / intermittent traffic | Steady high RPS |
| Glue, webhooks, light APIs | Long-lived WS / heavy CPU |
| Minimal ops for small surface | Need fixed low latency |

### Ops that still exist

| Concern | Reality |
|---------|---------|
| IAM, DLQ, retries | Still your design |
| DB connections | Pool via RDS Proxy / similar |
| Observability | Trace + logs across many short invokes |

## Simple example

**Thumbnailer:** user uploads to S3 → event invokes function → generates sizes → writes back to S3 → updates metadata. No fleet to patch.

**Cron:** EventBridge schedule → Lambda → emit report.

## When to use / trade-offs

| Prefer **serverless** when… | Prefer **containers/VMs** when… |
|-----------------------------|-------------------------------|
| Spiky / intermittent traffic | Steady high RPS (cost/latency) |
| Glue code, webhooks, light APIs | Long-lived connections (WS), heavy CPU |
| Small team wants minimal ops | Need fixed latency, custom networking depth |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Scale to zero | Cost at idle | Cold starts |
| Managed scaling | Less capacity planning | Concurrency surprises / throttling |
| Many tiny functions | Isolation | Distributed sprawl, tracing harder |

## Pitfalls

- Cold starts on latency-sensitive user paths (mitigate: provisioned concurrency, lighter runtimes, keep-warm carefully).  
- Connecting to **RDS** from many Lambdas without pooling (RDS Proxy).  
- Timeouts shorter than downstream → retries amplify load.  
- Giant deployment packages.  
- Assuming “no servers” means “no ops” — still need IAM, observability, DLQs.

## Interview trigger phrase

> “I’d use **Lambda for event-driven and spiky work**, design for **statelessness** and **idempotency**, and avoid it when I need **steady ultra-low latency** or long-lived connections — then containers win.”

## Exercise

**Webhook receiver for Stripe.**

1. Why is serverless a good fit?  
2. How do you handle retries + idempotency?  
3. When would you move this to a always-on service instead?
