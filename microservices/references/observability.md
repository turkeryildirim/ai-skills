# Observability

**Impact:** HIGH · **Prefix:** `obs-` · **4 rules**

You can't fix what you can't see. Observability = logs + metrics + traces, all joined by a correlation ID, with SLOs to say what "healthy" means.

## Load When

- Bootstrapping a new service's telemetry stack
- Debugging a cross-service latency spike
- Writing a postmortem and needing to reconstruct a request timeline
- Defining SLOs before a launch
- Reviewing whether logs leak PII or tokens

## Rules

| Rule | Summary |
|------|---------|
| [`obs-correlation-ids`](../rules/obs-correlation-ids.md) | `X-Correlation-Id` on every hop; generate if missing |
| [`obs-distributed-tracing`](../rules/obs-distributed-tracing.md) | OpenTelemetry spans across services, brokers, DBs |
| [`obs-structured-logging`](../rules/obs-structured-logging.md) | JSON logs with `service`, `level`, `correlation_id`, `span_id` |
| [`obs-slo-sli`](../rules/obs-slo-sli.md) | Define SLIs, SLOs, and an error budget policy |

## Three Pillars

| Pillar | What it answers | Typical tool |
|--------|-----------------|--------------|
| Logs | "What happened at 09:12:34?" | Loki, CloudWatch, Elastic |
| Metrics | "How often / how fast / how many?" | Prometheus, Datadog |
| Traces | "Where did the latency go?" | Jaeger, Tempo, Honeycomb |

All three **must** share a correlation ID so you can pivot between them.

## Correlation ID Propagation

```
client ── X-Correlation-Id: req_abc ──► gateway
                                          │
                                          ├─ log { correlation_id: req_abc }
                                          ├─ span attrs { correlation_id: req_abc }
                                          └─ X-Correlation-Id: req_abc ──► service A
                                                                             │
                                                                             └─ event { correlation_id: req_abc } ──► broker
                                                                                                                       └─► consumer (same id)
```

If the inbound request has no correlation ID, **generate one** at the edge (gateway) — don't trust clients but don't lose the chain either.

## OpenTelemetry Minimum

Every service ships:
- **Auto-instrumentation** for HTTP server, HTTP client, DB driver, broker client
- **Resource attributes**: `service.name`, `service.version`, `deployment.environment`
- **Span attributes**: `http.route`, `db.system`, `messaging.system`, `correlation_id`
- **Exporter**: OTLP → collector → backend (don't hard-code to a vendor)

## Log Shape

```json
{
  "ts": "2026-04-15T09:12:34.567Z",
  "level": "info",
  "service": "orders-api",
  "env": "prod",
  "correlation_id": "req_abc",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "msg": "order created",
  "order_id": "order_123",
  "customer_id": "cust_9"
}
```

- Never log: passwords, tokens, JWTs, full card numbers, full request bodies
- Redact at the logger layer, not at call sites (too easy to forget)

## SLI → SLO → Error Budget

| Term | Meaning | Example |
|------|---------|---------|
| SLI | measured metric | `successful_requests / total_requests` |
| SLO | target over window | 99.9% over 30 days |
| Error budget | allowed failure | 0.1% × 30d = 43m downtime |
| Policy | what happens when burned | freeze feature work, focus on reliability |

**Good SLIs are user-centric**: success rate, latency p99, freshness of data. Not "CPU %".

## RED + USE

- **RED** (for request-driven services): Rate, Errors, Duration
- **USE** (for resources): Utilization, Saturation, Errors

Dashboard every service with both views.
