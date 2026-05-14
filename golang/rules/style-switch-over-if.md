---
title: Prefer switch Over if-else Chains
impact: HIGH
impactDescription: switch is more readable and exhaustiveness is easier to verify
tags: style, control-flow, switch, idiomatic
---

## Prefer switch Over if-else Chains

**Impact: HIGH — switch is more readable and exhaustiveness is easier to verify**

When the same variable or expression is compared against multiple values, prefer `switch` over a sequence of `if-else if`. For unrelated boolean conditions, use a `switch` without an expression (tagless switch).

## Bad Example

```go
// Repeated variable comparison — hard to scan
func handleStatus(status OrderStatus) {
    if status == StatusPending {
        queue(order)
    } else if status == StatusActive {
        process(order)
    } else if status == StatusCancelled {
        refund(order)
    } else if status == StatusCompleted {
        archive(order)
    } else {
        log.Printf("unexpected status: %v", status)
    }
}

// Boolean else-if chain hides default
func setLevel(debug, verbose bool) slog.Level {
    if debug {
        return slog.LevelDebug
    } else if verbose {
        return slog.LevelWarn
    } else {
        return slog.LevelInfo
    }
}
```

## Good Example

```go
// switch on variable — clear, exhaustiveness-checkable
func handleStatus(status OrderStatus) {
    switch status {
    case StatusPending:
        queue(order)
    case StatusActive:
        process(order)
    case StatusCancelled:
        refund(order)
    case StatusCompleted:
        archive(order)
    default:
        log.Printf("unexpected status: %v", status)
    }
}

// Tagless switch for unrelated boolean conditions
func setLevel(debug, verbose bool) slog.Level {
    level := slog.LevelInfo
    switch {
    case debug:
        level = slog.LevelDebug
    case verbose:
        level = slog.LevelWarn
    }
    return level
}
```

## Exhaustiveness Checking

When switching on a custom type (especially an `iota` enum), add a `default` that panics or logs — this catches unhandled future values:

```go
switch direction {
case North, South, East, West:
    move(direction)
default:
    panic(fmt.Sprintf("unhandled direction: %v", direction))
}
```

Tools like `exhaustive` linter enforce that all enum values are covered.

## Why

- **Readability**: The compared expression appears once, cases are visually aligned
- **Exhaustiveness**: Static analysis tools can warn about missing cases for typed enums
- **No fallthrough by default**: Go `switch` doesn't fall through; each case is independent
- **Convention**: Preferred form in the Go standard library

Reference: [Effective Go — Switch](https://go.dev/doc/effective_go#switch) | [exhaustive linter](https://github.com/nishanths/exhaustive) | [Code Style reference](../references/code-style.md)
See also: `golang/references/code-style.md`
