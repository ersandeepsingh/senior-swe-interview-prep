# Kubernetes

> **Kubernetes (K8s)** schedules and runs containers across a cluster. You declare desired state; the control plane **reconciles** reality toward it — restarts, scaling, rollouts.

## Plain English

| Object | Role |
|--------|------|
| **Pod** | Smallest unit — one or more containers sharing network/storage |
| **Deployment** | Manages replica Pods + rolling updates |
| **Service** | Stable virtual IP / DNS to reach Pods |
| **Ingress** | HTTP(S) routing from outside into Services |
| **ConfigMap / Secret** | Config and sensitive config injected into Pods |
| **HPA** | Horizontal Pod Autoscaler |

```text
  Ingress → Service → Pod(s) managed by Deployment
                         │
                    node(s) in cluster
```

You don’t usually SSH to fix one container — you fix the **spec** and let K8s replace Pods.

## Essentials (must-know for this topic)

### Core objects — one-liners

| Object | Role |
|--------|------|
| **Pod** | Smallest deployable unit — container(s) sharing network/volumes |
| **Deployment** | Desired replicas + rolling updates of Pods |
| **Service** | Stable ClusterIP/DNS in front of changing Pod IPs |
| **Ingress** | HTTP(S) routing from outside → Services |
| **ConfigMap** | Non-secret config injected as env/files |
| **Secret** | Sensitive config (still base64 in etcd — protect the cluster) |
| **HPA** | Horizontal Pod Autoscaler — scale replicas on metrics |
| **Namespace** | Soft isolation / quota boundary inside a cluster |
| **StatefulSet** | Sticky identity + storage for stateful apps |

### Traffic path

```text
  Ingress → Service → Pod(s) ← Deployment / ReplicaSet
```

### Probes that belong here

| Probe | Meaning |
|-------|---------|
| **Liveness** | Dead? restart container |
| **Readiness** | Ready for traffic? remove from Service endpoints |
| **Startup** | Slow boot grace before liveness kills |

## Simple example

**API with 3 replicas:**

```text
  Deployment: api, replicas: 3, image: ecr/.../api:sha-abc
  Service: ClusterIP api:80 → Pods labeled app=api
  Ingress: api.example.com/ → Service api
  Secret: DB_URL mounted as env
  HPA: CPU > 70% → scale 3..20
```

**Rolling update:** new ReplicaSet ramps up; old ramps down; readiness probes gate traffic.

## When to use / trade-offs

| Prefer **Kubernetes** when… | Prefer **simpler** when… |
|-----------------------------|--------------------------|
| Many services, need scheduling/healing | One or two apps on App Runner / ECS / VMs |
| Team can operate (or buy managed EKS/GKE/AKS) | Ops cost &gt; benefit |
| Custom networking, batch, cron, stateful sets | Pure serverless fits |

| Decision | You gain | You give up |
|----------|----------|-------------|
| More replicas | Availability | Cost; need stateless design |
| Rolling update | Zero-ish downtime | Need readiness/backward compatible |
| StatefulSet + PVC | Sticky identity/storage | Harder than stateless |

## Pitfalls

- No **readiness/liveness** probes → traffic to dead Pods or kill loops.  
- Resource requests/limits missing → noisy neighbors / OOMKill.  
- Secrets in plain ConfigMaps.  
- One giant cluster with no namespaces/quotas → blast radius.  
- Treating K8s as “free HA” without multi-AZ and pod disruption budgets.

## Interview trigger phrase

> “I’d run stateless services as **Deployments** behind a **Service/Ingress**, inject config via **ConfigMap/Secret**, gate rollouts with **readiness probes**, and scale with **HPA** on real SLI-related metrics.”

## Exercise

**Deploy a web API + worker.**

1. Which objects for API vs worker? Do they share a Service?  
2. Rolling update breaks DB migrations — what went wrong (compat story)?  
3. Pods crash-loop on missing env — which probe/config practice would catch it earlier?
