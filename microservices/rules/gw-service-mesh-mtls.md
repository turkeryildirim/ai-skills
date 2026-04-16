---
title: Mesh encrypts east-west traffic with mTLS and identity-based authz
impact: HIGH
tags: [gateway, mesh, security]
---

# gw-service-mesh-mtls

Internal traffic should be encrypted and authenticated by workload identity — not by IP allow-lists, shared API keys, or trust of the network. A service mesh (Istio, Linkerd) provides this via sidecar proxies without app code changes.

## Bad — implicit trust of the network

```php
// Payments service allows anyone inside the VPC to call /internal/charge
Route::post('/internal/charge', fn (Request $r) => $this->charge($r->all()));
```

```ts
// Inventory service uses a shared secret in an env var, rotated manually once a year
app.use((req, res, next) => {
  if (req.header('X-Internal-Token') !== process.env.INTERNAL_TOKEN) return res.sendStatus(403);
  next();
});
```

A single compromised pod inside the VPC can call any endpoint.

## Good — Istio PeerAuthentication (strict mTLS everywhere)

```yaml
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata: { name: default, namespace: istio-system }
spec:
  mtls: { mode: STRICT }
```

## Good — Identity-based authorization

```yaml
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata: { name: payments-callers, namespace: prod }
spec:
  selector: { matchLabels: { app: payments } }
  rules:
    - from:
        - source:
            principals:
              - cluster.local/ns/prod/sa/orders        # only orders-service may call
              - cluster.local/ns/prod/sa/refunds       # and refunds-service
      to:
        - operation: { methods: [POST], paths: [/v1/charge, /v1/refund] }
```

Apps need no changes: the sidecar enforces mTLS and authz. When a new service needs to call payments, it's one YAML review, not a secret rotation.
