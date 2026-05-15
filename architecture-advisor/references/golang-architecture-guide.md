---
name: golang-architecture-guide
description: Go architecture pattern benchmarks (Standard Layout, Clean Architecture, domain-driven), concurrency models, interface design, and common anti-patterns for architectural analysis.
type: reference
---

# Go Architecture Guide

Reference for analyzing Go (Golang) projects — CLI tools, web services, gRPC backends, and libraries.

## Maturity Levels

| Level | Signals |
|-------|---------|
| **Level 1** | All logic in `main.go`, no folder structure, global variables |
| **Level 2** | Some packages, but business logic in HTTP handlers |
| **Level 3** | Handler → Service → Repository separation, interfaces used |
| **Level 4** | `internal/` boundaries enforced, context propagated, tests with mocks |
| **Level 5** | Clean/Hexagonal layout, dependency injection, goroutine lifecycle managed, >70% coverage |

---

## Layout Pattern Comparison

### Flat Package (Appropriate: small tools, scripts)
```
myapp/
├── main.go
├── handler.go
├── service.go
└── go.mod

✅ Acceptable for: CLI tools, single-purpose services <500 LOC
❌ Problem when: growing service has 20+ .go files in root, circular logic
```

### Standard Layout (Recommended: web services, multi-binary)
```
myapp/
├── cmd/
│   ├── api/main.go          → HTTP server binary
│   └── worker/main.go       → Background worker binary
├── internal/
│   ├── domain/              → Entities + interfaces (no framework imports)
│   ├── handler/             → HTTP handlers (net/http, gin, chi, echo)
│   ├── service/             → Business logic
│   ├── repository/          → Data access (sqlx, gorm, pgx)
│   └── config/              → Env config struct + validation
├── pkg/
│   └── pagination/          → Reusable utility, safe to export
├── migrations/              → SQL migration files
├── go.mod
└── Makefile
```

### Domain-Driven Layout (Recommended: large services, bounded contexts)
```
myapp/
├── cmd/api/main.go
├── internal/
│   ├── orders/              → Bounded context: own handler, service, repository
│   │   ├── handler.go
│   │   ├── service.go
│   │   ├── repository.go
│   │   └── domain.go
│   ├── users/
│   └── shared/              → Cross-cutting: logger, config, DB connection
└── go.mod
```

---

## Framework Assessment

### net/http (stdlib)
```
✅ Preferred for: simple services, maximum portability, no external deps
Detection: http.HandleFunc / http.NewServeMux
Watch for: no middleware chaining, auth/logging duplicated in handlers
```

### Chi
```
✅ Preferred for: idiomatic stdlib-compatible router with middleware
Detection: github.com/go-chi/chi in go.mod
Healthy: r.Use(middleware.Logger), r.Group() for versioned routes
Watch for: missing middleware, all routes registered in main.go
```

### Gin
```
✅ Common for: teams coming from Express/Laravel background
Detection: github.com/gin-gonic/gin in go.mod
Watch for: c.JSON inside service layer (HTTP types leaking), no error middleware
```

### gRPC
```
✅ For: internal microservices, streaming, strict contracts
Detection: google.golang.org/grpc, *.proto files
Healthy: generated code in gen/, business logic in internal/
Watch for: proto types used as domain entities (should map to internal types)
```

---

## Error Handling Patterns

### Error Wrapping (Required Go 1.13+)
```go
// ✅ Wrap with context, preserve chain
if err != nil {
    return fmt.Errorf("getUserByID %s: %w", id, err)
}

// ✅ Check error type
if errors.Is(err, sql.ErrNoRows) {
    return nil, domain.ErrNotFound
}

var pgErr *pgconn.PgError
if errors.As(err, &pgErr) && pgErr.Code == "23505" {
    return nil, domain.ErrAlreadyExists
}

// ❌ Avoid: string comparison on errors
if err.Error() == "sql: no rows in result set" { ... }  // breaks with wrapping
```

### Sentinel Errors
```go
// ✅ Domain-level sentinel errors in internal/domain/errors.go
var (
    ErrNotFound      = errors.New("not found")
    ErrAlreadyExists = errors.New("already exists")
    ErrUnauthorized  = errors.New("unauthorized")
)

// Handler maps domain errors to HTTP status
switch {
case errors.Is(err, domain.ErrNotFound):      http.Error(w, "not found", 404)
case errors.Is(err, domain.ErrUnauthorized):   http.Error(w, "unauthorized", 401)
default:                                        http.Error(w, "internal error", 500)
}
```

---

## Testing Architecture Benchmarks

```
✅ Healthy test layout:
internal/service/user_service_test.go   → unit tests with mock repository
internal/handler/user_handler_test.go   → httptest.NewRecorder(), mock service
internal/repository/user_repo_test.go   → integration tests (//go:build integration)

Test naming:
func TestGetUser_NotFound(t *testing.T)
func TestGetUser_Success(t *testing.T)
func TestGetUser/valid_id, missing_id  (table-driven sub-tests)

✅ Mock patterns:
- Interfaces defined in domain/ or at consumer
- Manual fakes for simple cases
- mockery / gomock for generated mocks

❌ Warning signals:
- No _test.go files
- Tests only in main package
- Tests require a running database (no interface mocking)
- TestMain with real DB for unit tests (use integration build tag)
```

---

## Common Anti-Patterns

| Anti-Pattern | Signs | Impact |
|-------------|-------|--------|
| **God main.go** | >200 lines, SQL + HTTP + business logic | Untestable, cannot add binaries |
| **Goroutine leak** | `go func()` with no ctx or done channel | Silent memory/connection exhaustion |
| **Missing context** | `context.Background()` in handlers | Ignores client cancellations |
| **Interface in producer** | Interface defined next to its implementation | Forces import of implementation package |
| **Global DB variable** | `var db *sql.DB` at package level | Cannot test without real DB, race-prone |
| **panic for errors** | `panic("user not found")` | Crashes server; use error return |
| **Unused dependencies** | `go.mod` with packages not imported | Bloats binary, security surface |
| **`replace` in production** | `replace` directives in committed go.mod | Breaks reproducible builds in CI |
