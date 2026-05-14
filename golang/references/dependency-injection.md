# Dependency Injection in Go

Building testable, loosely coupled applications by passing dependencies rather than hardcoding them.

## When to Load

- Designing service architecture or composition root
- Setting up a new DI container or wiring services
- Refactoring tightly coupled code with global variables or `init()`
- Choosing between manual injection and a DI library

## Core Rules

1. Dependencies MUST be injected via constructors — NEVER use global variables or `init()` for service setup
2. Small projects (< 10 services) SHOULD use manual constructor injection — no library needed
3. Interfaces MUST be defined where consumed, not where implemented — accept interfaces, return structs
4. NEVER use global registries or package-level service locators
5. The DI container MUST only exist at the composition root (`main()` or app startup) — NEVER pass the container as a dependency
6. Mock at the interface boundary — DI makes this trivial
7. Keep the dependency graph shallow — deep chains signal design problems

## Why Dependency Injection?

| Problem without DI | How DI solves it |
|---|---|
| Functions create their own dependencies | Dependencies are injected — swap implementations freely |
| Testing requires real databases, APIs | Pass mock implementations in tests |
| Changing one component breaks others | Loose coupling via interfaces |
| Services initialized in `init()` everywhere | Centralized wiring at startup |
| All services loaded at startup | Lazy loading — services created only when first requested |

## Manual Constructor Injection

For small projects, pass dependencies through constructors — no library needed.

```go
// Good — explicit dependencies, testable
type UserService struct {
    db     UserStore
    mailer Mailer
    logger *slog.Logger
}

func NewUserService(db UserStore, mailer Mailer, logger *slog.Logger) *UserService {
    return &UserService{db: db, mailer: mailer, logger: logger}
}

// Interfaces defined at the point of use (in this package, not in postgres/)
type UserStore interface {
    FindByID(ctx context.Context, id string) (*User, error)
    Create(ctx context.Context, user *User) error
}

type Mailer interface {
    Send(ctx context.Context, to, subject, body string) error
}
```

```go
// main.go — composition root
func main() {
    logger := slog.Default()
    db := postgres.NewUserStore(connStr)
    mailer := smtp.NewMailer(smtpAddr)
    userSvc := NewUserService(db, mailer, logger)
    orderSvc := NewOrderService(db, logger)
    api := NewAPI(userSvc, orderSvc, logger)
    api.ListenAndServe(":8080")
}
```

```go
// Bad — hardcoded dependencies, untestable
type UserService struct{ db *sql.DB }

func NewUserService() *UserService {
    db, _ := sql.Open("postgres", os.Getenv("DATABASE_URL")) // hidden!
    return &UserService{db: db}
}
```

When to graduate from manual DI:
- 15+ services with cross-dependencies
- Need lifecycle management (health checks, graceful shutdown)
- Need lazy initialization
- Wiring order becomes fragile

## DI Library Decision Table

| Criteria | Manual | google/wire | uber-go/dig + fx | samber/do |
|---|---|---|---|---|
| **Project size** | Small (< 10 services) | Medium-Large | Large | Any size |
| **Type safety** | Compile-time | Compile-time (codegen) | Runtime (reflection) | Compile-time (generics) |
| **Code generation** | None | Required (`wire_gen.go`) | None | None |
| **Lazy loading** | Manual | No (all eager) | Built-in (fx) | Built-in |
| **Graceful shutdown** | Manual | Manual | Built-in (fx) | Built-in |
| **Learning curve** | None | Medium | High | Low |

## Quick Comparison: Four Approaches

The dependency graph: `Config → Database → UserStore → UserService → API`

**Manual:**
```go
cfg := NewConfig()
db := NewDatabase(cfg)
store := NewUserStore(db)
svc := NewUserService(store)
api := NewAPI(svc)
api.Run()
```

**google/wire** (compile-time codegen):
```go
// wire.go — then run: wire ./...
func InitializeAPI() (*API, error) {
    wire.Build(NewConfig, NewDatabase, NewUserStore, NewUserService, NewAPI)
    return nil, nil
}
```

**uber-go/fx** (reflection-based):
```go
app := fx.New(
    fx.Provide(NewConfig, NewDatabase, NewUserStore, NewUserService),
    fx.Invoke(func(api *API) { api.Run() }),
)
app.Run()
```

**samber/do** (generics-based, no codegen):
```go
i := do.New()
do.Provide(i, NewConfig)
do.Provide(i, NewDatabase)   // auto shutdown + health check
do.Provide(i, NewUserStore)
do.Provide(i, NewUserService)
api := do.MustInvoke[*API](i)
defer i.Shutdown()           // cleans up all services
api.Run()
```

## samber/do — Lifecycle Management

`samber/do` provides compile-time type safety via generics and built-in lifecycle hooks:

```go
import "github.com/samber/do/v2"

// Service with shutdown hook
func NewDatabase(i do.Injector) (*sql.DB, error) {
    db, err := sql.Open("pgx", os.Getenv("DATABASE_URL"))
    if err != nil {
        return nil, err
    }
    // Register shutdown hook
    do.RegisterShutdown(i, func() error {
        return db.Close()
    })
    return db, nil
}

// Health-checkable service — implement do.Healthcheckable
type Server struct{ db *sql.DB }

func (s *Server) HealthCheck() error {
    return s.db.PingContext(context.Background())
}
```

### Container cloning for tests

```go
func TestUserService(t *testing.T) {
    // Clone the production container, override just what you need
    testContainer := do.Package(
        do.Scope("test"),
        do.Override[UserStore](func(i do.Injector) (UserStore, error) {
            return &MockUserStore{}, nil
        }),
    )

    i := do.New(testContainer)
    defer i.Shutdown()

    svc := do.MustInvoke[*UserService](i)
    // test with real dependencies except UserStore
}
```

## Testing with DI

DI makes testing straightforward — inject mocks instead of real implementations:

```go
type MockUserStore struct {
    users map[string]*User
}

func (m *MockUserStore) FindByID(ctx context.Context, id string) (*User, error) {
    u, ok := m.users[id]
    if !ok {
        return nil, sql.ErrNoRows
    }
    return u, nil
}

func TestUserService_GetUser(t *testing.T) {
    store := &MockUserStore{
        users: map[string]*User{"1": {ID: "1", Name: "Alice"}},
    }
    svc := NewUserService(store, &MockMailer{}, slog.Default())

    user, err := svc.GetUser(context.Background(), "1")
    require.NoError(t, err)
    assert.Equal(t, "Alice", user.Name)
}
```

## Anti-Patterns

```go
// Bad — service locator: container passed as a parameter
func NewUserService(container Container) *UserService {
    db := container.Get("db").(*sql.DB)   // hidden dependencies
    // ...
}

// Bad — global registry
var services = make(map[string]any)
func Register(name string, svc any) { services[name] = svc }

// Bad — init() service setup
func init() {
    globalDB, _ = sql.Open("postgres", os.Getenv("DB_URL"))
}
```

## References

- [samber/do](https://github.com/samber/do)
- [google/wire](https://github.com/google/wire)
- [uber-go/fx](https://github.com/uber-go/fx)
- [Dependency Injection in Go — Dave Cheney](https://dave.cheney.net/2016/11/13/do-not-design-for-testability)
