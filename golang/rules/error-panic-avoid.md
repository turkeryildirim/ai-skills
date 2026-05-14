---
title: Avoid panic for Expected Errors
impact: CRITICAL
impactDescription: panic crashes the entire process; use error returns for recoverable failures
tags: error, panic, recover, idiomatic
---

## Avoid panic for Expected Errors

**Impact: CRITICAL — panic crashes the entire process; use error returns for recoverable failures**

Reserve `panic` for programmer errors (invariant violations that should never happen). For all expected failure conditions — network errors, invalid input, missing files — return an `error` value.

## Bad Example

```go
func getUser(id int) *User {
    if id <= 0 {
        panic("invalid user ID") // crashes the whole server for bad input
    }

    u, err := db.FindUser(id)
    if err != nil {
        panic(err) // bad: propagated to caller as a crash, not an error
    }
    return u
}
```

## Good Example

```go
func getUser(ctx context.Context, id int) (*User, error) {
    if id <= 0 {
        return nil, fmt.Errorf("getUser: id must be positive, got %d", id)
    }

    u, err := db.FindUser(ctx, id)
    if err != nil {
        return nil, fmt.Errorf("getUser id=%d: %w", id, err)
    }
    return u, nil
}
```

## When panic IS Acceptable

```go
// 1. Package-level init — configuration that must be valid at startup
var compiled = regexp.MustCompile(`^\d{4}-\d{2}-\d{2}$`) // panics at init if invalid

// 2. Invariant violations that indicate programmer error
func (s *Stack) Pop() any {
    if s.Len() == 0 {
        panic("stack: Pop called on empty stack") // this is a bug, not a runtime error
    }
    // ...
}
```

## Why

- **Availability**: A `panic` in a goroutine crashes the whole program unless recovered
- **HTTP handlers**: The `net/http` server recovers panics in handlers, but other code does not
- **Error contract**: Callers expect errors they can handle; panics are invisible in function signatures
- **Testing**: Panicking code is hard to test — error returns are easy

Reference: [Effective Go — Panic](https://go.dev/doc/effective_go#panic) | [Code Review Comments — Don't panic](https://github.com/golang/go/wiki/CodeReviewComments#dont-panic) | [Error Handling reference](../references/error-handling.md) | [Design Patterns reference](../references/design-patterns.md)
See also: `golang/references/error-handling.md` | `golang/references/design-patterns.md`
