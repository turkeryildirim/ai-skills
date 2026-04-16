# Resilience

**Impact:** CRITICAL · **Prefix:** `resil-` · **5 rules**

Every remote call will fail eventually. Resilience is the set of defaults that turn a partial outage into a degraded experience instead of a cascading failure.

## Load When

- Adding a new outbound HTTP / gRPC call
- Reviewing an incident where one slow dependency took down the fleet
- Hardening a queue consumer against flapping downstreams
- Deciding retry policy for a payment / third-party API
- Designing a fallback path for a non-critical feature

## Rules

| Rule | Summary |
|------|---------|
| [`resil-circuit-breaker`](../rules/resil-circuit-breaker.md) | Stop calling a failing dependency; fail fast; half-open to probe |
| [`resil-retry-backoff`](../rules/resil-retry-backoff.md) | Exponential backoff + jitter; bounded attempts; only retry idempotent ops |
| [`resil-timeouts`](../rules/resil-timeouts.md) | Every outbound call has an explicit timeout shorter than upstream |
| [`resil-bulkhead`](../rules/resil-bulkhead.md) | Isolate resources (thread pools, connection pools) per dependency |
| [`resil-graceful-degradation`](../rules/resil-graceful-degradation.md) | Serve reduced feature set when a dependency is down |

## The Four Horsemen of Cascading Failure

1. **No timeout** — one slow call saturates your workers
2. **Unbounded retries** — amplify load on an already-struggling dependency
3. **No isolation** — one dependency's pool exhaustion starves healthy paths
4. **No fallback** — partial outage becomes total outage

## Timeout Budget

Timeouts must get **tighter** as you go deeper. If the client has a 5s budget:

```
client (5s) → gateway (4.5s) → service A (3s) → service B (1.5s) → DB (500ms)
```

Leave headroom at each hop for processing + retries. A timeout equal to the parent's is a bug.

## Retry Policy Matrix

| Operation | Retry? | Notes |
|-----------|:-----:|------|
| GET / HEAD | ✓ | safe, idempotent |
| PUT / DELETE | ✓ | idempotent by spec |
| POST without `Idempotency-Key` | ✗ | may double-charge |
| POST with `Idempotency-Key` | ✓ | server dedupes |
| Queue consumer | ✓ | broker redelivers; use dedup table |

**Backoff:** `min(cap, base * 2^attempt) + random(0, jitter)` — always with jitter.

## Circuit Breaker States

```
CLOSED  ── failures > threshold ──►  OPEN
  ▲                                    │
  │                                    │ cooldown
  │                                    ▼
  └────── success ──── HALF_OPEN ◄─────┘
                (1 probe request)
```

- **CLOSED** — normal, counting failures in a sliding window
- **OPEN** — short-circuit instantly; emit metric; fallback if configured
- **HALF_OPEN** — allow one request; success → CLOSED, failure → OPEN

## Bulkheads

Separate connection pools, goroutine/thread limits, or semaphores per dependency so one bad neighbour can't starve the others.

```
orders service
├─ http-pool(payments)    max 20 concurrent
├─ http-pool(inventory)   max 20 concurrent
└─ http-pool(recommender) max  5 concurrent   ← non-critical, capped
```

## Fallback Ladder (pick the highest that's safe)

1. **Cached response** — last-known-good from Redis
2. **Static default** — empty recommendations, default feature flags
3. **Queued write** — accept the request, process when dep recovers
4. **Explicit error** — `503 Service Unavailable` with `Retry-After`

Never silently swallow errors — always log + emit a metric.
