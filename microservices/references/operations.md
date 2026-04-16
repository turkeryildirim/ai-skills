# Deployment & Operations

**Impact:** HIGH · **Prefix:** `ops-` · **4 rules**

Services live in a scheduler (Kubernetes). Operational patterns make rollouts boring: the scheduler knows when to start a pod, when to send it traffic, when to stop sending traffic, and when to kill it.

## Load When

- Writing a new service's Dockerfile / Helm chart / manifest
- Debugging pods flapping between Ready and NotReady
- Rolling out a release that risks dropping in-flight requests
- Moving an env-specific value out of a baked-in config file
- Designing a canary or blue-green strategy

## Rules

| Rule | Summary |
|------|---------|
| [`ops-health-probes`](../rules/ops-health-probes.md) | `/health/live` and `/health/ready` are different |
| [`ops-graceful-shutdown`](../rules/ops-graceful-shutdown.md) | Drain in-flight work before SIGTERM grace expires |
| [`ops-config-externalization`](../rules/ops-config-externalization.md) | Config via env vars / secret manager — same image everywhere |
| [`ops-zero-downtime-deploys`](../rules/ops-zero-downtime-deploys.md) | Rolling / blue-green / canary with automated rollback |

## Liveness vs Readiness

| | Liveness | Readiness |
|--|---------|-----------|
| Question | Am I alive? | Can I serve traffic? |
| Fails → | pod restarted | pod removed from Service endpoints |
| Checks | process responds | deps reachable, warmup done, queues drained (on shutdown) |
| Bad pattern | check DB here | skip the DB dep check |

**Liveness checking external deps** is the classic mistake — a shared DB blip then restarts every pod in the fleet.

## Graceful Shutdown Sequence

```
SIGTERM received
  │
  ├─► mark /health/ready = 503         ← service mesh stops sending traffic
  │   (wait preStop + readinessPeriod: ~5–10s)
  │
  ├─► stop accepting new HTTP connections
  ├─► stop polling queues
  ├─► wait for in-flight requests to finish  (bounded by grace period)
  ├─► flush logs, traces, metrics
  └─► exit(0)
```

K8s default `terminationGracePeriodSeconds` is 30s. If requests can take longer, bump it **and** wire the preStop hook.

## Config Hierarchy

1. **Env vars** — everything 12-factor (URLs, flags, log levels)
2. **Secret manager** — passwords, API keys (never env vars in git / Helm values)
3. **Feature flags** — runtime toggles (LaunchDarkly, Unleash, or a DB table)
4. **ConfigMap** — non-secret, non-code config that's environment-specific

Same container image runs in dev / staging / prod — only env differs.

## Rollout Strategies

| Strategy | How | Rollback | Use when |
|----------|-----|----------|----------|
| Rolling | k8s replaces pods N at a time | scale old RS back up | Default; compatible schemas |
| Blue-green | two full stacks, cut traffic | flip service back | Risky schema / contract changes |
| Canary | 1–5% traffic to new version | remove canary | High-risk changes, need real data |
| Shadow | mirror traffic, discard response | stop mirroring | Pre-validate new path |

Automate rollback based on SLO burn rate (error rate, latency p99) — not just pod health.

## Pre-Deploy Checklist

- [ ] DB migrations are backwards-compatible (expand → migrate → contract)
- [ ] New service version can read events emitted by old version, and vice versa
- [ ] Feature hidden behind a flag if user-facing
- [ ] Dashboards & alerts exist for the new code paths
- [ ] `kubectl rollout undo` works (no one-way migrations tied to the deploy)
