# Go Concurrency

Goroutines, channels, context cancellation, sync primitives, and data race prevention.

## When to Load

- Spawning goroutines or managing their lifecycle
- Using channels for communication
- Working with `sync.Mutex`, `sync.WaitGroup`, or `sync.Once`
- Implementing timeouts, deadlines, or cancellation
- Debugging data races

## Rule Index

### 1. Goroutine Lifecycle (CRITICAL)

- [`conc-goroutine-leak`](../rules/conc-goroutine-leak.md) — Every goroutine must have a clear exit path
- `sync.WaitGroup` — Use it to wait for goroutine completion when no shared error path is needed
- `errgroup` — Prefer `golang.org/x/sync/errgroup` when concurrent workers should fail fast together

### 2. Context (CRITICAL)

- [`conc-context-cancellation`](../rules/conc-context-cancellation.md) — Propagate `context.Context`; respect cancellation
- `context ownership` — Never store `context.Context` in a struct; pass it as the first parameter

### 3. Channels (HIGH)

- `channel direction` — Declare send-only/receive-only intent in function signatures where it clarifies ownership
- `select default` — Use `select` with `default` only when non-blocking behavior is intentional and documented

### 4. Shared State (CRITICAL)

- `data race prevention` — Run `go test -race`; never share memory without synchronization
- `mutex scope` — Keep critical sections short and never hold locks across I/O

## Patterns

### Goroutine with Context Cancellation

```go
func worker(ctx context.Context, jobs <-chan Job) error {
    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        case job, ok := <-jobs:
            if !ok {
                return nil
            }
            if err := process(ctx, job); err != nil {
                return fmt.Errorf("process job %d: %w", job.ID, err)
            }
        }
    }
}
```

### errgroup for Fan-out

```go
g, ctx := errgroup.WithContext(ctx)

for _, url := range urls {
    url := url // capture loop variable
    g.Go(func() error {
        return fetch(ctx, url)
    })
}

if err := g.Wait(); err != nil {
    return err
}
```

### Channel Direction

```go
// Producer: send-only channel
func produce(ctx context.Context) <-chan int {
    ch := make(chan int)
    go func() {
        defer close(ch)
        // send values
    }()
    return ch
}

// Consumer: receive-only in signature
func consume(ctx context.Context, ch <-chan int) error { ... }
```

### References

- [Go Concurrency Patterns](https://go.dev/talks/2012/concurrency.slide)
- [Context package](https://pkg.go.dev/context)
- [sync package](https://pkg.go.dev/sync)
- [errgroup](https://pkg.go.dev/golang.org/x/sync/errgroup)
- [The Go Race Detector](https://go.dev/blog/race-detector)
