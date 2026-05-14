---
title: Detect Goroutine Leaks with goleak
impact: HIGH
impactDescription: Leaked goroutines silently accumulate; goleak catches them in tests
tags: testing, goroutine, leak, goleak
---

## Detect Goroutine Leaks with goleak

**Impact: HIGH — Leaked goroutines silently accumulate; goleak catches them in tests**

Use `go.uber.org/goleak` to detect goroutines that are still running after a test completes. Without it, goroutine leaks accumulate silently until the process runs out of memory or file descriptors in production.

## Setup

```bash
go get go.uber.org/goleak
```

## Bad Example

```go
// No leak detection — goroutines that leak pass unnoticed
func TestWorkerPool(t *testing.T) {
    pool := NewWorkerPool(10)
    pool.Start()
    // ... test logic ...
    // pool never stopped — 10 goroutines leak, test still passes
}
```

## Good Example

```go
// TestMain catches leaks across the entire package
func TestMain(m *testing.M) {
    goleak.VerifyTestMain(m)
}

// Per-test when a specific test exercises goroutines
func TestWorkerPool(t *testing.T) {
    defer goleak.VerifyNone(t)

    pool := NewWorkerPool(10)
    pool.Start()
    // ... test logic ...
    pool.Stop() // must clean up before VerifyNone runs
}
```

## Excluding Known Background Goroutines

Some goroutines are started by the test runtime or known libraries and can be safely ignored:

```go
func TestMain(m *testing.M) {
    goleak.VerifyTestMain(m,
        // Ignore goroutines from specific packages
        goleak.IgnoreTopFunction("net/http.(*Server).Serve"),
        // Ignore all goroutines that existed before the test started
        goleak.IgnoreCurrent(),
    )
}
```

## When to Add goleak

Add `goleak.VerifyTestMain` to any package that:
- Spawns goroutines in production code
- Starts background workers, timers, or tickers
- Opens connections that might not be closed
- Uses channels that could block indefinitely

## Why

- **Silent failures**: Goroutine leaks don't cause test failures — they pass and accumulate
- **Production impact**: Each leaked goroutine consumes stack memory (~2–8 KB minimum) and potentially holds resources (connections, file descriptors)
- **Early detection**: Catching leaks in tests is far cheaper than debugging production memory growth
- **Integration with `t.Parallel()`**: `goleak.VerifyNone` works correctly with parallel subtests

Reference: [uber-go/goleak](https://github.com/uber-go/goleak) | [conc-goroutine-leak rule](conc-goroutine-leak.md)
