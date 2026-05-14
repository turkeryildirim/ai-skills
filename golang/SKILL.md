---
name: golang
description: Go (Golang) modern patterns, idiomatic code, concurrency, error handling, and toolchain best practices. Use when writing, reviewing, or auditing Go code. Triggers on "Go", "Golang", "goroutine", "channel", "Go module", "review Go", "Go best practices".
model: inherit
---

# Go Best Practices

Modern Go patterns, idiomatic code style, concurrency primitives, error handling, testing, and toolchain conventions. Rules for writing clean, performant, and maintainable Go code.

> "Clear is better than clever." — Go Proverbs

## Specialized Agents

| Agent | Role | Focus |
|-------|------|-------|
| **golang-pro** | Go Expert | Idiomatic Go, concurrency, performance, CLI/API design. |

## When to Use

Reference these guidelines when:
- Writing or reviewing Go code
- Designing packages, modules, or APIs
- Working with goroutines, channels, or the `sync` package
- Implementing error handling and wrapping
- Using generics (Go 1.18+)
- Writing tests with `testing`, `testify`, or table-driven tests
- Optimizing performance or memory usage
- Following Go toolchain conventions (`go fmt`, `go vet`, `golangci-lint`)
- Starting or structuring a new Go project
- Choosing libraries or managing dependencies

Use `golang-tester` alongside this skill when the task is primarily about authoring, restructuring, or debugging tests.

## Step 1: Detect Go Version

**Always check the project's Go version before giving advice.**

```bash
go version
```

Check `go.mod` for the module path and minimum Go version:
```
module github.com/example/app

go 1.22
```

### Feature Availability by Version

| Feature | Version |
|---------|---------|
| Modules | 1.11+ |
| Generics, `any` alias | 1.18+ |
| `slices`, `maps`, `cmp`, `log/slog`, `min`/`max` | 1.21+ |
| Range over integers, `math/rand/v2`, `cmp.Or` | 1.22+ |
| Range over func, `unique`, `iter` | 1.23+ |
| `weak.Pointer`, `os.Root`, `b.Loop()`, `t.Context()` | 1.24+ |
| `sync.WaitGroup.Go` | 1.25+ |
| `encoding/json/v2`, `modernize` linter in `go fix` | 1.26+ |

## Core Directives

### MUST DO

- Use `gofmt` / `goimports` — code must be formatted before review
- Declare errors as values; wrap with `fmt.Errorf("...: %w", err)` for context
- Return errors explicitly; never ignore them with `_`
- Log OR return errors — never both (single handling rule)
- Use table-driven tests with `t.Run` subtests
- Prefer small, focused interfaces (1–3 methods); accept interfaces, return concrete types
- Use `context.Context` as the first parameter for any function that does I/O or long work
- Initialise structs with named fields only (no positional)
- Always initialise slices and maps explicitly — never leave them nil
- Handle errors and edge cases first (early return); keep the happy path flat
- Keep error message strings low-cardinality — attach variable data as structured attributes
- Use `golangci-lint` for static analysis in CI
- Ask before adding a dependency — check stdlib first

### MUST NOT DO

- Use `panic` for expected error conditions
- Ignore errors with blank identifier (`_ = someCall()`)
- Use `init()` unless absolutely necessary
- Embed mutable state in value types; use pointer receivers for mutation
- Use naked returns in functions longer than a few lines
- Pass `nil` context; use `context.Background()` or `context.TODO()` instead
- Store `context.Context` in a struct field
- Use dot imports (`.`) in library code
- Write `else` after a block that ends with `return` / `break` / `continue`
- Write functions with more than 4 parameters — use an options struct instead
- Repeat the package name in an identifier (`http.HTTPClient` → `http.Client`)
- Put a real state (e.g. `StatusReady`) at `iota` 0 — use `StatusUnknown`
- Return a typed nil pointer as an interface — return `nil` explicitly
- Interpolate variable IDs/paths into error message strings (breaks APM grouping)

## Category Index — When to Load Which Reference

