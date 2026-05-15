---
title: Go Dependency and Interface Management
impact: MEDIUM
impactDescription: "Oversized interfaces and tight package coupling prevent testing and reduce reusability"
tags: golang, interfaces, dependency-injection, go-modules, coupling, testability
---

## Go Dependency and Interface Management

**Impact: MEDIUM (Oversized interfaces and tight package coupling prevent testing and reduce reusability)**

Go's interface system is implicit — any type that satisfies the method set implements the interface. This means interfaces should be small and defined where they are consumed, not where they are produced. Poor interface and dependency design manifests as untestable code and tightly coupled packages.

## Incorrect

```go
// ❌ Large "God interface" defined in the implementation package
// internal/userservice/user_service.go
type UserService interface {
    GetUser(ctx context.Context, id string) (*User, error)
    CreateUser(ctx context.Context, req CreateUserRequest) (*User, error)
    UpdateUser(ctx context.Context, id string, req UpdateUserRequest) (*User, error)
    DeleteUser(ctx context.Context, id string) error
    ListUsers(ctx context.Context, page int) ([]User, error)
    SearchUsers(ctx context.Context, query string) ([]User, error)
    SendWelcomeEmail(ctx context.Context, id string) error  // ❌ mixed responsibility
    ExportToCSV(ctx context.Context) ([]byte, error)         // ❌ mixed responsibility
}

// ❌ Concrete type dependency — cannot mock in tests
type OrderHandler struct {
    svc *userservice.UserServiceImpl  // ❌ concrete, not interface
}
```

## Correct

```go
// ✅ Small, focused interface defined at the consumer side
// internal/handler/user_handler.go

// UserGetter is the only capability the handler needs
type UserGetter interface {
    GetUser(ctx context.Context, id string) (*domain.User, error)
}

type UserHandler struct {
    getter UserGetter  // ✅ interface, easily mocked in tests
}

// ✅ Each consumer defines only what it needs
// internal/notifier/welcome.go
type UserEmailer interface {
    GetEmail(ctx context.Context, id string) (string, error)
}
```

```go
// ✅ go.mod — clean, no local replace directives in production code
module github.com/myorg/myapp

go 1.22

require (
    github.com/go-chi/chi/v5 v5.0.12
    github.com/jackc/pgx/v5  v5.5.5
    go.uber.org/zap           v1.27.0
)

// ❌ Red flag in go.mod:
// replace github.com/myorg/shared => ../shared  ← must not be in production commits
```

## Interface Discipline Assessment

```
HIGH violations:
├── Interface with >5 methods used as a dependency (should be split)
├── Concrete struct dependency (not interface) in handler/service constructors
└── Interface defined in the producer package — Go convention is consumer-side

MEDIUM violations:
├── Any-typed parameters/returns: func Process(data interface{}) interface{}
├── Empty interface (any) used as a map value when a typed struct would work
└── Single large "service interface" tested via the concrete implementation

LOW violations:
├── Unused exported interface in a package (interface pollution)
└── Interface method names do not follow Go naming (no "I" prefix, short verb names)
```

## go.mod Health Checklist

```
✅ Healthy go.mod signals:
- go directive is recent (1.21+)
- No 'replace' directives (or only documented dev ones)
- Minimal indirect dependencies in direct require block
- go.sum committed alongside go.mod

❌ Warning signals:
- replace directives pointing to local paths   → forgotten from dev
- require indirect entries outnumber direct    → dependency audit needed
- No go.sum committed                          → reproducible builds broken
- Multiple major versions of same library      → version conflict
```

## Why

- **Implicit interfaces**: Unlike Java, Go types don't declare interface implementation — small interfaces defined at the consumer side allow test doubles without code generation
- **`internal/` for interfaces**: Defining a `Repository` interface in `internal/domain/` means both the service and a mock can satisfy it without either importing the other
- **Testability**: A handler that depends on a `UserGetter` interface can be unit tested with a two-line fake — a handler that imports the concrete service requires wiring the full dependency graph
