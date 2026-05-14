# Go Libraries and Frameworks

Production-ready library recommendations by category. Standard library first — only reach for external libs when they provide clear value.

## When to Load

- Choosing a library for a specific task
- Comparing alternatives for a new dependency
- Adding a new dependency to a project

## Core Philosophy

1. **Standard library first** — Go's stdlib is excellent and sufficient for many use cases
2. **Maturity** — check maintenance status, license, and community adoption before recommending
3. **Simplicity** — simpler solutions are usually better in Go
4. **Dependency cost** — more dependencies = more attack surface and maintenance burden

More libraries: https://github.com/avelino/awesome-go

---

## Web Frameworks

| Library | Use when |
|---|---|
| **`net/http`** (stdlib) | Simple APIs, when you control the full stack |
| **[Gin](https://github.com/gin-gonic/gin)** | High-performance REST APIs, familiar Express-like API |
| **[Echo](https://github.com/labstack/echo)** | Clean middleware system, REST APIs and web apps |
| **[Chi](https://github.com/go-chi/chi)** | Lightweight idiomatic router, composes with `net/http` |
| **[Fiber](https://github.com/gofiber/fiber)** | Very fast, Node.js/Express developers transitioning to Go |

## HTTP Clients

| Library | Use when |
|---|---|
| **`net/http`** (stdlib) | Standard HTTP calls |
| **[Resty](https://github.com/go-resty/resty)** | API consumption with retry support, fluent API |
| **[Req](https://github.com/imroc/req)** | Minimal code for common patterns |

## ORM & Database

| Library | Use when |
|---|---|
| **`database/sql`** (stdlib) | Direct SQL, maximum control |
| **[sqlx](https://github.com/jmoiron/sqlx)** | Thin stdlib extension, type-safe query helpers |
| **[sqlc](https://github.com/sqlc-dev/sqlc)** | Generate type-safe Go from SQL — compiler-checked queries |
| **[GORM](https://github.com/go-gorm/gorm)** | Feature-complete ORM, auto-migrations, associations |
| **[Ent](https://github.com/ent/ent)** | Code-generated type-safe ORM, complex graph queries |

## Database Drivers

| Driver | Database |
|---|---|
| **[pgx](https://github.com/jackc/pgx)** | PostgreSQL — faster than lib/pq, full feature support |
| **[lib/pq](https://github.com/lib/pq)** | PostgreSQL — mature, widely used |
| **[go-sql-driver/mysql](https://github.com/go-sql-driver/mysql)** | MySQL |
| **[go-redis](https://github.com/redis/go-redis)** | Redis — cluster support, modern features |
| **[mongo-go-driver](https://github.com/mongodb/mongo-go-driver)** | MongoDB — official driver |

## Schema Migrations

| Library | Use when |
|---|---|
| **[golang-migrate](https://github.com/golang-migrate/migrate)** | SQL migrations, multiple databases |
| **[goose](https://github.com/pressly/goose)** | SQL or Go migrations, simple API |

## Testing

| Library | Use when |
|---|---|
| **`testing`** (stdlib) | Always — all tests start here |
| **[testify](https://github.com/stretchr/testify)** | Assertions (`assert`/`require`), mocking, suites |
| **[gomock](https://github.com/uber-go/mock)** | Interface mocks with code generation |
| **[testcontainers-go](https://golang.testcontainers.org)** | Integration tests with real Docker dependencies |
| **[goleak](https://github.com/uber-go/goleak)** | Goroutine leak detection in tests |
| **[go-sqlmock](https://github.com/DATA-DOG/go-sqlmock)** | Mock database/sql without a real DB |

## CLI & Configuration

| Library | Use when |
|---|---|
| **[Cobra](https://github.com/spf13/cobra)** | CLI applications — subcommands, flags, auto-generated docs |
| **[Viper](https://github.com/spf13/viper)** | Configuration — works with Cobra, JSON/YAML/TOML/env |
| **[env](https://github.com/caarlos0/env)** | Parse env vars into structs, simple and type-safe |
| **[Koanf](https://github.com/knadh/koanf)** | Lightweight multi-source config (JSON/YAML/TOML/env) |

## Logging

| Library | Use when |
|---|---|
| **`log/slog`** (stdlib, Go 1.21+) | Structured logging — prefer this over external libs |
| **[Zap](https://github.com/uber-go/zap)** | Ultra-high performance, zero-allocation hot paths |
| **[Zerolog](https://github.com/rs/zerolog)** | Zero-allocation JSON logging, simple API |

## Error Handling

| Library | Use when |
|---|---|
| **`errors`** (stdlib) | Standard error creation, `Is`/`As`/`Join` |
| **`fmt`** (stdlib) | `fmt.Errorf("...: %w", err)` for wrapping |
| **[samber/oops](https://github.com/samber/oops)** | Production errors needing stack traces, user context, structured attributes |

## Validation

| Library | Use when |
|---|---|
| **[go-playground/validator](https://github.com/go-playground/validator)** | Struct validation with tags, cross-field rules |
| **[ozzo-validation](https://github.com/go-ozzo/ozzo-validation)** | Code-based validation rules, no struct tags |

## Authentication & Authorization

| Library | Use when |
|---|---|
| **[golang-jwt/jwt](https://github.com/golang-jwt/jwt)** | JWT creation and validation |
| **[Casbin](https://github.com/casbin/casbin)** | ACL / RBAC / ABAC policy-based authorization |
| **`golang.org/x/oauth2`** | OAuth2 client |

## Caching

| Library | Use when |
|---|---|
| **[Ristretto](https://github.com/dgraph-io/ristretto)** | High-performance memory-bound cache |
| **[BigCache](https://github.com/allegro/bigcache)** | Gigabytes of cached data, high throughput |
| **[go-cache](https://github.com/patrickmn/go-cache)** | Simple in-memory key/value with expiration |

## Messaging

| Library | Use when |
|---|---|
| **[franz-go](https://github.com/twmb/franz-go)** | Kafka — modern, high-performance |
| **[amqp091-go](https://github.com/rabbitmq/amqp091-go)** | RabbitMQ — official client |
| **[nats.go](https://github.com/nats-io/nats.go)** | NATS — simple, fast messaging |
| **[Temporal Go SDK](https://github.com/temporalio/sdk-go)** | Durable execution, long-running workflows |

## Metrics & Observability

| Library | Use when |
|---|---|
| **[prometheus/client_golang](https://github.com/prometheus/client_golang)** | Prometheus metrics |
| **[opentelemetry-go](https://github.com/open-telemetry/opentelemetry-go)** | Distributed tracing, metrics, logs (OpenTelemetry) |

## Dependency Injection

| Library | Use when |
|---|---|
| Manual constructors | Small projects — simplest, no magic |
| **[samber/do](https://github.com/samber/do)** | Runtime DI with service locator, health checks |
| **[google/wire](https://github.com/google/wire)** | Compile-time DI, no reflection |
| **[uber-go/fx](https://github.com/uber-go/fx)** | Application framework with lifecycle + DI |

## Functional Utilities

| Library | Use when |
|---|---|
| **`slices`** (stdlib, Go 1.21+) | Slice operations — prefer over lo for basic needs |
| **`maps`** (stdlib, Go 1.21+) | Map operations |
| **[samber/lo](https://github.com/samber/lo)** | Advanced: filter, group-by, chunk, flatten |
| **[samber/mo](https://github.com/samber/mo)** | Functional patterns: Option, Either, Try |

## API Documentation

| Library | Use when |
|---|---|
| **[swag](https://github.com/swaggo/swag)** | Auto-generate OpenAPI/Swagger from comment annotations |

## gRPC & GraphQL

| Library | Use when |
|---|---|
| **[grpc-go](https://github.com/grpc/grpc-go)** | gRPC services |
| **[gqlgen](https://github.com/99designs/gqlgen)** | GraphQL — schema-first, type-safe code generation |

## Standard Library New Packages (Prefer These)

| Package | Since | Purpose |
|---|---|---|
| `slices` | Go 1.21 | Generic slice operations |
| `maps` | Go 1.21 | Generic map operations |
| `cmp` | Go 1.21 | Comparison utilities |
| `log/slog` | Go 1.21 | Structured logging |
| `iter` | Go 1.23 | Range-over-func iterators |
| `unique` | Go 1.23 | Value canonicalization |
| `math/rand/v2` | Go 1.22 | Improved random (auto-seeded) |
| `weak` | Go 1.24 | Weak references for caches |
