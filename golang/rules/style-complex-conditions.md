---
title: Extract Complex Conditions into Named Booleans
impact: HIGH
impactDescription: Named booleans make business rules visible and conditions scannable
tags: style, control-flow, readability, conditions
---

## Extract Complex Conditions into Named Booleans

**Impact: HIGH — Named booleans make business rules visible and conditions scannable**

When an `if` condition has 3 or more operands, extract each sub-condition into a named boolean. The name documents the intent; the `if` line becomes a plain-English policy statement.

Keep expensive sub-expressions inline in the condition for short-circuit benefit, but otherwise extract for readability.

## Bad Example

```go
// Wall of conditions — hides business logic, hard to modify
if user.Role == RoleAdmin || resource.OwnerID == user.ID ||
    (resource.IsPublic && user.IsVerified) || permissions.Contains(PermOverride) {
    allow()
}

// Mixed levels of abstraction
if order.Status == StatusPending && order.CreatedAt.Before(cutoff) &&
    !order.IsFlagged && len(order.Items) > 0 && order.TotalCents >= MinOrderCents {
    processOrder(order)
}
```

## Good Example

```go
// Named booleans — each sub-condition is a business concept
isAdmin          := user.Role == RoleAdmin
isOwner          := resource.OwnerID == user.ID
isPublicVerified := resource.IsPublic && user.IsVerified
hasOverride      := permissions.Contains(PermOverride)

if isAdmin || isOwner || isPublicVerified || hasOverride {
    allow()
}

// Order eligibility — reads like a spec
isPending    := order.Status == StatusPending
isRecent     := order.CreatedAt.After(cutoff)
isClean      := !order.IsFlagged
hasItems     := len(order.Items) > 0
meetsMinimum := order.TotalCents >= MinOrderCents

if isPending && isRecent && isClean && hasItems && meetsMinimum {
    processOrder(order)
}
```

## Scope Variables to if Blocks When Appropriate

When the variable is only needed for the condition, use the `if` init statement:

```go
if err := validate(input); err != nil {
    return err
}
```

## When Not to Extract

- Short, obvious 2-operand conditions: `if x > 0 && y > 0` — extraction would add noise
- Short-circuit-dependent expensive calls: keep them in the condition so they're skipped when not needed

## Why

- **Readability**: The `if` line reads like a policy, not an expression soup
- **Debuggability**: Named booleans can be logged or inspected individually
- **Maintainability**: Adding or removing a condition is a clean one-line change
- **Documentation**: The name replaces a comment explaining what the condition means

Reference: [Uber Go Style Guide — Reduce Scope of Variables](https://github.com/uber-go/guide/blob/master/style.md) | [Code Style reference](../references/code-style.md)
See also: `golang/references/code-style.md`
