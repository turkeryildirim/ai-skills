---
title: Go Concurrency Pattern Analysis
impact: CRITICAL
impactDescription: "Goroutine leaks and missing context propagation cause silent resource exhaustion and unpredictable service behavior"
tags: golang, concurrency, goroutine, channel, context, mutex, sync, leak
---

## Go Concurrency Pattern Analysis

**Impact: CRITICAL (Goroutine leaks and missing context propagation cause silent resource exhaustion and unpredictable service behavior)**

Go's concurrency primitives are powerful but require discipline. Goroutines started without a clear termination path, missing context propagation, and incorrect mutex usage are the most frequent sources of production incidents in Go services.

## Incorrect

```go
// ❌ Goroutine leak — no termination path
func StartWorker() {
    go func() {
        for {
            processItem()  // ❌ runs forever, cannot be stopped
        }
    }()
}

// ❌ context.Background() inside request handler — ignores client cancellation
func (h *Handler) GetData(w http.ResponseWriter, r *http.Request) {
    result, err := h.svc.FetchFromDB(context.Background())  // ❌ should use r.Context()
    // ...
}

// ❌ Goroutine started without waiting for completion
func processAll(items []Item) {
    for _, item := range items {
        go process(item)  // ❌ main returns before goroutines finish
    }
    // return — goroutines may still be running
}
```

## Correct

```go
// ✅ Goroutine with controlled lifecycle via context
func StartWorker(ctx context.Context) {
    go func() {
        for {
            select {
            case <-ctx.Done():
                return  // ✅ clean exit when context cancelled
            default:
                processItem()
            }
        }
    }()
}

// ✅ Request context propagated to all downstream calls
func (h *Handler) GetData(w http.ResponseWriter, r *http.Request) {
    result, err := h.svc.FetchFromDB(r.Context())  // ✅ propagates deadline + cancellation
    // ...
}

// ✅ WaitGroup for fan-out with deterministic completion
func processAll(ctx context.Context, items []Item) error {
    var wg sync.WaitGroup
    errs := make(chan error, len(items))

    for _, item := range items {
        wg.Add(1)
        go func(i Item) {
            defer wg.Done()
            if err := process(ctx, i); err != nil {
                errs <- err
            }
        }(item)  // ✅ capture loop variable
    }

    wg.Wait()
    close(errs)
    for err := range errs {
        return err  // return first error
    }
    return nil
}
```

## Concurrency Compliance Assessment

```
CRITICAL violations:
├── Goroutines started with no context or done channel (goroutine leak)
├── context.Background() used in request-scoped handlers
└── go func() inside loops without capturing loop variable (pre-Go 1.22)

HIGH violations:
├── Shared mutable state without sync.Mutex or sync/atomic
├── Channel sends with no corresponding receive (channel leak)
└── Missing timeout context for external calls (DB, HTTP client, gRPC)

MEDIUM violations:
├── sync.Mutex used where sync/atomic or channels would be simpler
├── WaitGroup.Add() called inside goroutine instead of before launch
└── errgroup not used when multiple goroutines must return errors

LOW violations:
├── sync.Mutex embedded in struct that is passed by value (copies lock)
└── Unbuffered channel used where a small buffer would prevent blocking
```

## Context Propagation Checklist

```
All DB calls:        db.QueryContext(ctx, ...)  ✅
All HTTP clients:    req.WithContext(ctx)        ✅
All gRPC calls:      client.Method(ctx, ...)    ✅
All time.Sleep:      select { case <-ctx.Done(): return; case <-time.After(d): }  ✅

❌ Red flags:
context.Background() in handlers
context.TODO() in non-stub production code
Missing ctx parameter in service/repository function signatures
```

## Why

- **Goroutine leaks**: Unlike threads, leaked goroutines hold references to memory and keep sockets open; `goleak` in tests will catch these
- **Context cancellation**: When a client disconnects, `r.Context()` is cancelled — database queries and external calls must honour this to avoid wasted work
- **Loop variable capture**: Pre Go 1.22, `go func() { use(item) }()` always captures the last value — must use `go func(i Item) { use(i) }(item)`
