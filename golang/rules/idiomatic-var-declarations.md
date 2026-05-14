---
title: var vs := — Declaration Form Signals Intent
impact: HIGH
impactDescription: The declaration form communicates whether the zero value is intentional
tags: idiomatic, declaration, var, short-variable
---

## var vs := — Declaration Form Signals Intent

**Impact: HIGH — The declaration form communicates whether the zero value is intentional**

Use `:=` for non-zero values assigned at declaration time. Use `var` when the zero value is the intended initial value — this signals that the variable will be set later or that the zero value is meaningful.

## Bad Example

```go
// var for a non-zero value — looks like the zero value was intended
var name = "default"

// := for a zero value — hides that zero is the intent
count := 0
found := false
var buf = bytes.Buffer{} // zero value is ready to use; just use var buf bytes.Buffer

// Redundant zero-value initialization
var users []*User = nil    // nil is already the zero value for slices
var timeout int = 0        // 0 is already the zero value for int
```

## Good Example

```go
// var — signals "this starts at zero and will be set later"
var count int
var found bool
var buf bytes.Buffer   // zero value of bytes.Buffer is ready to use — no need to call New

// := — signals "this starts with a non-zero computed value"
name := "default"
timeout := 5 * time.Second
users := make([]*User, 0, len(ids))

// var for zero-value-ready types (idiomatic)
var sb strings.Builder
var mu sync.Mutex
var wg sync.WaitGroup
```

## Package-level Variables

Package-level variables always use `var` (`:=` is not allowed at package scope):

```go
var (
    defaultTimeout = 30 * time.Second
    ErrNotFound    = errors.New("not found")
)
```

## Multiple Assignment with var Block

Group related zero-value declarations in a `var` block:

```go
var (
    total   int
    count   int
    lastErr error
)
```

## Why

- **Readability**: `var count int` is immediately understood as "starts at zero, set later"
- **Zero-value types**: `bytes.Buffer`, `sync.Mutex`, `sync.WaitGroup` are ready at zero — no constructor needed
- **Convention**: The Go standard library follows this pattern consistently
- **Signal**: `var` tells the next reader "I chose zero deliberately"

Reference: [Effective Go — Variables](https://go.dev/doc/effective_go#variables) | [Go Code Review Comments — Variable Declarations](https://github.com/golang/go/wiki/CodeReviewComments#variable-declarations) | [Code Style reference](../references/code-style.md)
See also: `golang/references/code-style.md`
