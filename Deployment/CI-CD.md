# CI/CD — Continuous Integration & Continuous Delivery/Deployment

> **CI/CD automates getting code from a developer’s laptop into production safely and repeatedly** — build, test, and release on every change instead of manual “hope it works” deploys.

---

## 1. Plain English

| Term | Meaning |
|------|---------|
| **CI — Continuous Integration** | Developers merge often; each merge **automatically builds + runs tests**. Breakages are caught in minutes, not at release day. |
| **CD — Continuous Delivery** | Every green build produces a **release candidate** that *could* go to prod (often one-click / approval). |
| **CD — Continuous Deployment** | Every green build **goes to production automatically** (no manual gate). |

```text
  Code push / PR
       │
       ▼
  ┌──────── CI ────────┐
  │  build → unit test │
  │  lint → security   │
  └─────────┬──────────┘
            ▼
  ┌──────── CD ────────┐
  │  package (image)   │
  │  deploy staging    │
  │  integration tests │
  │  → prod (auto or   │
  │    with approval)  │
  └────────────────────┘
```

**Without CI/CD:** “Works on my machine” → Friday night deploy → rollback chaos.  
**With CI/CD:** small changes, fast feedback, same pipeline every time.

---

## 2. Typical pipeline stages

| Stage | What happens | Example |
|-------|----------------|---------|
| **Trigger** | Push, PR, tag, schedule | Push to `main`, open PR |
| **Checkout** | Fetch source | `actions/checkout` |
| **Build** | Compile / bundle | `go build`, `npm run build`, Docker build |
| **Test** | Unit / integration | `pytest`, `go test`, Jest |
| **Static checks** | Lint, format, typecheck | ESLint, `golangci-lint`, mypy |
| **Security** | Scan deps / image | Snyk, Trivy, Dependabot |
| **Package** | Artifact or container | Docker image → ECR/GHCR |
| **Deploy** | Push to an environment | Helm/kubectl, Terraform, serverless |
| **Verify** | Smoke / e2e / health | Hit `/health`, Playwright |
| **Notify** | Slack / email on fail | Pipeline status |

---

## 3. Tools (what interviewers expect)

### CI/CD platforms (orchestrate the pipeline)

| Tool | Where it shines | Notes |
|------|-----------------|-------|
| **GitHub Actions** | Repos on GitHub; YAML workflows | Very common; marketplace actions |
| **GitLab CI** | GitLab; `.gitlab-ci.yml` | Built-in registry + environments |
| **Jenkins** | Self-hosted, highly customizable | Powerful but heavier to operate |
| **CircleCI** | Cloud CI, good caching | Popular with startups |
| **Azure DevOps Pipelines** | Microsoft / Azure shops | Boards + repos + pipelines |
| **Bitbucket Pipelines** | Atlassian stack | Tight Jira integration |
| **Argo CD** | **GitOps** deploys to Kubernetes | Watches Git; syncs cluster state |
| **Flux** | GitOps for Kubernetes | CNCF; similar niche to Argo CD |
| **Tekton** | Cloud-native pipelines on K8s | Pipeline CRDs |
| **AWS CodePipeline / CodeBuild** | AWS-native | Pairs with CodeCommit/ECR/ECS |
| **Google Cloud Build** | GCP-native | Triggers from Cloud Source/GitHub |
| **Spinnaker** | Multi-cloud continuous delivery | Netflix-style; canary/deploy strategies |

### Supporting tools in the same workflow

| Area | Tools | Role |
|------|-------|------|
| **VCS** | GitHub, GitLab, Bitbucket | Source of truth; PR gates |
| **Artifacts** | Nexus, Artifactory, npm/PyPI | Store build outputs |
| **Containers** | Docker, Podman, BuildKit | Package app + runtime |
| **Registries** | ECR, GCR, GHCR, Docker Hub | Store images |
| **IaC** | Terraform, Pulumi, CloudFormation | Provision infra from pipeline |
| **K8s deploy** | kubectl, Helm, Kustomize, Argo CD | Roll out services |
| **Tests** | JUnit, pytest, Jest, Playwright, k6 | Quality gates |
| **Security** | Trivy, Snyk, SonarQube, CodeQL | Shift-left scanning |
| **Secrets** | GitHub Secrets, Vault, AWS SM | Never hardcode credentials |
| **Observability** | Datadog, Prometheus, CloudWatch | Detect bad deploys fast |

---

## 4. Example A — GitHub Actions (CI + deploy image)

Simple Go/Node-style flow: test on PR, build & push image on `main`.

