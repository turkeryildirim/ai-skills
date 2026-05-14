# Go Performance

Allocation reduction, profiling methodology, CPU optimization, memory layout, GC tuning, and pooling.

## When to Load

- Profiling has identified a bottleneck and you need the right optimization pattern
- Reviewing hot paths for structural anti-patterns
- Pre-allocating slices and maps
- Reducing GC pressure in high-throughput services

## Core Philosophy

1. **Profile before optimizing** — intuition about bottlenecks is wrong ~80% of the time
2. **Allocation reduction yields the biggest ROI** — reducing allocations per request often matters more than micro-optimizing CPU
3. **Document optimizations** — add comments explaining why with benchmark numbers; future readers need context to avoid reverting an optimization
4. **Rule out external bottlenecks first** — if 90% of latency is a slow DB query or API call, reducing allocations won't help

## Rule Index

- [`perf-prealloc`](../rules/perf-prealloc.md) — Pre-allocate slices/maps with known capacity
- `strings.Builder` — Prefer it over repeated string concatenation in loops
- `sync.Pool` — Reuse temporary objects only in measured hot paths
- `escape analysis` — Check heap escapes with `go build -gcflags=\"-m\"`
- `profiling first` — Profile with `pprof` before optimizing

## Iterative Optimization Methodology

1. **Define your metric** — latency, throughput, memory, or CPU? Without a target, optimizations are random
2. **Baseline** — `go test -bench=BenchmarkMyFunc -benchmem -count=6 ./pkg/... | tee /tmp/report-1.txt`
3. **Diagnose** — use pprof to identify the actual hot spot
4. **Improve** — apply ONE optimization at a time with an explanatory comment
5. **Compare** — `benchstat /tmp/report-1.txt /tmp/report-2.txt` to confirm statistical significance
6. **Commit** — paste benchstat output in the commit body so reviewers see the exact improvement

## Decision Tree: Where Is Time Spent?

| Bottleneck | Signal (from pprof) | Action |
|---|---|---|
| Too many allocations | `alloc_objects` high in heap profile | Use `sync.Pool`, prealloc, reduce escapes |
| CPU-bound hot loop | Function dominates CPU profile | Inlining, avoid reflection, cache locality |
| GC pauses / OOM | High GC%, container limits hit | Set `GOMEMLIMIT`, reduce allocations |
| Network / I/O latency | Goroutines blocked on I/O | Connection pooling, streaming, batch I/O |
| Repeated expensive work | Same computation multiple times | Caching, `sync.Once`, `singleflight` |
| Wrong algorithm | O(n²) where O(n) exists | Choose right data structure |
| Lock contention | Mutex/block profile hot | Use channels, sharding, lock-free structures |

## Profiling Commands

```bash
# CPU profile
go test -cpuprofile=cpu.prof -bench=. ./...
go tool pprof cpu.prof

# Memory profile
go test -memprofile=mem.prof -benchmem -bench=. ./...
go tool pprof mem.prof

# Escape analysis — shows what allocates on the heap
go build -gcflags="-m" ./...
go build -gcflags="-m=2" ./... # more verbose

# Inline analysis
go build -gcflags="-m" ./... 2>&1 | grep "inlining call"

# Compare benchmarks
go install golang.org/x/perf/cmd/benchstat@latest
benchstat /tmp/report-1.txt /tmp/report-2.txt

# Benchmark with memory stats
go test -bench=BenchmarkMyFunc -benchmem -count=6 ./...
```

## Allocation Reduction

### Pre-allocate Slices and Maps

```go
// Bad — repeated reallocations as slice grows
var results []string
for _, item := range items {
    results = append(results, process(item))
}

// Good — single allocation
results := make([]string, 0, len(items))
for _, item := range items {
    results = append(results, process(item))
}

// Pre-grow for subsequent appends (Go 1.21+)
results = slices.Grow(results, additionalCount)

// Map preallocation
m := make(map[string]*User, len(users)) // avoids rehashing
```

### String Building

```go
// Bad — O(n²) allocations
s := ""
for _, part := range parts {
    s += part
}

// Good — single buffer, String() does not copy
var sb strings.Builder
sb.Grow(estimatedSize)
for _, part := range parts {
    sb.WriteString(part)
}
s := sb.String()
```

### sync.Pool — Reuse Temporary Objects

```go
var bufPool = sync.Pool{
    New: func() any { return new(bytes.Buffer) },
}

func renderTemplate(w http.ResponseWriter, tmpl *template.Template, data any) {
    buf := bufPool.Get().(*bytes.Buffer)
    buf.Reset()
    defer bufPool.Put(buf) // return to pool, not to GC

    if err := tmpl.Execute(buf, data); err != nil {
        http.Error(w, "render error", http.StatusInternalServerError)
        return
    }
    buf.WriteTo(w)
}
```

Rules for `sync.Pool`:
- Objects must be safe to reuse — always `Reset()` before use
- Pool entries are GC'd between GC cycles — don't use for objects that must be retained
- Pool is most effective for objects created and discarded at high frequency

