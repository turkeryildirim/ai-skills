---
name: microservices
description: Microservices architecture patterns for PHP (Laravel/Symfony) and TypeScript (NestJS/Express) — service decomposition, DDD bounded contexts, sync/async communication, saga and event sourcing, resilience (circuit breaker, retry, bulkhead, timeout), observability (correlation IDs, distributed tracing, SLO), deployment (health probes, graceful shutdown), API gateway, and service mesh. Use when decomposing monoliths, designing new distributed systems, reviewing service boundaries, implementing inter-service communication, or hardening an existing microservice.
license: MIT
metadata:
  author: consolidated (Jeffallan/microservices-architect, VoltAgent/microservices-architect, wshobson/microservices-patterns)
  version: "1.0.0"
  languages: [PHP 8.3+, TypeScript 5.x]
  frameworks: [Laravel 13, Symfony 7, NestJS 10, Express 4]
  ruleCount: 29
  categoryCount: 7
---

# Microservices

Distributed-system patterns for PHP and TypeScript services. Every rule file includes bad / good examples in **both** languages. Per-category guides live in `references/`.

## When to Use

- Decomposing a monolith into independently deployable services
- Designing service boundaries, data ownership, and API contracts
- Choosing between synchronous (REST, gRPC) and asynchronous (Kafka, RabbitMQ, SQS) communication
- Implementing distributed transactions (saga), event sourcing, or CQRS
- Hardening resilience: circuit breakers, retries, timeouts, bulkheads, fallbacks
- Wiring observability: correlation IDs, distributed tracing, structured logs, SLI / SLO
- Setting up health probes, graceful shutdown, externalised config
- Designing API gateways or enrolling services into a service mesh (Istio, Linkerd)

## Basic Coverage

```
Service   ─── owns its own DB schema ─────────►  no cross-service SQL / shared tables
          ◄── API contract (OpenAPI / proto) ──  consumers depend on the contract, not the impl
Sync call ─── REST / gRPC with timeout ───────►  circuit-breaker + retry(exp-backoff) + deadline
Async     ─── publish DomainEvent to broker ──►  subscribers react; producer never awaits
Saga      ─── step + compensating action ─────►  eventual consistency, idempotent steps
Request   ─── X-Correlation-Id propagates ────►  every log + span tagged with it
Pod       ─── /health/live + /health/ready ───►  k8s probes gate traffic and restarts
Deploy    ─── config via env / secret ────────►  rebuild image only for code changes
```

## Core Directives

### MUST DO

- One service owns one business capability (bounded context) — single responsibility
- Each service owns its own database schema — **no cross-service reads or joins**
- Every external call has an explicit `timeout`, a bounded `retry budget`, and a `fallback`
- Every inbound request carries (or is assigned) a correlation ID that propagates to outbound calls, logs, and traces
- Health endpoints distinguish **liveness** (am I alive) from **readiness** (can I serve traffic)
- Consumers of async events are **idempotent** — deduplicate by `event_id` or aggregate version
- Define API contracts **first** (OpenAPI, protobuf, AsyncAPI) — generate types / clients from them
- Externalise all config (env vars, secret manager) — the same artifact runs in every environment
- Ship structured logs (JSON) with `service`, `correlation_id`, `span_id`, `level`
- Shutdown gracefully: stop accepting new work → drain in-flight → flush consumers → exit

### MUST NOT DO

- Share a database schema between services
- Call another service without a timeout (defaults are almost always too high)
- Use distributed two-phase commit / XA across services — use sagas
- Retry non-idempotent POSTs without an `Idempotency-Key`
- Emit domain events whose shape depends on internal DB columns — events are a public contract
- Log secrets, tokens, JWTs, or full request bodies — redact first
- Couple services to each other's deployment cadence (synchronous deploy dependencies)
- Put business logic in the API gateway — it routes, auths, and rate-limits, nothing more

## Category Index — When to Load Which Reference

| # | Category | Impact | Load when… | Reference | Prefix | Rules |
|--:|----------|:------:|------------|-----------|--------|:-----:|
| 1 | Service Boundaries & Decomposition | CRITICAL | Splitting a monolith, drawing service boundaries, deciding data ownership | [`references/boundaries.md`](references/boundaries.md) | `boundary-` | 4 |
| 2 | Inter-Service Communication | CRITICAL | Choosing sync vs async, REST / gRPC / Kafka / RabbitMQ, contracts | [`references/communication.md`](references/communication.md) | `comm-` | 5 |
| 3 | Data Management | CRITICAL | Saga vs 2PC, event sourcing, CQRS, eventual consistency | [`references/data.md`](references/data.md) | `data-` | 4 |
| 4 | Resilience | CRITICAL | Adding circuit breakers, retries, bulkheads, timeouts, fallbacks | [`references/resilience.md`](references/resilience.md) | `resil-` | 5 |
| 5 | Observability | HIGH | Correlation IDs, tracing, structured logs, SLI / SLO | [`references/observability.md`](references/observability.md) | `obs-` | 4 |
| 6 | Deployment & Operations | HIGH | Health probes, graceful shutdown, config, zero-downtime rollouts | [`references/operations.md`](references/operations.md) | `ops-` | 4 |
| 7 | API Gateway & Service Mesh | HIGH | BFF / gateway design, mTLS, traffic splitting, mesh policies | [`references/gateway-mesh.md`](references/gateway-mesh.md) | `gw-` | 3 |

