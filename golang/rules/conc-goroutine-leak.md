---
title: Prevent Goroutine Leaks
impact: CRITICAL
impactDescription: Leaked goroutines consume memory and file descriptors indefinitely
tags: concurrency, goroutine, leak, context
---

## Prevent Goroutine Leaks

**Impact: CRITICAL — Leaked goroutines consume memory and file descriptors indefinitely**

Every goroutine must have a clear, deterministic exit path. Use `context.Context` for cancellation and always ensure goroutines can exit when their work is done or their caller gives up.

## Bad Example

```go
func startWorker(jobs <-chan Job) {
    go func() {
        for job := range jobs {
            process(job)
        }
        // If `jobs` is never closed, this goroutine leaks forever.
    }()
    // No way for the caller to stop the worker.
}
```

## Good Example

```go
func startWorker(ctx context.Context, jobs <-chan Job) {
    go func() {
        for {
            select {
            case <-ctx.Done():
                return // clean exit on cancellation
            case job, ok := <-jobs:
                if !ok {
                    return // channel closed — exit cleanly
                }
                process(ctx, job)
            }
        }
    }()
}

// Usage
ctx, cancel := context.WithCancel(context.Background())
defer cancel() // guarantees goroutine exits when caller returns

startWorker(ctx, jobs)
```

## Why

- **Memory**: Each goroutine has a minimum stack of ~2–8 KB; leaks accumulate
- **File Descriptors**: Goroutines holding connections or files prevent cleanup
- **Detectability**: Use `goleak` (uber-go/goleak) in tests to detect leaks automatically
- **Ownership**: The goroutine's creator is responsible for its lifecycle

Reference: [Goroutine Leaks — Dave Cheney](https://dave.cheney.net/2016/12/22/never-start-a-goroutine-without-knowing-how-it-will-stop) | [uber-go/goleak](https://github.com/uber-go/goleak) | [Concurrency reference](../references/concurrency.md) | [test-goleak rule](test-goleak.md)
See also: `golang/references/concurrency.md`