| # | Category | Impact | Load when… | Reference |
|--:|----------|:------:|------------|-----------|
| 1 | Best Practices & Naming | CRITICAL | Package design, naming, project layout | [`references/best-practices.md`](references/best-practices.md) |
| 2 | Naming (detailed) | CRITICAL | Naming decisions, common mistakes | [`references/naming.md`](references/naming.md) |
| 3 | Error Handling | CRITICAL | Errors, wrapping, single handling rule, slog | [`references/error-handling.md`](references/error-handling.md) |
| 4 | Concurrency | CRITICAL | Goroutines, channels, sync, data races | [`references/concurrency.md`](references/concurrency.md) |
| 5 | Safety | CRITICAL | nil traps, slice aliasing, numeric overflow | [`references/safety.md`](references/safety.md) |
| 6 | Code Style | HIGH | Control flow, function design, declarations | [`references/code-style.md`](references/code-style.md) |
| 7 | Design Patterns | HIGH | Functional options, resource management, streaming | [`references/design-patterns.md`](references/design-patterns.md) |
| 8 | Testing | HIGH | Unit tests, integration, mocks, goleak | [`references/testing.md`](references/testing.md) |
| 9 | Observability | HIGH | slog, Prometheus, OpenTelemetry, pprof | [`references/observability.md`](references/observability.md) |
| 10 | Performance | HIGH | Allocations, profiling, escape analysis | [`references/performance.md`](references/performance.md) |
| 11 | Security | HIGH | Input validation, crypto, secrets | [`references/security.md`](references/security.md) |
| 12 | Database | HIGH | database/sql, sqlx, pgx, transactions, connection pool | [`references/database.md`](references/database.md) |
| 13 | Context | HIGH | context propagation, cancellation, timeouts, context values | [`references/context.md`](references/context.md) |
| 14 | Data Structures | MEDIUM | slices, maps, container/, generics, copy semantics | [`references/data-structures.md`](references/data-structures.md) |
| 15 | Dependency Injection | MEDIUM | manual DI, wire, fx, samber/do, testing with DI | [`references/dependency-injection.md`](references/dependency-injection.md) |
| 16 | Project Layout | MEDIUM | New project, module naming, directory structure | [`references/project-layout.md`](references/project-layout.md) |
| 17 | Libraries | MEDIUM | Choosing a library or dependency | [`references/libraries.md`](references/libraries.md) |
| 18 | Dependency Management | MEDIUM | go mod, govulncheck, versioning | [`references/dependency-management.md`](references/dependency-management.md) |
| 19 | Linting | MEDIUM | golangci-lint config, nolint directives | [`references/linting.md`](references/linting.md) |
| 20 | Modernize | MEDIUM | Code upgrades, deprecated APIs, new idioms | [`references/modernize.md`](references/modernize.md) |

## Rule Index

### 1. Idiomatic Go (`idiomatic-`) — CRITICAL
`idiomatic-naming` · `idiomatic-no-stutter` · `idiomatic-struct-init` · `idiomatic-var-declarations` · `idiomatic-slice-map-init` · `idiomatic-blank-imports` · `idiomatic-file-organization` · `idiomatic-boolean-naming` · `idiomatic-constructor-naming` · `idiomatic-enum-zero-value`

### 2. Error Handling (`error-`) — CRITICAL
`error-wrap` · `error-panic-avoid` · `error-single-handling` · `error-low-cardinality`

### 3. Concurrency (`conc-`) — CRITICAL
`conc-goroutine-leak` · `conc-context-cancellation`

### 4. Safety (`safety-`) — CRITICAL
`safety-nil-interface`

### 5. Types & Interfaces (`type-`) — HIGH
`type-small-interfaces`

### 6. Code Style (`style-`) — HIGH
`style-early-return` · `style-no-else` · `style-switch-over-if` · `style-complex-conditions` · `style-line-breaking` · `style-function-design` · `style-value-vs-pointer` · `style-string-handling` · `style-functional-options`

### 7. Testing (`test-`) — HIGH
`test-table-driven` · `test-goleak` · `test-integration-tags`

For parallel subtests, helpers, async assertions, mocking, and benchmark-specific guidance, load `golang-tester`.

### 8. Performance (`perf-`) — MEDIUM
`perf-prealloc`

### 9. Reference-Only Topics
Security, database, dependency-management, context deep-dives, and modernization guidance currently live in `references/` rather than standalone `rules/` files. Load those references directly when the task needs them.

## Validation Checklist

- [ ] Code is formatted with `gofmt` / `goimports`
- [ ] All errors are explicitly handled (no `_ = err`)
- [ ] Errors are wrapped with `%w` to preserve the chain
- [ ] Errors are handled once — logged OR returned, never both
- [ ] Error message strings are low-cardinality (no interpolated IDs/paths)
- [ ] No typed nil returned as an interface — use explicit `nil`
- [ ] Goroutines have clear ownership and lifecycle management
- [ ] `context.Context` is threaded through all I/O paths
- [ ] Interfaces are small and defined at the point of use
- [ ] Slices and maps are explicitly initialised (never nil)
- [ ] Functions have ≤4 parameters; options structs used otherwise
- [ ] No `else` after a block ending with `return`/`break`/`continue`
- [ ] No package-name stuttering in exported identifiers
- [ ] Enum iota starts with Unknown/Invalid sentinel at 0
- [ ] Constructors use `New()` for single-type packages
- [ ] Tests are table-driven and use `t.Run`
- [ ] Integration tests use `//go:build integration` tag
- [ ] Packages with goroutines use `goleak.VerifyTestMain`
- [ ] `golangci-lint` passes with no new warnings
- [ ] `govulncheck ./...` passes before release
- [ ] No use of `panic` for expected runtime errors

## External References

- [Go Documentation](https://go.dev/doc/)
- [Effective Go](https://go.dev/doc/effective_go)
- [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments)
- [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md)
- [Go Proverbs](https://go-proverbs.github.io)
- [golangci-lint](https://golangci-lint.run)
- [Awesome Go](https://github.com/avelino/awesome-go)
