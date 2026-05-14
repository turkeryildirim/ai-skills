---
name: golang-tester
description: Expert Go testing skill — unit tests, table-driven tests, parallel tests, mocking, integration tests, benchmarks, fuzzing, and goroutine leak detection. Use when writing, reviewing, or debugging Go tests of any kind. Triggers on "Go test", "golang test", "testify", "goleak", "gomock", "table-driven", "benchmark", "fuzz", "go test", "httptest", "testcontainers".
model: inherit
---

# Go Testing Best Practices

Comprehensive guidance for writing correct, fast, and maintainable Go tests. Covers unit tests, integration tests, mocking, benchmarks, fuzzing, and test infrastructure.

> "Test names are specifications. A failing test name should tell you exactly what broke." — Go Testing Proverbs

## Specialized Agents

| Agent | Role | Focus |
|-------|------|-------|
| **golang-tester-pro** | Go Testing Expert | Table-driven tests, mocking strategies, integration patterns, benchmarks, TDD. |

## When to Use

- Writing new unit, integration, or benchmark tests
- Reviewing existing tests for correctness, isolation, or coverage
- Setting up test infrastructure (goleak, testcontainers, build tags)
- Choosing between inline mocks, testify/mock, and gomock
- Debugging flaky or slow tests
- Adding fuzz tests or golden file tests
- Improving code coverage

Use `golang` alongside this skill when the test task also requires production-code refactors or broader package/API design review.

## Step 1: Detect Go Version and Test Stack

Always confirm the active toolchain and the test libraries already in use before recommending new patterns.

```bash
go version
go test ./...
```

Check `go.mod` for the module version and the current testing stack:

```go
go 1.24

require (
    github.com/stretchr/testify v1.10.0
    go.uber.org/goleak v1.3.0
)
```

Prefer the repo's existing test stack unless there is a clear reason to introduce something new.

## Core Workflow

1. **Identify** the System Under Test (SUT) and its dependencies
2. **Isolate** external dependencies — mock at the interface boundary
3. **Write** tests table-driven with `t.Run` subtests
4. **Assert** with testify `require` (stop on first failure) or `assert` (continue)
5. **Verify** goroutine lifecycle with `goleak.VerifyTestMain`
6. **Run** with `-race` and `-count=1` in CI

## Core Directives

### MUST DO

- Use table-driven tests with `t.Run` — every case needs a `name` field
- Use `t.Parallel()` inside subtests for independent cases
- Use `testify/require` for preconditions (stops test on failure) and `testify/assert` for regular assertions
- Use `t.Helper()` in all test helper functions
- Use `//go:build integration` for tests that need external services
- Use `goleak.VerifyTestMain(m)` in any package that spawns goroutines
- Mock at the interface boundary — mock interfaces, not concrete types
- Keep test files next to the source: `user.go` + `user_test.go`
- Use `testdata/` for fixture files; use `t.TempDir()` for temporary files
- Run tests with `-race ./...` in CI

### MUST NOT DO

- Write test logic that depends on test execution order
- Use `time.Sleep` to wait for async operations — use channels or `require.Eventually`
- Mock unexported functions or access unexported fields directly
- Put business-logic assertions in `TestMain` — use it only for setup/teardown
- Skip `t.Cleanup` or `defer` for resource teardown — leaks break other tests
- Use `os.Exit` in test code — it skips `t.Cleanup` and deferred calls
- Ignore `rows.Err()` or unchecked errors in test helpers
- Use real network calls, real clocks, or real file system paths in unit tests

## Category Index — When to Load Which Reference

| # | Category | Impact | Load when… | Reference |
|--:|----------|:------:|------------|-----------|
| 1 | Test Patterns | CRITICAL | Table-driven tests, subtests, parallel, test helpers | [`references/patterns.md`](references/patterns.md) |
| 2 | Assertions & testify | CRITICAL | require vs assert, error assertions, custom matchers | [`references/assertions.md`](references/assertions.md) |
| 3 | Mocking | CRITICAL | Interface mocks, gomock, testify/mock, fakes | [`references/mocking.md`](references/mocking.md) |
| 4 | Integration Tests | HIGH | Build tags, testcontainers, database tests, HTTP tests | [`references/integration.md`](references/integration.md) |
| 5 | Benchmarks | HIGH | Benchmark functions, b.Loop(), benchstat, profiling | [`references/benchmarks.md`](references/benchmarks.md) |
| 6 | Fuzzing | MEDIUM | Fuzz targets, seed corpus, crash reproduction | [`references/fuzzing.md`](references/fuzzing.md) |
| 7 | Coverage & CI | MEDIUM | Coverage commands, thresholds, CI configuration | [`references/coverage.md`](references/coverage.md) |

## Rule Index

### 1. Test Patterns (`test-`) — CRITICAL
`test-table-driven` · `test-parallel` · `test-helpers` · `test-goleak` · `test-integration-tags`

### 2. Assertions (`assert-`) — CRITICAL
`test-require-vs-assert`

### 3. Mocking (`mock-`) — HIGH
`test-mock-interface`

### 4. Async & Flake Prevention (`test-`) — HIGH
`test-no-sleep`

### 5. Reference-Only Topics
Benchmarks, fuzzing, coverage, integration infrastructure, and richer mocking tradeoffs live in `references/`. Load those references directly when the task needs them.

## Validation Checklist

- [ ] Tests are table-driven with named subtests using `t.Run`
- [ ] Independent subtests call `t.Parallel()`
- [ ] `testify/require` used for preconditions, `assert` for regular checks
- [ ] All test helpers call `t.Helper()` as first line
- [ ] Integration tests have `//go:build integration` tag
- [ ] Packages with goroutines have `goleak.VerifyTestMain` in `TestMain`
- [ ] Mocks target interfaces, not concrete types
- [ ] Resources cleaned up with `t.Cleanup` or `defer`
- [ ] No `time.Sleep` — use channels, `require.Eventually`, or context timeout
- [ ] Tests pass with `-race -count=1` (no cache, race detection)
- [ ] Coverage ≥ 80% on business logic packages
- [ ] Benchmark functions call `b.ReportAllocs()` and `b.ResetTimer()`
- [ ] `go test ./...` runs unit tests only; `-tags=integration` for integration tests

## External References

- [testing package](https://pkg.go.dev/testing)
- [testify](https://github.com/stretchr/testify)
- [gomock (uber-go/mock)](https://github.com/uber-go/mock)
- [goleak](https://github.com/uber-go/goleak)
- [testcontainers-go](https://testcontainers.com/guides/getting-started-with-testcontainers-for-go/)
- [Table Driven Tests](https://github.com/golang/go/wiki/TableDrivenTests)
- [Go Fuzzing](https://go.dev/doc/fuzz/)
