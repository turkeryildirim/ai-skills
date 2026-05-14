# Go Best Practices

Idiomatic Go patterns, package design, naming conventions, and project layout. Rules for writing clear, maintainable Go code.

## When to Load

- Designing new packages or modules
- Reviewing package structure or naming
- Making architectural decisions
- Onboarding to a Go codebase

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Naming & Conventions | CRITICAL | `idiomatic-` |
| 2 | Package Design | CRITICAL | `pkg-` |
| 3 | Interface Design | HIGH | `type-` |

## Rule Index

### 1. Naming & Conventions (CRITICAL)

- [`idiomatic-naming`](../rules/idiomatic-naming.md) — MixedCaps, not underscores; unexported = lowercase
- [`idiomatic-struct-init`](../rules/idiomatic-struct-init.md) — Always use named fields in struct literals
- `receiver names` — Keep receiver names short and consistent (`u *User`, `s *Service`)
- `package names` — Use lowercase, concise names that read well at the call site
- `exported docs` — Every exported symbol should have a doc comment
- `init() avoidance` — Prefer explicit initialisation over hidden startup behavior

### 2. Interface Design (HIGH)

- [`type-small-interfaces`](../rules/type-small-interfaces.md) — Prefer 1–3 method interfaces
- `accept interfaces, return concrete types` — Define interfaces at the consumer boundary
- `zero-value usability` — Types should be safe and unsurprising before extra setup
- `embedding` — Use embedding for behavior composition, not inheritance

## Key Principles

### Project Layout

Follow the standard Go project layout:
```
myapp/
  cmd/          # main packages (one per binary)
    myapp/
      main.go
  internal/     # private packages (not importable externally)
  pkg/          # public packages (importable by external code)
  go.mod
  go.sum
```

### Package Design

- **One purpose per package** — a package should do one thing well
- **Name from the caller's perspective** — `http.Client`, not `http.HTTPClient`
- Avoid `util`, `common`, `helpers` package names — they become dumping grounds
- Prefer many small packages over one large package

### The `internal` Package

Use `internal/` to prevent external packages from importing your private code:
```
myapp/internal/database/  ← cannot be imported outside myapp module
```

### References

- [Effective Go](https://go.dev/doc/effective_go)
- [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments)
- [Standard Go Project Layout](https://github.com/golang-standards/project-layout)
- [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md)
