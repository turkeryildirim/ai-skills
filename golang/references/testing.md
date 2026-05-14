# Go Testing

Table-driven tests, subtests, integration tags, mocks, benchmarks, goleak, fuzzing.

> For comprehensive test guidance use the `golang-tester` skill.

## When to Load

- Quick reference for test structure, naming, and commands
- Setting up goleak or integration build tags

## Best Practices Summary

1. Table-driven tests MUST use named subtests — every case needs a `name` field passed to `t.Run`
2. Integration tests MUST use `//go:build integration` build tags
3. Tests MUST NOT depend on execution order — each must be independently runnable
4. Independent tests SHOULD use `t.Parallel()`
5. NEVER test implementation details — test observable behavior and public API contracts
6. Use `goleak.VerifyTestMain` in packages with goroutines to detect leaks
7. Use testify as helpers, not a replacement for the standard library
8. Mock interfaces, not concrete types
9. Keep unit tests fast (< 1ms); isolate integration tests with build tags
10. Run tests with race detection in CI: `go test -race ./...`

## File Conventions

```go
// Black-box test — separate package, tests public API (preferred)
package mypackage_test

// White-box test — same package, access unexported
package mypackage
```

## Naming Conventions

```go
func TestAdd(t *testing.T) { ... }               // function test
func TestMyStruct_MyMethod(t *testing.T) { ... } // method test
func BenchmarkAdd(b *testing.B) { ... }          // benchmark
func ExampleAdd() { ... }                        // example (verified by go test)
func FuzzAdd(f *testing.F) { ... }               // fuzz test
```

## Table-Driven Tests

```go
func TestCalculatePrice(t *testing.T) {
    t.Parallel()
    tests := []struct {
        name      string
        quantity  int
        unitPrice float64
        want      float64
        wantErr   bool
    }{
        {name: "single item", quantity: 1, unitPrice: 10.0, want: 10.0},
        {name: "bulk discount", quantity: 100, unitPrice: 10.0, want: 900.0},
        {name: "zero quantity", quantity: 0, unitPrice: 10.0, want: 0.0},
    }

    for _, tt := range tests {
        tt := tt // capture (required before Go 1.22)
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()
            got := CalculatePrice(tt.quantity, tt.unitPrice)
            if got != tt.want {
                t.Errorf("got %.2f; want %.2f", got, tt.want)
            }
        })
    }
}
```

## Goroutine Leak Detection

```go
func TestMain(m *testing.M) {
    goleak.VerifyTestMain(m)
}
```

## Integration Tests

```go
//go:build integration

func TestDatabaseIntegration(t *testing.T) { ... }
```

```bash
go test ./...                    # unit tests only
go test -tags=integration ./...  # includes integration tests
```

## Quick Reference

```bash
go test ./...                           # all unit tests
go test -run TestName ./...             # specific test
go test -run TestName/subtest ./...     # specific subtest
go test -race ./...                     # with race detector
go test -cover ./...                    # coverage summary
go test -bench=. -benchmem ./...        # benchmarks
go test -fuzz=FuzzName ./...            # fuzzing
go test -tags=integration ./...         # integration tests
go test -count=1 ./...                  # disable test cache
go test -v ./...                        # verbose output
```

## References

- [testing package](https://pkg.go.dev/testing)
- [testify](https://github.com/stretchr/testify)
- [gomock (uber-go/mock)](https://github.com/uber-go/mock)
- [goleak](https://github.com/uber-go/goleak)
- [Table Driven Tests](https://github.com/golang/go/wiki/TableDrivenTests)
