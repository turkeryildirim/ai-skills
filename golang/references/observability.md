# Go Observability

Structured logging with slog, Prometheus metrics, OpenTelemetry tracing, pprof profiling, and production-ready instrumentation.

## When to Load

- Instrumenting a service for production monitoring
- Setting up structured logging
- Adding metrics or tracing to new features
- Migrating from zap/logrus/zerolog to slog
- Correlating logs with traces

## The Five Signals

| Signal | Question answered | Tool |
|---|---|---|
| **Logs** | What happened? | `log/slog` |
| **Metrics** | How much / how fast? | Prometheus client |
| **Traces** | Where did time go? | OpenTelemetry |
| **Profiles** | Why is it slow / using memory? | pprof, Pyroscope |
| **RUM** | How do users experience it? | PostHog, Segment |

## Best Practices Summary

1. **Use `log/slog`** — standard library since Go 1.21; stop adding zap/logrus/zerolog
2. **Structured logging always** — JSON in production, human-readable in dev
3. **Log OR return errors, never both** — see `error-single-handling` rule
4. **Low-cardinality Prometheus labels** — NEVER use user IDs or full URLs as label values
5. **Histogram over Summary** for latency — supports server-side aggregation and `histogram_quantile()`
6. **Context everywhere** — use `slog.InfoContext(ctx, ...)` to correlate logs with traces
7. **A feature is not done until it is observable** — metrics, logs, spans before shipping

## Structured Logging with slog

```go
import "log/slog"

// Setup — JSON handler for production
logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
}))
slog.SetDefault(logger)

// Structured logging — key-value pairs
slog.Info("user logged in",
    "user_id", userID,
    "ip", r.RemoteAddr,
)

slog.Error("payment failed",
    "error", err,
    "order_id", orderID,
    "amount_cents", amount,
)

// Context-aware — injects trace_id/span_id when OpenTelemetry is configured
slog.InfoContext(ctx, "order created", "order_id", orderID)
```

### Log Levels

| Level | When to use |
|---|---|
| `Debug` | Development only — high volume, suppressed in production |
| `Info` | Normal operations — service start, requests, key events |
| `Warn` | Degraded state — retrying, fallback used, approaching limit |
| `Error` | Failure requiring attention — errors logged at the top level |

### Migrating from Third-Party Loggers

```go
// Use bridge handlers during migration — routes slog through existing logger
import "github.com/samber/slog-zap/v2"

logger := slog.New(slogzap.Option{Logger: zapLogger}.NewZapHandler())
slog.SetDefault(logger)

// Then gradually replace: zap.L().Info(...) → slog.Info(...)
// Once complete, remove the bridge and zap dependency
```

## Prometheus Metrics

```go
import "github.com/prometheus/client_golang/prometheus"

// Counter — rate of change (requests, errors, processed items)
var requestsTotal = prometheus.NewCounterVec(
    prometheus.CounterOpts{
        Name: "http_requests_total",
        Help: "Total HTTP requests",
    },
    []string{"method", "route", "status"},
)

// Histogram — latency distribution (use this, not Summary)
var requestDuration = prometheus.NewHistogramVec(
    prometheus.HistogramOpts{
        Name:    "http_request_duration_seconds",
        Help:    "HTTP request latency",
        Buckets: prometheus.DefBuckets,
    },
    []string{"method", "route"},
)

// Gauge — current value (connections, queue depth, in-flight requests)
var activeConnections = prometheus.NewGauge(
    prometheus.GaugeOpts{
        Name: "active_connections",
        Help: "Current active connections",
    },
)
```

**High-cardinality label danger:**
```go
// Bad — every user ID is a unique label value → OOM
httpRequests.WithLabelValues(r.Method, r.URL.Path, userID).Inc()

// Good — bounded values only
httpRequests.WithLabelValues(r.Method, routePattern, strconv.Itoa(status)).Inc()
```

## OpenTelemetry Tracing

```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/codes"
)

var tracer = otel.Tracer("my-service")

func (s *OrderService) Create(ctx context.Context, order Order) error {
    ctx, span := tracer.Start(ctx, "OrderService.Create")
    defer span.End()

    span.SetAttributes(
        attribute.String("order.id", order.ID),
        attribute.Int("order.items", len(order.Items)),
    )

    if err := s.db.Insert(ctx, order); err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, err.Error())
        return fmt.Errorf("inserting order: %w", err)
    }

    return nil
}
```

### Correlate Logs with Traces

```go
// otelslog bridge — automatically injects trace_id and span_id into logs
import "go.opentelemetry.io/contrib/bridges/otelslog"

logger := otelslog.NewHandler("my-service")
slog.SetDefault(slog.New(logger))

// Now every slog call with context includes trace correlation
slog.InfoContext(ctx, "order created", "order_id", orderID)
// → {"trace_id":"abc123", "span_id":"def456", "msg":"order created", ...}
```

## pprof Profiling

```go
import _ "net/http/pprof"

// Expose profiling endpoints (protect with auth in production!)
go func() {
    log.Println(http.ListenAndServe("localhost:6060", nil))
}()
```

```bash
# CPU profile
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

# Memory profile
go tool pprof http://localhost:6060/debug/pprof/heap

# Goroutine profile
go tool pprof http://localhost:6060/debug/pprof/goroutine
```

## Definition of Done for Observability

Before shipping a feature:

- [ ] **Metrics declared** — counters for operations/errors, histograms for latencies
- [ ] **Logging structured** — key-value pairs with `slog`, context variants, no PII
- [ ] **Spans created** — service methods, DB queries, external calls
- [ ] **Errors handled once** — logged OR returned, never both
- [ ] **No high-cardinality labels** in Prometheus

## Common Mistakes

```go
// Bad — log AND return (duplicate noise in log aggregators)
if err != nil {
    slog.Error("query failed", "error", err)
    return fmt.Errorf("query: %w", err)
}

// Bad — high-cardinality Prometheus label
httpRequests.WithLabelValues(userID).Inc()

// Bad — Summary for latency (not aggregatable across instances)
prometheus.NewSummary(...)

// Bad — context not passed (breaks trace propagation)
result, err := db.Query("SELECT ...")

// Good — context flows through
result, err := db.QueryContext(ctx, "SELECT ...")
```

## References

- [log/slog](https://pkg.go.dev/log/slog)
- [Prometheus Go client](https://github.com/prometheus/client_golang)
- [OpenTelemetry Go](https://opentelemetry.io/docs/languages/go/)
- [awesome-prometheus-alerts](https://samber.github.io/awesome-prometheus-alerts/)
- [samber/slog-*](https://github.com/samber/slog-multi)
