# API Gateway & Service Mesh

**Impact:** HIGH · **Prefix:** `gw-` · **3 rules**

Two layers of network control: the **gateway** is the front door (north-south traffic); the **mesh** runs between services (east-west traffic). Don't conflate them — the gateway does auth and routing; the mesh does mTLS, retries, and telemetry for internal traffic.

## Load When

- Choosing / configuring an API gateway (Kong, Envoy, Traefik, AWS API Gateway)
- Deciding whether to adopt a service mesh (Istio, Linkerd)
- Designing a Backend-for-Frontend (BFF)
- Rolling out mTLS between services
- Planning rate-limiting strategy across the fleet

## Rules

| Rule | Summary |
|------|---------|
| [`gw-api-gateway`](../rules/gw-api-gateway.md) | Gateway routes, auths, rate-limits — no business logic |
| [`gw-service-mesh-mtls`](../rules/gw-service-mesh-mtls.md) | Mesh encrypts east-west traffic with mTLS + identity-based authz |
| [`gw-rate-limiting`](../rules/gw-rate-limiting.md) | Per-key, per-endpoint, per-tier; return `429` with `Retry-After` |

## North-South vs East-West

```
  ┌───────────────────────────────────────────────────────┐
  │                    Public Internet                    │
  └──────────────────────┬────────────────────────────────┘
                         │ TLS                 ← north-south
  ┌──────────────────────▼────────────────────────────────┐
  │                   API Gateway                         │
  │  auth · rate-limit · routing · request/response shape │
  └──────────┬──────────────────┬─────────────────────────┘
             │ mTLS             │ mTLS         ← east-west
        ┌────▼─────┐       ┌────▼─────┐
        │ orders   │──mTLS─│ payments │
        └──────────┘       └──────────┘
```

## Gateway Responsibilities

- **TLS termination** and HTTPS redirect
- **AuthN** — validate JWT / API key / OAuth token
- **Rate limiting** — per key, per IP, per endpoint
- **Routing** — path / host → service; blue-green weights
- **Request shaping** — strip internal headers, normalize paths
- **Observability** — access logs, trace injection

## Gateway Anti-Patterns

- ❌ Business logic (fraud scoring, price calculation) in gateway plugins
- ❌ Service-to-service calls routed through the gateway (use mesh or direct)
- ❌ One giant gateway with hundreds of unrelated routes — split per-team or BFF
- ❌ Aggregating responses from 5 backends in a gateway plugin — that's a BFF, build it as a service

## BFF Pattern

A Backend-for-Frontend is a gateway-shaped **service** tuned to one client (web, mobile, partner). It:
- composes calls to downstream services
- shapes responses to match the UI's needs
- owns its own deploy cadence, tied to the client team

One BFF per client, not one BFF per service.

## Service Mesh Checklist

Adopt a mesh when you have **enough services** (≥ ~10) that per-service resilience code is duplicated everywhere. Benefits:

- **mTLS everywhere** without per-app cert wiring
- **Identity-based authz** (SPIFFE / workload identity) — "payments can call ledger, nothing else"
- **Retries / timeouts / circuit breakers** configured declaratively
- **Traffic splitting** for canary / blue-green independent of deploys
- **Uniform telemetry** emitted by sidecars

Costs: sidecar memory / CPU, control-plane ops burden, debugging hidden by the proxy layer.

**Rule of thumb:** < 10 services → skip the mesh, use libraries. > 30 services → almost certainly worth it.

## Rate Limiting Strategy

| Limit | Enforced at | Why |
|-------|-------------|-----|
| Per API key | Gateway | Commercial tiers, abuse prevention |
| Per IP | Gateway / CDN | DoS mitigation |
| Per endpoint | Gateway | Protect expensive routes |
| Per user | Service | Fairness inside a tenant |
| Per tenant | Service / DB | Multi-tenant isolation |

Always return `429` with `Retry-After`, `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.
