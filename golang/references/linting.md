# Go Linting

`golangci-lint` configuration, essential linters, nolint directives, and workflow integration.

## When to Load

- Setting up linting for a new project
- Configuring `.golangci.yml`
- Running or interpreting lint output
- Adding a `//nolint` suppression

## Core Tool: golangci-lint

`golangci-lint` aggregates 100+ linters into one binary with a unified configuration file. Every Go project MUST have a `.golangci.yml` as the single source of truth.

```bash
golangci-lint run ./...            # run all configured linters
golangci-lint run --fix ./...      # auto-correct where possible
golangci-lint fmt ./...            # format code
golangci-lint linters              # list available linters
```

## Recommended .golangci.yml

```yaml
run:
  timeout: 5m
  go: "1.22"

linters:
  enable:
    # Correctness
    - errcheck       # unchecked errors
    - govet          # suspicious constructs (go vet)
    - staticcheck    # comprehensive static analysis
    - gosimple       # simplify code
    - ineffassign    # detect unused assignments

    # Style & Idioms
    - revive         # exported docs, receiver naming, stuttering
    - gocritic       # style issues, unnecessary else
    - misspell       # typos
    - predeclared    # shadows builtins
    - errname        # error naming conventions

    # Complexity
    - gocognit       # cognitive complexity
    - cyclop         # cyclomatic complexity

    # Security
    - gosec          # OWASP-based security checks

    # Testing
    - thelper        # t.Helper() usage
    - paralleltest   # t.Parallel() missing
    - testifylint    # testify usage correctness

    # Performance
    - prealloc       # missing slice pre-allocation

linters-settings:
  revive:
    rules:
      - name: exported
        severity: warning
      - name: receiver-naming
        severity: warning
  gocognit:
    min-complexity: 15
  cyclop:
    max-complexity: 10
  gosec:
    excludes:
      - G304  # file path from variable (review case by case)

issues:
  exclude-rules:
    - path: "_test.go"
      linters:
        - gocritic
        - gocognit
```

## Suppressing Warnings

Use `//nolint` with the specific linter name AND a justification comment. The `nolintlint` linter enforces this.

```go
// Bad — no linter name, no reason
result, _ := riskyOperation() //nolint

// Bad — linter named but no reason
result, _ := riskyOperation() //nolint:errcheck

// Good — specific linter + reason
result, _ := riskyOperation() //nolint:errcheck // fire-and-forget: logging error is handled upstream

// Good — multiple linters
func init() { //nolint:gochecknoinits // required by plugin registration interface
    registerPlugin()
}
```

## Linter Purpose Map

| Linter | Category | What it catches |
|---|---|---|
| `errcheck` | Correctness | Unchecked error returns |
| `govet` | Correctness | printf format mismatches, unreachable code |
| `staticcheck` | Correctness | SA*, S*, ST*, QF* checks |
| `gosimple` | Style | Simplifiable expressions |
| `revive` | Naming | Exported docs, stuttering, receiver names |
| `gocritic` | Style | Unnecessary else, inefficient patterns |
| `errname` | Naming | `ErrFoo` variables, `FooError` types |
| `misspell` | Quality | Typos in strings and comments |
| `gosec` | Security | SQL injection, hardcoded creds, weak crypto |
| `prealloc` | Performance | Missing `make([]T, 0, n)` |
| `thelper` | Testing | Missing `t.Helper()` in helpers |
| `paralleltest` | Testing | Missing `t.Parallel()` |
| `testifylint` | Testing | Incorrect testify assertion usage |
| `exhaustive` | Correctness | Unhandled switch cases for enums |

## Development Workflow

1. **During development**: Run `golangci-lint run --fix ./...` after significant changes
2. **Before commit**: Run `golangci-lint fmt ./...` then `golangci-lint run ./...`
3. **Legacy code**: Adopt incrementally using `issues.new-from-rev` to only lint changed lines:

```yaml
issues:
  new-from-rev: HEAD~10  # only report issues in lines changed since this commit
```

4. **CI**: Run with `--out-format=colored-line-number` for readable output; fail on any new issue

## Reading Lint Output

```
./internal/user/service.go:42:9: SA4006: this value of `err` is never used (staticcheck)
│                              │   │       └── message
│                              │   └── linter name
│                              └── column
└── file:line
```

## References

- [golangci-lint](https://golangci-lint.run)
- [golangci-lint linters list](https://golangci-lint.run/usage/linters/)
- [staticcheck](https://staticcheck.io)
- [gosec](https://github.com/securego/gosec)
