---
title: Wrap Errors with Context
impact: CRITICAL
impactDescription: Preserves error chain and adds actionable context for debugging
tags: error, wrapping, fmt.Errorf
---

## Wrap Errors with Context

**Impact: CRITICAL — Preserves error chain and adds actionable context for debugging**

Always wrap errors with `fmt.Errorf("context: %w", err)` before returning them up the call stack. This adds the operation context while preserving the original error for `errors.Is` / `errors.As` inspection.

## Bad Example

```go
func loadUser(id int) (*User, error) {
    row := db.QueryRow("SELECT * FROM users WHERE id = ?", id)
    var u User
    if err := row.Scan(&u.ID, &u.Name); err != nil {
        return nil, err  // no context: caller sees "sql: no rows" with no hint where
    }
    return &u, nil
}
```

## Good Example

```go
func loadUser(ctx context.Context, id int) (*User, error) {
    row := db.QueryRowContext(ctx, "SELECT * FROM users WHERE id = $1", id)
    var u User
    if err := row.Scan(&u.ID, &u.Name); err != nil {
        return nil, fmt.Errorf("loadUser id=%d: %w", id, err)
        // caller sees: "loadUser id=42: sql: no rows in result set"
    }
    return &u, nil
}
```

## Why

- **Debugging**: Error messages read like a stack trace — `getUserPrefs: loadUser id=42: sql: no rows`
- **`errors.Is` / `errors.As`**: `%w` keeps the original error unwrappable
- **Context**: Adds operation-specific data (IDs, paths) that plain `err` drops
- **Convention**: Prefix with the function name, e.g. `"funcName: "`

Reference: [Working with Errors in Go 1.13](https://go.dev/blog/go1.13-errors) | [fmt.Errorf](https://pkg.go.dev/fmt#Errorf) | [Error Handling reference](../references/error-handling.md)
See also: `golang/references/error-handling.md`
