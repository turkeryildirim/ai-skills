---
title: Early Return — Handle Errors and Edge Cases First
impact: HIGH
impactDescription: Keeps the happy path at minimal indentation; reduces cognitive load
tags: style, control-flow, early-return, guard-clause
---

## Early Return — Handle Errors and Edge Cases First

**Impact: HIGH — Keeps the happy path at minimal indentation; reduces cognitive load**

Handle errors, invalid inputs, and edge cases at the top of a function and return immediately. The successful execution path then flows straight down without nesting.

## Bad Example

```go
func processOrder(order *Order) (*Receipt, error) {
    if order != nil {
        if order.Items != nil && len(order.Items) > 0 {
            if order.UserID > 0 {
                total, err := calculateTotal(order.Items)
                if err == nil {
                    receipt, err := chargeUser(order.UserID, total)
                    if err == nil {
                        return receipt, nil
                    } else {
                        return nil, fmt.Errorf("charge: %w", err)
                    }
                } else {
                    return nil, fmt.Errorf("calculate total: %w", err)
                }
            } else {
                return nil, errors.New("missing user ID")
            }
        } else {
            return nil, errors.New("order has no items")
        }
    }
    return nil, errors.New("order is nil")
}
```

## Good Example

```go
func processOrder(order *Order) (*Receipt, error) {
    if order == nil {
        return nil, errors.New("order is nil")
    }
    if len(order.Items) == 0 {
        return nil, errors.New("order has no items")
    }
    if order.UserID <= 0 {
        return nil, errors.New("missing user ID")
    }

    total, err := calculateTotal(order.Items)
    if err != nil {
        return nil, fmt.Errorf("calculate total: %w", err)
    }

    receipt, err := chargeUser(order.UserID, total)
    if err != nil {
        return nil, fmt.Errorf("charge: %w", err)
    }

    return receipt, nil
}
```

## Why

- **Readability**: The reader sees all the failure conditions upfront, then the happy path uninterrupted
- **Indentation**: Each extra nesting level costs mental energy; early returns keep it flat
- **Diff clarity**: Adding a new guard clause is a clean addition, not a structural change
- **Guard clauses**: This pattern is also called "guard clauses" — standard in Go style

Reference: [Code Review Comments — Error handling](https://github.com/golang/go/wiki/CodeReviewComments#handle-errors) | [Effective Go](https://go.dev/doc/effective_go) | [Code Style reference](../references/code-style.md) | [Error Handling reference](../references/error-handling.md)
See also: `golang/references/code-style.md` | `golang/references/error-handling.md`
