# Inter-Service Communication

**Impact:** CRITICAL · **Prefix:** `comm-` · **5 rules**

Pick the right shape (sync vs async), contract it, and make consumers idempotent. Everything else — tracing, resilience, versioning — builds on these choices.

## Load When

- Choosing REST, gRPC, GraphQL, Kafka, RabbitMQ, or SQS
- Designing a new API contract (OpenAPI / proto / AsyncAPI)
- Implementing an event consumer
- Reviewing an endpoint that does multi-service orchestration
- Deduplicating retried or replayed messages

## Rules

| Rule | Summary |
|------|---------|
| [`comm-sync-rest-grpc`](../rules/comm-sync-rest-grpc.md) | REST for public / polyglot; gRPC for internal hot paths |
| [`comm-async-messaging`](../rules/comm-async-messaging.md) | Queue long-running / cross-service work via broker |
| [`comm-pubsub-events`](../rules/comm-pubsub-events.md) | Publish domain events; subscribers are decoupled |
| [`comm-idempotent-consumers`](../rules/comm-idempotent-consumers.md) | Dedupe by `event_id` — brokers deliver at-least-once |
| [`comm-api-contracts`](../rules/comm-api-contracts.md) | OpenAPI / proto / AsyncAPI are the source of truth |

## Sync vs Async — Decision Matrix

| Need | Use |
|------|-----|
| Answer in the current request | **Sync** (REST / gRPC) |
| Caller can be decoupled from processing | **Async** (queue / event) |
| Cross-service transaction | **Async saga** — never sync 2PC |
| Fan-out to N subscribers | **Pub/sub** (Kafka topic, SNS+SQS) |
| One worker of a pool picks the job | **Queue** (SQS, RabbitMQ, Laravel queue) |
| Strong ordering required | **Partitioned topic** keyed by aggregate ID |

## Sync — REST vs gRPC

| | REST + JSON | gRPC + protobuf |
|--|--|--|
| Polyglot clients / browsers | ✓ | ✗ (browser needs grpc-web) |
| Wire size & latency | larger | smaller, faster |
| Contract tooling | OpenAPI | `.proto` + codegen |
| Streaming | SSE / WebSocket (awkward) | ✓ bidirectional |
| Typical use | public API, BFF | internal east-west |

## Event Shape

```json
{
  "event_id": "01HXQ...",
  "event_type": "OrderCreated",
  "event_version": 1,
  "aggregate_id": "order_123",
  "occurred_at": "2026-04-15T09:12:34.123Z",
  "correlation_id": "req_abc",
  "causation_id": "cmd_xyz",
  "data": { "order_id": "order_123", "customer_id": "cust_9", "total_cents": 4299 }
}
```

- `event_id` — unique, for idempotency
- `event_version` — schema version; bump when the payload shape changes
- `correlation_id` — ties event back to the originating request
- `causation_id` — the command / event that produced this one

## At-Least-Once Delivery

Every modern broker delivers at-least-once. Consumers **must** be idempotent:
- Dedupe table keyed by `event_id` (or `(consumer_name, event_id)`)
- Or idempotent writes (`INSERT … ON CONFLICT DO NOTHING`, upserts keyed on event id)
- Or version-check: apply event only if `aggregate.version == event.expected_version`

See [`comm-idempotent-consumers`](../rules/comm-idempotent-consumers.md) for code.

## Contract-First Workflow

1. Author `openapi.yaml` / `order.proto` / `asyncapi.yaml` in a shared repo
2. CI validates the spec (spectral, `buf lint`)
3. Codegen produces server stubs + typed clients for PHP **and** TypeScript
4. Breaking changes → new version (same rules as API versioning)
5. Publish specs to a registry (Backstage, Buf Schema Registry, or SwaggerHub)
