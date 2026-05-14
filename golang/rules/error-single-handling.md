---
title: Single Handling Rule — Log OR Return, Never Both
impact: CRITICAL
impactDescription: Dual handling floods logs with duplicates and masks the actual error origin
tags: error, logging, slog, single-handling
---

## Single Handling Rule — Log OR Return, Never Both

**Impact: CRITICAL — Dual handling floods logs with duplicates and masks the actual error origin**

An error must be handled exactly once: either log it at the point of handling, or return it to the caller with added context. Doing both produces duplicate log entries — one at each call-stack frame — making log aggregators noisy and root-cause analysis harder.

## Bad Example

```go
// Logs AND returns — every layer that does this produces a duplicate entry
func chargeCard(orderID string) error {
    err := gateway.Charge(orderID)
    if err != nil {
        log.Printf("gateway charge failed: %v", err)  // logged here
        return fmt.Errorf("charging card: %w", err)   // AND propagated
    }
    return nil
}

func processOrder(orderID string) error {
    err := chargeCard(orderID)
    if err != nil {
        log.Printf("process order failed: %v", err)   // logged AGAIN
        return fmt.Errorf("processing order: %w", err)
    }
    return nil
}
// Result in logs:
// gateway charge failed: connection refused
// process order failed: charging card: connection refused
// ← same event, two lines, two different messages
```

## Good Example

```go
// Internal layers — return with context only
func chargeCard(ctx context.Context, orderID string) error {
    if err := gateway.Charge(ctx, orderID); err != nil {
        return fmt.Errorf("charging card: %w", err)
    }
    return nil
}

func processOrder(ctx context.Context, orderID string) error {
    if err := chargeCard(ctx, orderID); err != nil {
        return fmt.Errorf("processing order %s: %w", orderID, err)
    }
    return nil
}

// Top-level boundary — log once, with full context
func handleOrder(w http.ResponseWriter, r *http.Request) {
    orderID := r.FormValue("id")
    if err := processOrder(r.Context(), orderID); err != nil {
        slog.Error("order failed",
            "error", err,
            "order_id", orderID,
            "request_id", r.Header.Get("X-Request-ID"),
        )
        http.Error(w, "internal error", http.StatusInternalServerError)
        return
    }
    w.WriteHeader(http.StatusOK)
}
// Result in logs:
// order failed  error="processing order abc: charging card: connection refused"  order_id=abc
// ← one entry, full chain, all context
```

## Where the Boundary Is

Log at the **topmost layer** that knows the full context and has a final decision to make:
- HTTP handlers
- Background job runners
- `main()` for CLI commands

All layers below should return errors up the chain. Middleware may log for observability (request logging) but should not suppress the error.

## Why

- **Signal-to-noise**: One error = one log line; operators can count occurrences accurately
- **Aggregation**: APM tools can deduplicate correctly when each event is logged once
- **Traceability**: Full error chain (`processing order: charging card: connection refused`) reads like a stack trace
- **Testability**: Functions that only return errors are easier to unit test

Reference: [Code Review Comments — Error handling](https://github.com/golang/go/wiki/CodeReviewComments#handle-errors) | [samber/oops](https://github.com/samber/oops) | [Error Handling reference](../references/error-handling.md) | [Observability reference](../references/observability.md)
See also: `golang/references/error-handling.md` | `golang/references/observability.md`
