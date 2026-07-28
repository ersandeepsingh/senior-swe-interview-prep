# Docker (Containers)

> A **container** packages your app + runtime dependencies into a portable unit. **Docker** builds **images** (layered filesystem snapshots) and runs **containers** from them. Same artifact from laptop → CI → prod.

## Plain English

| Term | Meaning |
|------|---------|
| **Image** | Immutable template (layers of filesystem + metadata) |
| **Container** | Running instance of an image |
| **Dockerfile** | Recipe to build an image |
| **Layer** | Cached filesystem diff; rebuild only changed layers |
| **Registry** | Store/pull images (Docker Hub, ECR, GCR) |

```text
  Dockerfile → docker build → Image → docker run → Container
       │                         │
    FROM, COPY, RUN           tags: app:1.2.3
```

Containers share the host kernel (unlike full VMs) → lighter and faster to start.

## Essentials (must-know for this topic)

### Image vs container vs layer

| Term | Meaning |
|------|---------|
| **Image** | Immutable template (layered FS + metadata + entrypoint) |
| **Container** | Running (or stopped) **instance** of an image |
| **Layer** | Cached filesystem diff from a Dockerfile instruction |
| **Dockerfile** | Build recipe (`FROM`, `COPY`, `RUN`, …) |
| **Tag** | Human name (`app:1.2.3`); prefer git SHA in prod |
| **Registry** | Store/pull images (ECR, GCR, Docker Hub) |

### Image vs VM (one-liner)

| | **Container** | **VM** |
|---|---------------|--------|
| Isolation | Share host **kernel** | Own guest OS / kernel |
| Size / start | Light, seconds | Heavier |
| Use | App packaging, microservices | Stronger isolation, custom kernels |

### Build hygiene (interview list)

| Practice | Why |
|----------|-----|
| Multi-stage build | Tiny final image |
| Non-root user | Blast radius |
| Pin base digests/versions | Reproducible |
| No secrets in layers | History leaks forever |
| `.dockerignore` | Fast, small build context |

## Simple example

```dockerfile
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
USER nonroot
CMD ["gunicorn", "app:app"]
```

**Best practices:** small base images, multi-stage builds, non-root user, pin versions, don’t bake secrets into layers, `.dockerignore`, one process per container (usual rule).

## When to use / trade-offs

| Prefer **containers** when… | Prefer **VM / bare metal** when… |
|-----------------------------|----------------------------------|
| Same runtime across envs | Need custom kernel / heavy isolation |
| Microservices, K8s, CI | Legacy apps hard to containerize |
| Fast scale-out of stateless apps | Strict compliance on dedicated hosts |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Fat image (all tools) | Convenient debug | Size, attack surface, slow pulls |
| Slim/distroless | Security, speed | Harder live debugging |
| Multi-stage build | Small final image | Slightly more Dockerfile complexity |

## Pitfalls

- Secrets in `ENV` / build args → leaked in image history.  
- Running as **root**.  
- Huge context (no `.dockerignore`) → slow builds.  
- Mutable “latest” tag in prod → unreproducible deploys.  
- Storing important state **only** in the container filesystem.

## Interview trigger phrase

> “I’d ship a **small, pinned, non-root image** built in CI, tagged by git SHA, with secrets injected at runtime — not baked into layers.”

## Exercise

**Containerize a Node API.**

1. Sketch a multi-stage Dockerfile (build vs run).  
2. Name three things that must *not* be in the image.  
3. Why is `latest` dangerous in Kubernetes manifests?
