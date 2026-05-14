# Go Benchmarks

Benchmark functions, b.Loop() (Go 1.24+), benchstat comparison, and profiling from benchmarks.

## Basic Benchmark Structure

```go
func BenchmarkProcess(b *testing.B) {
    input := generateInput() // prepare outside the loop

    b.ReportAllocs()  // show allocations/op and bytes/op
    b.ResetTimer()    // exclude setup time

    for i := 0; i < b.N; i++ {
        Process(input)
    }
}
```

## b.Loop() — Go 1.24+

`b.Loop()` replaces the `for i := 0; i < b.N; i++` loop. It handles timer management automatically and provides better accuracy:

```go
// Old pattern (still valid)
func BenchmarkOld(b *testing.B) {
    b.ReportAllocs()
    input := prepareInput()
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        Process(input)
    }
}

// New pattern (Go 1.24+) — b.Loop() handles timer automatically
func BenchmarkNew(b *testing.B) {
    b.ReportAllocs()
    input := prepareInput()
    for b.Loop() {
        Process(input) // loop body is the benchmark
    }
}
```

## Sub-Benchmarks for Multiple Input Sizes

```go
func BenchmarkFibonacci(b *testing.B) {
    for _, n := range []int{1, 10, 20, 30} {
        b.Run(fmt.Sprintf("n=%d", n), func(b *testing.B) {
            b.ReportAllocs()
            for b.Loop() {
                Fibonacci(n)
            }
        })
    }
}

func BenchmarkSortAlgorithms(b *testing.B) {
    sizes := []int{100, 1_000, 10_000}
    for _, size := range sizes {
        b.Run(fmt.Sprintf("size=%d", size), func(b *testing.B) {
            data := generateRandomSlice(size)
            b.ReportAllocs()
            b.ResetTimer()
            for b.Loop() {
                result := make([]int, len(data))
                copy(result, data)
                sort.Ints(result)
            }
        })
    }
}
```

## Parallel Benchmarks

```go
func BenchmarkConcurrentMap(b *testing.B) {
    m := &sync.Map{}
    b.ReportAllocs()

    b.RunParallel(func(pb *testing.PB) {
        i := 0
        for pb.Next() {
            key := fmt.Sprintf("key-%d", i%100)
            m.Store(key, i)
            m.Load(key)
            i++
        }
    })
}
```

## b.ReportMetric — Custom Metrics

```go
func BenchmarkHTTPHandler(b *testing.B) {
    server := httptest.NewServer(handler)
    defer server.Close()

    b.ReportAllocs()
    b.ResetTimer()

    var totalLatency time.Duration
    for b.Loop() {
        start := time.Now()
        resp, _ := http.Get(server.URL + "/users/1")
        resp.Body.Close()
        totalLatency += time.Since(start)
    }

    b.ReportMetric(float64(totalLatency.Milliseconds())/float64(b.N), "ms/op")
}
```

## Running Benchmarks

```bash
# Run all benchmarks
go test -bench=. -benchmem ./...

# Run specific benchmark
go test -bench=BenchmarkProcess -benchmem ./...

# Run sub-benchmarks matching pattern
go test -bench=BenchmarkFibonacci/n=10 -benchmem ./...

# Run N times for statistical significance
go test -bench=. -benchmem -count=6 ./...

# Run with CPU profiling
go test -bench=BenchmarkProcess -benchmem -cpuprofile=cpu.prof ./...
go tool pprof cpu.prof

# Run with memory profiling
go test -bench=BenchmarkProcess -benchmem -memprofile=mem.prof ./...
go tool pprof mem.prof
```

## Comparing Benchmarks with benchstat

```bash
go install golang.org/x/perf/cmd/benchstat@latest

# Save baseline
go test -bench=BenchmarkProcess -benchmem -count=6 ./... | tee /tmp/before.txt

# Make your change...

# Save new results
go test -bench=BenchmarkProcess -benchmem -count=6 ./... | tee /tmp/after.txt

# Compare
benchstat /tmp/before.txt /tmp/after.txt
```

Example output:
```
name         old time/op    new time/op    delta
Process-8    1.23µs ± 2%    0.87µs ± 1%  -29.27%  (p=0.008 n=6+6)

name         old alloc/op   new alloc/op   delta
Process-8    512B ± 0%       64B ± 0%     -87.50%  (p=0.000 n=6+6)

name         old allocs/op  new allocs/op  delta
Process-8    8.00 ± 0%      1.00 ± 0%     -87.50%  (p=0.000 n=6+6)
```

## Profile from Benchmarks

```bash
# CPU profile
go test -bench=BenchmarkProcess -cpuprofile=cpu.prof ./...
go tool pprof -http=:6060 cpu.prof  # open in browser

# Heap profile
go test -bench=BenchmarkProcess -memprofile=mem.prof ./...
go tool pprof -http=:6060 mem.prof

# Trace
go test -bench=BenchmarkProcess -trace=trace.out ./...
go tool trace trace.out
```

## Benchmark Best Practices

```go
// Good — input preparation outside the timed section
func BenchmarkEncrypt(b *testing.B) {
    key := make([]byte, 32)
    rand.Read(key)
    plaintext := make([]byte, 1024)
    rand.Read(plaintext)

    b.SetBytes(int64(len(plaintext)))
    b.ReportAllocs()
    b.ResetTimer()

    for b.Loop() {
        _, err := Encrypt(key, plaintext)
        if err != nil {
            b.Fatal(err)
        }
    }
}

// b.SetBytes — reports throughput (MB/s) in addition to time/op
// Useful for I/O, compression, encoding benchmarks
```

## Common Benchmark Mistakes

| Mistake | Fix |
|---|---|
| Setup code inside the timing loop | Move setup before `b.ResetTimer()` |
| Not calling `b.ReportAllocs()` | Always call it — allocations matter |
| Single run without `-count` | Use `-count=6` for statistical significance |
| Optimized-away loop body | Use the result (assign to a `sink` variable or pass to `b.StopTimer`) |
| Not using `benchstat` for comparison | Eyeballing numbers without statistical test is unreliable |

```go
// Prevent compiler from optimizing away the loop body
var sink any

func BenchmarkSomething(b *testing.B) {
    b.ReportAllocs()
    for b.Loop() {
        sink = expensiveComputation()
    }
    _ = sink
}
```
