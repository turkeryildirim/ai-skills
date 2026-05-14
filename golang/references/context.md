# Go context.Context

Idiomatic context creation, propagation, cancellation, timeouts, and context values.

## When to Load

- Writing functions that do I/O or spawn goroutines
- Reviewing context propagation across service boundaries
- Working with timeouts, deadlines, or graceful cancellation
- Storing and retrieving request-scoped values (trace IDs, user IDs)

## Core Rules

1. The same context MUST be propagated through the entire request lifecycle: HTTP handler → service → DB → external APIs
2. `ctx` MUST be the first parameter, named `ctx context.Context`
3. NEVER store context in a struct — pass explicitly through function parameters
4. NEVER pass `nil` context — use `context.TODO()` if unsure
5. `cancel()` MUST always be deferred immediately after `WithCancel`/`WithTimeout`/`WithDeadline`
6. `context.Background()` MUST only be used at the top level (main, init, tests)
7. NEVER create a new `context.Background()` in the middle of a request path
8. Context value keys MUST be unexported types to prevent collisions
9. Context values MUST only carry request-scoped metadata — NEVER use them as function parameters
10. Use `context.WithoutCancel` (Go 1.21+) when spawning background work that must outlive the parent request

## When to Use Each Context

| Situation | Use |
|---|---|
| Entry point (main, init, test) | `context.Background()` |
| Function needs context but caller doesn't provide one yet | `context.TODO()` |
| Inside an HTTP handler | `r.Context()` |
| Need cancellation control | `context.WithCancel(parentCtx)` |
| Need a timeout | `context.WithTimeout(parentCtx, duration)` |
| Need a deadline | `context.WithDeadline(parentCtx, t)` |
| Background work that must outlive request | `context.WithoutCancel(ctx)` |

## Context Propagation

The most important rule: **propagate the same context through the entire call chain**. Cancelling the parent cancels all downstream work automatically.

```go
// Bad — creates a new context, breaking the chain
func (s *OrderService) Create(ctx context.Context, order Order) error {
    return s.db.ExecContext(context.Background(), // breaks propagation
        "INSERT INTO orders ...", order.ID)
}

// Good — propagates the caller's context
func (s *OrderService) Create(ctx context.Context, order Order) error {
    return s.db.ExecContext(ctx, "INSERT INTO orders ...", order.ID)
}
```

## Cancellation and Timeouts

```go
// WithCancel — manual cancellation
ctx, cancel := context.WithCancel(parentCtx)
defer cancel() // always defer cancel immediately

// WithTimeout — automatic cancellation after duration
ctx, cancel := context.WithTimeout(parentCtx, 5*time.Second)
defer cancel()

// WithDeadline — cancel at absolute time
deadline := time.Now().Add(10 * time.Second)
ctx, cancel := context.WithDeadline(parentCtx, deadline)
defer cancel()
```

Checking for cancellation in a goroutine:

```go
func processItems(ctx context.Context, items []Item) error {
    for _, item := range items {
        select {
        case <-ctx.Done():
            return ctx.Err() // propagate cancellation reason
        default:
        }
        if err := processItem(ctx, item); err != nil {
            return fmt.Errorf("processing item %s: %w", item.ID, err)
        }
    }
    return nil
}
```

### Background work that must outlive the request

```go
// WithoutCancel (Go 1.21+) — preserves values but removes cancellation
func (s *AuditService) LogAction(ctx context.Context, action Action) {
    // audit log must complete even if request was cancelled
    bgCtx := context.WithoutCancel(ctx) // inherits trace IDs, not cancellation
    go func() {
        if err := s.db.InsertAudit(bgCtx, action); err != nil {
            slog.ErrorContext(bgCtx, "audit write failed", "error", err)
        }
    }()
}
```

## Context Values

Use unexported key types to prevent collisions between packages:

```go
// Good — unexported key type prevents collision
type contextKey string

const (
    requestIDKey contextKey = "requestID"
    userIDKey    contextKey = "userID"
)

func WithRequestID(ctx context.Context, id string) context.Context {
    return context.WithValue(ctx, requestIDKey, id)
}

func RequestIDFromContext(ctx context.Context) (string, bool) {
    id, ok := ctx.Value(requestIDKey).(string)
    return id, ok
}
```

```go
// Bad — string key, easy collision between packages
ctx = context.WithValue(ctx, "userID", id)  // any package can collide
```

### What belongs in context values

| Belongs in context | Does NOT belong in context |
|---|---|
| Request ID / Trace ID | Business logic parameters |
| Authenticated user ID | Database handles |
| Tenant / organization ID | Optional function parameters |
| Locale / timezone | Configuration |

Context values are for metadata that crosses many layers. If you're passing the value to only one or two functions, use a parameter instead.

## HTTP Server Context Patterns

```go
// HTTP middleware — inject request ID into context
func RequestIDMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        id := r.Header.Get("X-Request-ID")
        if id == "" {
            id = uuid.New().String()
        }
        ctx := WithRequestID(r.Context(), id)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

// Handler — use r.Context(), not context.Background()
func (h *Handler) CreateUser(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context() // carries request ID, trace, deadline, etc.

    user, err := h.svc.CreateUser(ctx, req)
    if err != nil {
        // ...
    }
}
```

## HTTP Client with Context

```go
// Always create requests with context
req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
if err != nil {
    return fmt.Errorf("creating request: %w", err)
}

resp, err := client.Do(req)
if err != nil {
    if errors.Is(err, context.DeadlineExceeded) {
        return fmt.Errorf("request to %s timed out: %w", url, err)
    }
    return fmt.Errorf("request to %s: %w", url, err)
}
defer resp.Body.Close()
```

## AfterFunc — Callback on Cancellation (Go 1.21+)

```go
// Run a function when the context is cancelled
stop := context.AfterFunc(ctx, func() {
    // called in its own goroutine when ctx is Done
    slog.Info("context cancelled, cleaning up")
    cleanup()
})
defer stop() // prevent the callback if we finish before cancellation
```

## Context in Tests

```go
// Use context.Background() in tests — they are top-level
func TestCreateUser(t *testing.T) {
    ctx := context.Background()
    // or with timeout for safety:
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    // Go 1.24+: t.Context() — cancelled when the test ends
    ctx := t.Context()
}
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Storing context in a struct | Pass via function parameter — context is per-request, not per-object |
| `context.Background()` inside a handler | Use `r.Context()` — it carries the request deadline |
| Not deferring `cancel()` | Context leak; goroutines waiting on `Done()` never unblock |
| `context.WithValue` with a `string` key | Use unexported type to prevent cross-package collisions |
| Passing context to goroutines without `WithoutCancel` | Background goroutine cancelled when parent request finishes |
| Using context values as function parameters | Breaks function signatures — values in context are invisible to callers |

## References

- [context package](https://pkg.go.dev/context)
- [Go Concurrency Patterns: Context](https://go.dev/blog/context)
- [Go 1.21 — context.WithoutCancel, context.AfterFunc](https://go.dev/doc/go1.21)
