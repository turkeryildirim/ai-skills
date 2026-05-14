---
title: Detect Goroutine Leaks with goleak
impact: HIGH
impactDescription: Leaked goroutines silently accumulate; goleak catches them in tests before they reach production
tags: testing, goroutine, leak, goleak, concurrency
---

## Detect Goroutine Leaks with goleak

**Impact: HIGH — Leaked goroutines don't cause test failures; they pass and accumulate until production runs out of memory**

Use `go.uber.org/goleak` to verify that all goroutines started during a test are stopped before the test ends.

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
    // test logic ...
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
    // test logic ...
    pool.Stop() // must stop before VerifyNone runs
}
```

## Excluding Known Background Goroutines

```go
func TestMain(m *testing.M) {
    goleak.VerifyTestMain(m,
        goleak.IgnoreTopFunction("net/http.(*Server).Serve"),
        goleak.IgnoreCurrent(), // ignore goroutines that existed before tests started
    )
}
```

## When to Add goleak

Add `goleak.VerifyTestMain` to any package that:
- Spawns goroutines in production code
- Starts background workers, timers, or tickers
- Opens connections (HTTP, gRPC, database) that might not be closed
- Uses channels that could block indefinitely

## Why

- **Silent failures** — leaked goroutines don't cause test failures on their own
- **Production impact** — each leaked goroutine consumes stack memory (~2–8 KB minimum) and potentially holds resources
- **Early detection** — catching leaks in tests is far cheaper than debugging production memory growth

Reference: [Goroutine Leaks — Dave Cheney](https://dave.cheney.net/2016/12/22/never-start-a-goroutine-without-knowing-how-it-will-stop) | [uber-go/goleak](https://github.com/uber-go/goleak) | [Patterns reference](../references/patterns.md)
See also: `golang-tester/references/patterns.md`