```yaml
# .github/workflows/ci-cd.yml
name: ci-cd

on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.22"
      - name: Unit tests
        run: go test ./...
      - name: Lint
        run: go vet ./...

  build-and-push:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: docker build -t ghcr.io/myorg/myapp:${{ github.sha }} .
      - name: Push
        run: |
          echo "${{ secrets.GHCR_TOKEN }}" | docker login ghcr.io -u USER --password-stdin
          docker push ghcr.io/myorg/myapp:${{ github.sha }}
```

**What this gives you:** every PR is tested; `main` always produces a versioned image tagged by commit SHA.

---

## 5. Example B — GitLab CI

```yaml
# .gitlab-ci.yml
stages: [test, build, deploy]

unit_tests:
  stage: test
  image: golang:1.22
  script:
    - go test ./...

docker_build:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  only:
    - main

deploy_staging:
  stage: deploy
  script:
    - helm upgrade --install myapp ./chart
        --set image.tag=$CI_COMMIT_SHA
        --namespace staging
  environment:
    name: staging
  only:
    - main
```

---

## 6. Example C — Jenkins (conceptual)

```text
  Jenkinsfile (Pipeline as Code)
       │
       ├─ stage('Test')   { sh 'npm test' }
       ├─ stage('Build')  { sh 'docker build ...' }
       └─ stage('Deploy') { sh 'kubectl set image ...' }
```

Jenkins runs agents (VMs/containers), polls Git or uses webhooks, stores history/artifacts. Common when companies need on-prem control.

---

## 7. Example D — GitOps with Argo CD (Kubernetes)

**Idea:** pipeline only updates Git (image tag). **Argo CD** syncs the cluster to match Git.

```text
  Dev push → CI builds image → CI updates values.yaml (tag=abc123) in Git
                                      │
                                      ▼
                               Argo CD detects drift
                                      │
                                      ▼
                               Cluster rolls out new pods
```

**Why teams like it:** cluster state is auditable in Git; rollbacks = `git revert`.

---

## 8. Continuous Delivery vs Continuous Deployment

| | Continuous **Delivery** | Continuous **Deployment** |
|--|-------------------------|---------------------------|
| Prod release | Ready anytime; **human approval** often | **Automatic** if tests pass |
| Best when | Regulated / high risk | Strong tests + fast rollback |
| Example | Deploy to staging auto; prod needs click | Merge to `main` → prod in minutes |

Both still use the same CI pipeline; they differ at the **last mile**.

---

## 9. Senior practices (say these out loud)

1. **Pipeline as code** — YAML/Jenkinsfile in the repo, reviewed like app code  
2. **Fail fast** — unit tests before slow e2e / image build  
3. **Immutable artifacts** — build once, promote same image `dev → staging → prod`  
4. **Environment parity** — staging ≈ prod (same charts, smaller scale)  
5. **Secrets never in logs/YAML** — inject from vault/CI secret store  
6. **Progressive delivery** — rolling / blue-green / canary + auto-rollback  
7. **Trunk-based + small PRs** — CI only works if integration is frequent  

```text
  Bad:  build different binaries per env ("prod build" with magic flags)
  Good: one image digest; config via env / Feature flags / ConfigMap
```

---

## 10. Mini end-to-end story (interview narration)

> “On every PR, GitHub Actions runs unit tests and lint. On merge to `main`, we build a Docker image tagged with the commit SHA, push to ECR, and update our Helm values. Argo CD syncs staging automatically; production sync requires an approval or a tag. If the `/health` smoke check fails, we roll back to the previous image digest. IAM roles grant the pipeline push-to-ECR and the cluster pull rights — no long-lived keys in the repo.”

---

## 11. Common interview questions

| Question | Short answer |
|----------|--------------|
| CI vs CD? | CI = integrate+test often; CD = release ready (delivery) or auto-prod (deployment) |
| Why Docker in CI? | Same artifact everywhere; fewer “works on my machine” issues |
| How to secret-manage? | CI secret store / Vault / cloud SM; short-lived OIDC roles into AWS |
| How to deploy safely? | Canary/blue-green, health checks, instant rollback, feature flags |
| Jenkins vs GitHub Actions? | Jenkins = flexible/self-hosted; GHA = low ops if you’re on GitHub |

---

## 12. Exercise

1. Sketch a pipeline for a Go API + Postgres: list stages from PR → prod.  
2. Pick **GitHub Actions vs Jenkins vs Argo CD** for a startup on Kubernetes — justify in 3 bullets.  
3. Name one failure mode of “auto deploy to prod” and one control that mitigates it (tests, canary, flag, approval).
