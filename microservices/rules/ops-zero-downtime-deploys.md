---
title: Rolling / blue-green / canary with automated rollback
impact: HIGH
tags: [operations, deploy]
---

# ops-zero-downtime-deploys

Deploys should be boring. The scheduler rolls pods gradually; readiness probes gate traffic; backwards-compatible schema changes mean old and new versions coexist during the cutover; SLO burn-rate auto-rolls-back bad versions.

## Bad — Deploy script

```bash
kubectl delete deploy orders-api
kubectl apply -f orders-api.yaml       # hard outage during the gap
psql -c 'ALTER TABLE orders DROP COLUMN legacy_status;'  # breaks old pods
```

## Good — Kubernetes Deployment (rolling)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: orders-api }
spec:
  replicas: 6
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxSurge: 2, maxUnavailable: 0 }
  template:
    spec:
      terminationGracePeriodSeconds: 60
      containers:
        - name: app
          image: registry/orders-api:v1.4.2
          readinessProbe:
            httpGet: { path: /health/ready, port: 8080 }
            periodSeconds: 5
            failureThreshold: 3
          livenessProbe:
            httpGet: { path: /health/live, port: 8080 }
            periodSeconds: 10
            failureThreshold: 3
          lifecycle:
            preStop: { exec: { command: ['/bin/sh','-c','sleep 10'] } }
```

## Good — Schema migrations (expand → migrate → contract)

```sql
-- Release N: expand (backwards compatible)
ALTER TABLE orders ADD COLUMN status_v2 VARCHAR(32);
-- both old and new pods can run

-- Release N+1: migrate (new pods read status_v2; old still read status)
UPDATE orders SET status_v2 = status WHERE status_v2 IS NULL;

-- Release N+2: contract (after all old pods are gone)
ALTER TABLE orders DROP COLUMN status;
```

## Good — Canary with automated rollback

```yaml
# Argo Rollouts / Flagger — gate promotion on SLO burn rate
canary:
  steps:
    - setWeight: 5
    - pause: { duration: 5m }
    - analysis:
        templates: [{ templateName: error-rate-slo }]   # abort if > 0.5%
    - setWeight: 25
    - pause: { duration: 10m }
    - setWeight: 100
```

Never: drop columns while old pods exist, run one-shot deploy scripts that hold state, or rely on humans to flip traffic.
