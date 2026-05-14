---
title: Line Breaking at Semantic Boundaries
impact: MEDIUM
impactDescription: Lines beyond ~120 characters and dense argument lists reduce readability
tags: style, formatting, line-length, arguments
---

## Line Breaking at Semantic Boundaries

**Impact: MEDIUM — Lines beyond ~120 characters and dense argument lists reduce readability**

No rigid column limit, but lines beyond ~120 characters must be broken. Break at **semantic boundaries** (after commas, before operators), not at arbitrary column counts. Functions with 4+ arguments must use one argument per line.

## Bad Example

```go
// Dense argument list — hard to parse which value belongs to which param
result, err := service.CreateOrder(ctx, userID, productID, quantity, shippingAddr, promoCode, notifyByEmail)

// Breaking mid-expression at an arbitrary column
if user.IsAdmin || user.Role == RoleManager ||
user.Permissions.Contains(PermWrite) {
    allow()
}

// Long import block on one line
import ("fmt"; "os"; "strings"; "github.com/example/app/internal/user")
```

## Good Example

```go
// One argument per line for 4+ args — each line has one piece of information
result, err := service.CreateOrder(
    ctx,
    userID,
    productID,
    quantity,
    shippingAddr,
    promoCode,
    notifyByEmail,
)

// Break at logical operator, aligned for readability
if user.IsAdmin ||
    user.Role == RoleManager ||
    user.Permissions.Contains(PermWrite) {
    allow()
}

// Standard import grouping (goimports handles this automatically)
import (
    "fmt"
    "os"
    "strings"

    "github.com/example/app/internal/user"
)
```

## Function Signatures with Many Parameters

When a signature is too long, the real fix is often **fewer parameters**, not better wrapping. Consider an options struct:

```go
// Long signature — sign of too many concerns
func Send(ctx context.Context, to, from, subject, body, replyTo string, attachments [][]byte, priority int) error

// Better — options struct
type SendOptions struct {
    To          string
    From        string
    Subject     string
    Body        string
    ReplyTo     string
    Attachments [][]byte
    Priority    int
}

func Send(ctx context.Context, opts SendOptions) error
```

## Trailing Commas

Always add a trailing comma on the last element of a multi-line list. Go's formatter requires it, and it makes diffs cleaner (adding a new element is a one-line change):

```go
// Good — trailing comma
srv := &http.Server{
    Addr:    ":8080",
    Handler: mux,      // ← trailing comma
}
```

## Why

- **Readability**: One argument per line lets the eye scan arguments vertically, not parse a dense string
- **Diffs**: Each argument on its own line means adding/removing an argument is a one-line diff
- **Review**: Reviewers can comment on individual arguments
- **gofmt enforces**: Trailing commas in multi-line literals are required by the formatter

Reference: [Effective Go — Formatting](https://go.dev/doc/effective_go#formatting) | [gofmt](https://pkg.go.dev/cmd/gofmt) | [Code Style reference](../references/code-style.md)
See also: `golang/references/code-style.md`
