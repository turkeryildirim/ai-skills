---
title: Eliminate Unnecessary else
impact: HIGH
impactDescription: Reduces nesting and makes control flow obvious
tags: style, control-flow, else, idiomatic
---

## Eliminate Unnecessary else

**Impact: HIGH — Reduces nesting and makes control flow obvious**

When an `if` block ends with `return`, `break`, `continue`, or `panic`, the `else` clause is unnecessary and adds indentation for no reason. Drop it.

For assignments with a default value, assign first and override with independent conditions rather than an else-if chain.

## Bad Example

```go
// Unnecessary else after return
func describe(n int) string {
    if n > 0 {
        return "positive"
    } else if n < 0 {
        return "negative"
    } else {
        return "zero"
    }
}

// Else-if chain hides that there is a default
func logLevel(debug, verbose bool) slog.Level {
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
// Drop else — the return already exits
func describe(n int) string {
    if n > 0 {
        return "positive"
    }
    if n < 0 {
        return "negative"
    }
    return "zero"
}

// Default-then-override with switch — cleanest for mutually exclusive conditions
func logLevel(debug, verbose bool) slog.Level {
    level := slog.LevelInfo // default
    switch {
    case debug:
        level = slog.LevelDebug
    case verbose:
        level = slog.LevelWarn
    }
    return level
}
```

## Also Applies to break / continue

```go
// Bad
for _, item := range items {
    if item.IsValid() {
        process(item)
    } else {
        continue
    }
}

// Good
for _, item := range items {
    if !item.IsValid() {
        continue
    }
    process(item)
}
```

## Why

- **Indentation**: Each unnecessary `else` adds a level of nesting for the remainder of the function
- **Clarity**: The reader doesn't need to track "what branch am I in?" after a `return`
- **Linters**: `gocritic` and `revive` flag this automatically
- **Go convention**: Standard library code consistently omits unnecessary `else`

Reference: [Code Review Comments — Indent Error Flow](https://github.com/golang/go/wiki/CodeReviewComments#indent-error-flow) | [Code Style reference](../references/code-style.md)
See also: `golang/references/code-style.md`
