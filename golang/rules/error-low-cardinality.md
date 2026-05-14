---
title: Keep Error Messages Low-Cardinality
impact: HIGH
impactDescription: High-cardinality errors fragment APM dashboards and break alerting
tags: error, logging, observability, cardinality, slog, oops
---

## Keep Error Messages Low-Cardinality

**Impact: HIGH — High-cardinality errors fragment APM dashboards and break alerting**

APM and log aggregation tools (Datadog, Loki, Sentry) group errors by their message string. When you interpolate variable data (IDs, file paths, line numbers) into error message strings, every unique combination creates a separate group — dashboards show thousands of one-off errors instead of a single pattern, and alerting on error rate becomes impossible.

Keep error **message** strings static. Attach variable data as **structured attributes**.

## Bad Example

```go
// High cardinality — every user+tenant combo is a unique message group
return fmt.Errorf("user %s not found in tenant %s", userID, tenantID)

// High cardinality — every file+line combo is unique
return fmt.Errorf("error in %s at line %d of the csv", csvPath, line)

// High cardinality — every order ID creates a new group in Sentry
return fmt.Errorf("order %s: payment gateway timeout", orderID)
```

## Good Example

```go
// Static message — all "user not found" events group together
// Variable data as structured attributes at the log boundary:
slog.Error("user not found",
    "user_id", userID,
    "tenant_id", tenantID,
)
return errors.New("user not found")

// Or with samber/oops — attributes travel with the error to wherever it's logged
return oops.
    With("user_id", userID).
    With("tenant_id", tenantID).
    Errorf("user not found")

// CSV parsing — static message, context as attributes
slog.Error("csv parsing failed",
    "csv_path", csvPath,
    "csv_line", line,
    "error", err,
)
return errors.New("csv parsing failed")
```

## What's OK to Include in Message Strings

Static wrapping prefixes are fine — they never change across requests:

```go
// Good — "fetching user" is a constant prefix, doesn't vary per call
return fmt.Errorf("fetching user: %w", err)

// Good — operation names are static
return fmt.Errorf("connecting to payment gateway: %w", err)
```

What to **not** include in the message: IDs, file paths, counts, user input, timestamps, or any value that varies per request.

## stdlib vs samber/oops

The stdlib approach requires you to log attributes at the point where you return the error, which may not have all the context:

```go
// Problem: by the time this error reaches the HTTP handler,
// csvPath and line are out of scope
func parseCSV(path string) error {
    for i, row := range rows {
        if err := validate(row); err != nil {
            return errors.New("csv parsing failed") // lost: path, line number
        }
    }
}
```

`samber/oops` solves this by attaching attributes to the error itself:

```go
func parseCSV(path string) error {
    for i, row := range rows {
        if err := validate(row); err != nil {
            return oops.
                With("csv_path", path).
                With("csv_line", i+1).
                Errorf("csv parsing failed")
            // attributes travel with the error — handler can log them
        }
    }
}
```

## Why

- **Dashboards**: 1 error type = 1 chart line; 10,000 unique messages = unusable dashboard
- **Alerting**: Alert on "csv parsing failed > 10/min", not on 10,000 individual patterns
- **Cost**: Log ingestion is priced per byte/event; duplicate unique messages inflate costs
- **Root cause**: Structured attributes are filterable and searchable in any log tool

Reference: [log/slog](https://pkg.go.dev/log/slog) | [samber/oops](https://github.com/samber/oops) | [12-Factor App: Logs](https://12factor.net/logs) | [Observability reference](../references/observability.md) | [Error Handling reference](../references/error-handling.md)
See also: `golang/references/observability.md` | `golang/references/error-handling.md`
