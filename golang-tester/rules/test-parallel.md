---
title: Use t.Parallel() for Independent Tests
impact: HIGH
impactDescription: Parallel tests reduce CI time; without t.Parallel() sequential tests take much longer than necessary
tags: testing, parallel, t.Parallel, performance
---

## Use t.Parallel() for Independent Tests

**Impact: HIGH — Parallel tests reduce CI time significantly; sequential tests take much longer than necessary**

Call `t.Parallel()` at the top of every test function and subtest that does not share mutable state with other tests. Go runs parallel tests concurrently within the same package.

## Bad Example

```go
// Sequential — only one test runs at a time
func TestCalculatePrice(t *testing.T) {
    tests := []struct{ ... }{ ... }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // Each subtest waits for the previous one to finish
            got := CalculatePrice(tt.quantity, tt.unitPrice)
            // ...
        })
    }
}
```

## Good Example

```go
func TestCalculatePrice(t *testing.T) {
    t.Parallel() // this test can run concurrently with other test functions

    tests := []struct {
        name      string
        quantity  int
        unitPrice float64
        want      float64
    }{
        {name: "single item", quantity: 1, unitPrice: 10.0, want: 10.0},
        {name: "bulk discount", quantity: 100, unitPrice: 10.0, want: 900.0},
    }

    for _, tt := range tests {
        tt := tt // capture loop variable (required before Go 1.22)
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel() // each subtest runs concurrently

            got := CalculatePrice(tt.quantity, tt.unitPrice)
            if got != tt.want {
                t.Errorf("got %v; want %v", got, tt.want)
            }
        })
    }
}
```

## When NOT to use t.Parallel()

```go
// Tests that write to shared state must NOT be parallel
func TestDatabaseMigration(t *testing.T) {
    // No t.Parallel() — modifies shared database schema
    runMigration(testDB)
    // ...
}

// Tests that use t.Setenv cannot be parallel (panics)
func TestWithEnvVar(t *testing.T) {
    // No t.Parallel() — t.Setenv is incompatible with t.Parallel()
    t.Setenv("API_KEY", "test")
    // ...
}
```

## Loop Variable Capture (Pre-Go 1.22)

Before Go 1.22, loop variables are shared across iterations. Capture them before passing to a goroutine or parallel subtest:

```go
for _, tt := range tests {
    tt := tt // shadow the loop variable — each goroutine gets its own copy
    t.Run(tt.name, func(t *testing.T) {
        t.Parallel()
        // tt is safe to use here
    })
}
// In Go 1.22+, loop variables are per-iteration — tt := tt is not needed
```

## Why

- **Speed** — parallel tests complete in `max(individual durations)` instead of `sum(all durations)`
- **Flakiness detection** — parallel tests expose race conditions that sequential tests hide
- **Standard practice** — the Go standard library uses `t.Parallel()` extensively

Reference: [Go Testing — Parallel Tests](https://pkg.go.dev/testing#hdr-Parallel_Tests) | [Patterns reference](../references/patterns.md)
See also: `golang-tester/references/patterns.md`
