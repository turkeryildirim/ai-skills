---
title: Propagate Context and Respect Cancellation
impact: CRITICAL
impactDescription: Ignoring context leaks resources and blocks graceful shutdown
tags: concurrency, context, cancellation, timeout
---

## Propagate Context and Respect Cancellation

**Impact: CRITICAL — Ignoring context leaks resources and blocks graceful shutdown**

Pass `context.Context` as the first parameter to every function that does I/O or long-running work. Check `ctx.Done()` in loops and selects so the function exits promptly when its caller cancels or times out.

## Bad Example

```go
// No context — cannot be cancelled
func fetchUser(id int) (*User, error) {
    resp, err := http.Get(fmt.Sprintf("https://api.example.com/users/%d", id))
    // If the request hangs, there is no way to stop it.
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    // ...
}

// Context passed but never used
func processItems(ctx context.Context, items []Item) error {
    for _, item := range items {
        process(item) // ignores ctx — loop runs even after cancellation
    }
    return nil
}
```

## Good Example

```go
// Context as first parameter; used in HTTP call
func fetchUser(ctx context.Context, id int) (*User, error) {
    req, err := http.NewRequestWithContext(ctx, http.MethodGet,
        fmt.Sprintf("https://api.example.com/users/%d", id), nil)
    if err != nil {
        return nil, fmt.Errorf("fetchUser: build request: %w", err)
    }

    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return nil, fmt.Errorf("fetchUser: do request: %w", err)
    }
    defer resp.Body.Close()
    // ...
}

// Context checked in loop
func processItems(ctx context.Context, items []Item) error {
    for _, item := range items {
        if err := ctx.Err(); err != nil {
            return fmt.Errorf("processItems: cancelled: %w", err)
        }
        if err := process(ctx, item); err != nil {
            return fmt.Errorf("processItems: item %v: %w", item.ID, err)
        }
    }
    return nil
}
```

## Rules

1. `context.Context` is always the **first** parameter, named `ctx`
2. **Never** store `ctx` in a struct field
3. Use `context.Background()` at the top of `main` and test setup; `context.TODO()` as a placeholder
4. Pass `ctx` down — never create a fresh context mid-call-chain unless creating a child with timeout
5. Use `http.NewRequestWithContext(ctx, ...)` not `http.NewRequest`

## Why

- **Graceful shutdown**: Services drain in-flight requests on SIGTERM — only works if ctx is propagated
- **Timeout enforcement**: A deadline set at the HTTP handler only works if passed to downstream calls
- **Resource cleanup**: Cancelled DB queries release connections sooner
- **Observability**: Tracing libraries (OpenTelemetry) attach spans to the context

Reference: [context package](https://pkg.go.dev/context) | [Go Blog: Contexts and structs](https://go.dev/blog/context-and-structs) | [Context reference](../references/context.md) | [Concurrency reference](../references/concurrency.md)
See also: `golang/references/context.md` | `golang/references/concurrency.md`