Load only the reference(s) relevant to the current task — not all seven.

## Rule Index — Direct Jumps

Each `rules/<name>.md` has: frontmatter (title, impact, tags), rationale, **bad example** (PHP + TS), **good example** (PHP + TS).

### 1. Boundaries (`boundary-`) — CRITICAL
[`boundary-ddd-bounded-contexts`](rules/boundary-ddd-bounded-contexts.md) · [`boundary-database-per-service`](rules/boundary-database-per-service.md) · [`boundary-single-responsibility`](rules/boundary-single-responsibility.md) · [`boundary-strangler-fig`](rules/boundary-strangler-fig.md)

### 2. Communication (`comm-`) — CRITICAL
[`comm-sync-rest-grpc`](rules/comm-sync-rest-grpc.md) · [`comm-async-messaging`](rules/comm-async-messaging.md) · [`comm-pubsub-events`](rules/comm-pubsub-events.md) · [`comm-idempotent-consumers`](rules/comm-idempotent-consumers.md) · [`comm-api-contracts`](rules/comm-api-contracts.md)

### 3. Data (`data-`) — CRITICAL
[`data-saga-orchestration`](rules/data-saga-orchestration.md) · [`data-saga-choreography`](rules/data-saga-choreography.md) · [`data-event-sourcing`](rules/data-event-sourcing.md) · [`data-cqrs`](rules/data-cqrs.md)

### 4. Resilience (`resil-`) — CRITICAL
[`resil-circuit-breaker`](rules/resil-circuit-breaker.md) · [`resil-retry-backoff`](rules/resil-retry-backoff.md) · [`resil-timeouts`](rules/resil-timeouts.md) · [`resil-bulkhead`](rules/resil-bulkhead.md) · [`resil-graceful-degradation`](rules/resil-graceful-degradation.md)

### 5. Observability (`obs-`) — HIGH
[`obs-correlation-ids`](rules/obs-correlation-ids.md) · [`obs-distributed-tracing`](rules/obs-distributed-tracing.md) · [`obs-structured-logging`](rules/obs-structured-logging.md) · [`obs-slo-sli`](rules/obs-slo-sli.md)

### 6. Operations (`ops-`) — HIGH
[`ops-health-probes`](rules/ops-health-probes.md) · [`ops-graceful-shutdown`](rules/ops-graceful-shutdown.md) · [`ops-config-externalization`](rules/ops-config-externalization.md) · [`ops-zero-downtime-deploys`](rules/ops-zero-downtime-deploys.md)

### 7. Gateway & Mesh (`gw-`) — HIGH
[`gw-api-gateway`](rules/gw-api-gateway.md) · [`gw-service-mesh-mtls`](rules/gw-service-mesh-mtls.md) · [`gw-rate-limiting`](rules/gw-rate-limiting.md)

## Target Stacks

| Concern | PHP suggestion | TypeScript suggestion |
|---------|---------------|----------------------|
| HTTP framework | Laravel 13, Symfony 7, Slim 4 | NestJS 10, Fastify, Express 4 |
| Async broker | Laravel queues (Redis/SQS), Symfony Messenger, php-amqplib | @nestjs/microservices, kafkajs, amqplib, bullmq |
| RPC | spiral/roadrunner-grpc, google/protobuf | `@grpc/grpc-js`, `ts-proto` |
| Circuit breaker | `ackintosh/ganesha` | `opossum`, `cockatiel` |
| Tracing | OpenTelemetry PHP SDK | `@opentelemetry/sdk-node` |
| Service mesh | Istio / Linkerd (language-agnostic) | Istio / Linkerd |
| Orchestrator | Kubernetes | Kubernetes |

## Validation Checklist (Architecture Review)

Use this before calling an architecture "done":

- [ ] Each service has a single owning team and a single bounded context
- [ ] No service reads or writes another service's database
- [ ] API contracts exist as machine-readable artifacts (OpenAPI, proto, AsyncAPI)
- [ ] Every outbound call has a timeout < upstream's timeout (with budget)
- [ ] Every outbound call has a circuit breaker or explicit fallback
- [ ] Every async consumer is idempotent (dedup by `event_id`)
- [ ] `X-Correlation-Id` propagates through sync and async hops
- [ ] `/health/live` and `/health/ready` exist and differ
- [ ] Graceful shutdown drains connections before SIGTERM grace expires
- [ ] All config is externalised; no environment-specific code branches
- [ ] Distributed traces span at least: ingress → service → outbound → broker → consumer
- [ ] SLOs defined; error budget policy agreed with product
- [ ] Rollout is canary / blue-green capable; rollback is automated

## External References

- [Microservices.io patterns](https://microservices.io/patterns/index.html)
- [Domain-Driven Design Reference, Eric Evans](https://www.domainlanguage.com/ddd/reference/)
- [Google SRE Book — SLOs](https://sre.google/sre-book/service-level-objectives/)
- [OpenTelemetry](https://opentelemetry.io)
- [CNCF Cloud Native Landscape](https://landscape.cncf.io)
- [AsyncAPI Specification](https://www.asyncapi.com/docs)
