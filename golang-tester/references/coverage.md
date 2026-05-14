# Go Test Coverage & CI

Coverage commands, thresholds, CI configuration, and test quality guidance.

## Coverage Commands

```bash
# Run tests with coverage summary
go test -cover ./...

# Generate coverage profile
go test -coverprofile=coverage.out ./...

# View coverage in browser
go tool cover -html=coverage.out

# View coverage by function
go tool cover -func=coverage.out

# Extract total coverage percentage
go tool cover -func=coverage.out | grep ^total

# Coverage for specific packages
go test -coverprofile=coverage.out ./internal/...

# Exclude generated files
go test -coverprofile=coverage.out -coverpkg=./... ./...
```

## What to Cover

Focus coverage efforts on **behavior that matters**:

| Always cover | Deprioritize |
|---|---|
| Business logic / domain rules | Auto-generated code |
| Error handling paths | `main()` bootstrap |
| Edge cases (nil, empty, max values) | Simple getters/setters |
| Security-sensitive code | Dependency wiring |
| Public API contracts | `String()` formatters |

**Target: ≥ 80% on business logic packages.** 100% coverage is not always valuable — brittle tests chasing coverage numbers slow development.

## Running Tests — Full Flags

```bash
# Unit tests (no integration)
go test ./...

# Unit tests with race detector
go test -race ./...

# Unit tests, no cache
go test -count=1 ./...

# Verbose output
go test -v ./...

# Run specific test
go test -run TestUserService ./...

# Run specific subtest
go test -run TestUserService/creates_user ./...

# Integration tests
go test -tags=integration ./...

# Integration with race detector
go test -tags=integration -race ./...

# All tests — unit, integration, race
go test -tags=integration -race -count=1 ./...

# With coverage
go test -race -count=1 -coverprofile=coverage.out ./...
go tool cover -func=coverage.out | grep total
```

## CI Configuration

### GitHub Actions

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: '1.24'
          cache: true

      - name: Run unit tests
        run: go test -race -count=1 -coverprofile=coverage.out ./...

      - name: Check coverage threshold
        run: |
          COVERAGE=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | sed 's/%//')
          echo "Coverage: ${COVERAGE}%"
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "Coverage ${COVERAGE}% is below threshold of 80%"
            exit 1
          fi

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: coverage.out

  integration:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: testdb
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.24'
          cache: true

      - name: Run integration tests
        env:
          TEST_DATABASE_URL: postgres://test:test@localhost:5432/testdb?sslmode=disable
        run: go test -tags=integration -race -count=1 ./...
```

### Makefile

```makefile
.PHONY: test test-integration test-all coverage lint

test:
	go test -race -count=1 ./...

test-integration:
	go test -tags=integration -race -count=1 ./...

test-all: test test-integration

coverage:
	go test -race -count=1 -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out
	go tool cover -func=coverage.out | grep total

lint:
	golangci-lint run ./...

bench:
	go test -bench=. -benchmem -count=6 ./...
```

## Test Caching

Go caches test results. Use `-count=1` to disable the cache when you need a fresh run:

```bash
go test -count=1 ./...         # bypass cache
go clean -testcache            # clear the entire test cache
```

Tests are cached based on inputs, environment variables, and file changes. The cache is safe to rely on in most cases.

## Test Tagging Strategy

```go
// Unit test — no tag, fast, no external deps
package order_test

func TestCalculateTotal(t *testing.T) { ... }
```

```go
//go:build integration
// Integration test — real DB, external services
package order_test

func TestCreateOrderInDB(t *testing.T) { ... }
```

```go
//go:build e2e
// End-to-end test — full stack
package e2e_test

func TestCheckoutFlow(t *testing.T) { ... }
```

## Coverage Exclusions

To exclude generated code or boilerplate from coverage:

```go
// coverage:ignore — exclude a function
func generateBoilerplate() string { // coverage:ignore
    // ...
}
```

In `.golangci.yml`, configure `gocover-cobertura` or use `coverpkg` to exclude packages:

```bash
# Only measure coverage for specific packages
go test -coverpkg=./internal/...,./pkg/... -coverprofile=coverage.out ./...
```

## Reading Coverage Reports

```
github.com/myapp/internal/order/service.go:45:   CreateOrder     87.5%
github.com/myapp/internal/order/service.go:89:   CancelOrder     100.0%
github.com/myapp/internal/order/service.go:120:  RefundOrder     62.5%  ← needs tests
total:                                            (statements)    82.1%
```

Lines shown in browser:
- **Red** — not covered by any test
- **Green** — covered by at least one test
- **Gray** — not statements (declarations, blank lines)