### Reduce Heap Escapes

```go
// Escape — pointer returned, allocates on heap
func newPoint(x, y int) *Point {
    return &Point{x, y} // escapes to heap
}

// Stack allocation — pass by value for small structs
func newPoint(x, y int) Point {
    return Point{x, y} // stays on stack
}

// Force stack allocation with size hint
var p Point // declare outside, reuse
p.x = x
p.y = y
```

## CPU Optimization

### Avoid Reflection in Hot Paths

```go
// Bad — reflect is 50-200x slower than typed comparison
reflect.DeepEqual(a, b)

// Good — typed comparison
slices.Equal(a, b)
maps.Equal(a, b)
bytes.Equal(a, b)
```

### Avoid Logging in Hot Loops

```go
// Bad — log calls prevent inlining and allocate even when level is disabled
for _, item := range items {
    slog.Debug("processing", "item", item) // allocates on every iteration
}

// Good — check level before constructing attributes
if slog.Default().Enabled(ctx, slog.LevelDebug) {
    slog.Debug("processing", "count", len(items))
}
// Or log outside the loop with aggregate stats
```

### HTTP Transport Configuration

```go
// Default http.Client has MaxIdleConnsPerHost = 2 — too low for concurrent services
client := &http.Client{
    Transport: &http.Transport{
        MaxIdleConnsPerHost:   100,
        MaxConnsPerHost:       100,
        IdleConnTimeout:       90 * time.Second,
        TLSHandshakeTimeout:   10 * time.Second,
        ResponseHeaderTimeout: 30 * time.Second,
    },
    Timeout: 60 * time.Second,
}
```

## GC Tuning

```bash
# Limit memory — GC triggers more aggressively before hitting the limit
# Set to 80-90% of container memory to prevent OOM kills
GOMEMLIMIT=1800MiB ./server

# Control GC frequency (default: trigger when heap doubles)
# Lower = more frequent GC (less memory, more CPU)
# Higher = less frequent GC (more memory, less CPU)
GOGC=100 ./server  # default
GOGC=200 ./server  # less frequent GC, higher memory
```

```go
// Set programmatically
import "runtime/debug"

func init() {
    // Limit to 1.8 GiB
    debug.SetMemoryLimit(1800 << 20)
}
```

## Caching Patterns

### singleflight — Prevent Cache Stampedes

```go
import "golang.org/x/sync/singleflight"

var group singleflight.Group

func (c *Cache) Get(ctx context.Context, key string) (*Result, error) {
    v, err, _ := group.Do(key, func() (any, error) {
        // Only one goroutine executes this — others wait and share the result
        return c.fetchFromDB(ctx, key)
    })
    if err != nil {
        return nil, err
    }
    return v.(*Result), nil
}
```

### sync.Once for Lazy Initialization

```go
// sync.OnceValue (Go 1.21+) — typed lazy init
getConfig := sync.OnceValue(func() *Config {
    return loadConfigFromFile("config.yaml")
})

// Used anywhere
cfg := getConfig() // loaded once, cached forever
```

## Struct Field Alignment

```go
// Bad — 40 bytes due to padding
type Bad struct {
    a bool    // 1 byte + 7 padding
    b float64 // 8 bytes
    c bool    // 1 byte + 7 padding
    d float64 // 8 bytes
    e bool    // 1 byte + 7 padding
}

// Good — 26 bytes (group same-size fields together)
type Good struct {
    b float64 // 8 bytes
    d float64 // 8 bytes
    a bool    // 1 byte
    c bool    // 1 byte
    e bool    // 1 byte
              // 5 bytes padding at end
}

// fieldalignment linter detects this
go install golang.org/x/tools/go/analysis/passes/fieldalignment/cmd/fieldalignment@latest
fieldalignment ./...
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Optimizing without profiling | Profile with pprof first — intuition is wrong ~80% of the time |
| Default `http.Client` without Transport | `MaxIdleConnsPerHost` defaults to 2 — set to match concurrency |
| `reflect.DeepEqual` in production | 50-200x slower — use `slices.Equal`, `maps.Equal`, `bytes.Equal` |
| Logging in tight loops | Allocates on every iteration — log aggregated stats outside the loop |
| `panic`/`recover` as control flow | Allocates a stack trace on every panic — use error returns |
| No `GOMEMLIMIT` in containers | Risk of OOM kill — set to 80-90% of container memory |
| `sync.Pool` for objects that must be retained | Pool entries are GC'd between cycles — use for temporary buffers only |

## References

- [Profiling Go Programs](https://go.dev/blog/pprof)
- [benchstat](https://pkg.go.dev/golang.org/x/perf/cmd/benchstat)
- [sync.Pool](https://pkg.go.dev/sync#Pool)
- [strings.Builder](https://pkg.go.dev/strings#Builder)
- [singleflight](https://pkg.go.dev/golang.org/x/sync/singleflight)
- [High Performance Go Workshop — Dave Cheney](https://dave.cheney.net/high-performance-go-workshop/gophercon-2019.html)
