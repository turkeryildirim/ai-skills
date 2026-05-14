# Go Integration Tests

Build tags, testcontainers, database tests, HTTP handler tests, and goroutine leak detection.

## Build Tags

Integration tests MUST use a build tag to prevent them running with `go test ./...`:

```go
//go:build integration

package order_test

import (
    "testing"
    "github.com/stretchr/testify/require"
)

func TestCreateOrder_WithRealDatabase(t *testing.T) {
    db := setupTestDB(t)
    repo := NewOrderRepository(db)

    order, err := repo.Create(t.Context(), testOrder)
    require.NoError(t, err)
    require.NotEmpty(t, order.ID)
}
```

```bash
go test ./...                       # unit tests only (no build tag)
go test -tags=integration ./...     # includes integration tests
go test -tags=integration -race ./... # integration + race detector
```

## Goroutine Leak Detection

Add `goleak.VerifyTestMain` to any package that spawns goroutines:

```go
package order_test

import (
    "testing"
    "go.uber.org/goleak"
)

func TestMain(m *testing.M) {
    // Catches goroutine leaks across all tests in the package
    goleak.VerifyTestMain(m)
}

// Per-test — when a specific test exercises goroutines
func TestWorkerPool(t *testing.T) {
    defer goleak.VerifyNone(t)

    pool := NewWorkerPool(10)
    pool.Start()
    defer pool.Stop() // must clean up before VerifyNone runs

    // test logic ...
}
```

Ignoring known background goroutines:

```go
func TestMain(m *testing.M) {
    goleak.VerifyTestMain(m,
        goleak.IgnoreTopFunction("net/http.(*Server).Serve"),
        goleak.IgnoreCurrent(), // ignore goroutines running at test start
    )
}
```

## HTTP Handler Tests

Use `httptest` — no external services needed, part of stdlib.

### httptest.NewRecorder — In-Process Handler Test

```go
func TestCreateUserHandler(t *testing.T) {
    t.Parallel()

    tests := []struct {
        name       string
        body       string
        wantStatus int
        wantName   string
    }{
        {
            name:       "creates user with valid input",
            body:       `{"name":"Alice","email":"alice@example.com"}`,
            wantStatus: http.StatusCreated,
            wantName:   "Alice",
        },
        {
            name:       "returns 400 for missing email",
            body:       `{"name":"Alice"}`,
            wantStatus: http.StatusBadRequest,
        },
        {
            name:       "returns 400 for empty body",
            body:       `{}`,
            wantStatus: http.StatusBadRequest,
        },
    }

    handler := NewUserHandler(newFakeUserService())

    for _, tt := range tests {
        tt := tt
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()

            req := httptest.NewRequest(http.MethodPost, "/users",
                strings.NewReader(tt.body))
            req.Header.Set("Content-Type", "application/json")

            w := httptest.NewRecorder()
            handler.ServeHTTP(w, req)

            assert.Equal(t, tt.wantStatus, w.Code)

            if tt.wantName != "" {
                var resp map[string]any
                require.NoError(t, json.NewDecoder(w.Body).Decode(&resp))
                assert.Equal(t, tt.wantName, resp["name"])
            }
        })
    }
}
```

### httptest.NewServer — Full HTTP Server Test (for clients)

```go
func TestUserClient_GetUser(t *testing.T) {
    t.Parallel()

    server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        if r.URL.Path == "/users/1" {
            w.Header().Set("Content-Type", "application/json")
            json.NewEncoder(w).Encode(User{ID: "1", Name: "Alice"})
            return
        }
        w.WriteHeader(http.StatusNotFound)
    }))
    t.Cleanup(server.Close)

    client := NewUserClient(server.URL)
    user, err := client.GetUser(t.Context(), "1")
    require.NoError(t, err)
    assert.Equal(t, "Alice", user.Name)
}
```

### Testing Middleware

```go
func TestAuthMiddleware(t *testing.T) {
    t.Parallel()

    tests := []struct {
        name       string
        token      string
        wantStatus int
    }{
        {"valid token", "Bearer valid-token", http.StatusOK},
        {"missing token", "", http.StatusUnauthorized},
        {"invalid token", "Bearer bad-token", http.StatusUnauthorized},
    }

    handler := AuthMiddleware(validatorFunc)(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
    }))

    for _, tt := range tests {
        tt := tt
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()

            req := httptest.NewRequest(http.MethodGet, "/", nil)
            if tt.token != "" {
                req.Header.Set("Authorization", tt.token)
            }
            w := httptest.NewRecorder()
            handler.ServeHTTP(w, req)

            assert.Equal(t, tt.wantStatus, w.Code)
        })
    }
}
```

## Database Integration Tests

### Transaction Rollback Pattern (Real Database, No Cleanup)

Each test runs inside a transaction that is rolled back — no data persists, no test interference:

```go
//go:build integration

func TestUserRepository(t *testing.T) {
    db := connectTestDB(t) // uses TEST_DATABASE_URL env var

    t.Run("creates and retrieves user", func(t *testing.T) {
        // Begin transaction for this test
        tx, err := db.BeginTxx(t.Context(), nil)
        require.NoError(t, err)
        t.Cleanup(func() { tx.Rollback() }) // rollback regardless of outcome

        repo := NewUserRepository(tx)

        created, err := repo.Create(t.Context(), &User{Name: "Alice", Email: "alice@test.com"})
        require.NoError(t, err)
        require.NotEmpty(t, created.ID)

        found, err := repo.FindByID(t.Context(), created.ID)
        require.NoError(t, err)
        assert.Equal(t, "Alice", found.Name)
    })
}

func connectTestDB(t *testing.T) *sqlx.DB {
    t.Helper()
    url := os.Getenv("TEST_DATABASE_URL")
    if url == "" {
        t.Skip("TEST_DATABASE_URL not set")
    }
    db, err := sqlx.Open("pgx", url)
    require.NoError(t, err)
    t.Cleanup(func() { db.Close() })
    return db
}
```

## Testcontainers — Ephemeral Test Databases

Spin up a real database in Docker for integration tests:

```bash
go get github.com/testcontainers/testcontainers-go
go get github.com/testcontainers/testcontainers-go/modules/postgres
```

```go
//go:build integration

package order_test

import (
    "testing"
    "github.com/testcontainers/testcontainers-go/modules/postgres"
    "github.com/testcontainers/testcontainers-go"
)

func setupPostgres(t *testing.T) *sqlx.DB {
    t.Helper()

    ctx := t.Context()

    container, err := postgres.Run(ctx,
        "postgres:16-alpine",
        postgres.WithDatabase("testdb"),
        postgres.WithUsername("test"),
        postgres.WithPassword("test"),
        testcontainers.WithWaitStrategy(
            wait.ForLog("database system is ready to accept connections").
                WithOccurrence(2).
                WithStartupTimeout(30*time.Second),
        ),
    )
    require.NoError(t, err)
    t.Cleanup(func() { container.Terminate(ctx) })

    connStr, err := container.ConnectionString(ctx, "sslmode=disable")
    require.NoError(t, err)

    db, err := sqlx.Open("pgx", connStr)
    require.NoError(t, err)
    t.Cleanup(func() { db.Close() })

    // Run migrations
    runMigrations(t, db)

    return db
}

// Share container across tests in a package (one container per package)
var (
    testDB   *sqlx.DB
    testOnce sync.Once
)

func getTestDB(t *testing.T) *sqlx.DB {
    t.Helper()
    testOnce.Do(func() {
        testDB = setupPostgres(t)
    })
    return testDB
}
```

### Other Testcontainer Modules

```go
// Redis
import tcredis "github.com/testcontainers/testcontainers-go/modules/redis"

container, err := tcredis.Run(ctx, "redis:7-alpine")
addr, err := container.ConnectionString(ctx)

// MySQL
import tcmysql "github.com/testcontainers/testcontainers-go/modules/mysql"

container, err := tcmysql.Run(ctx, "mysql:8",
    tcmysql.WithDatabase("testdb"),
    tcmysql.WithUsername("test"),
    tcmysql.WithPassword("test"),
)
```

## Environment Variable Management

```go
func TestWithEnvVar(t *testing.T) {
    t.Setenv("MY_CONFIG", "test-value") // automatically restored after test
    // ...
}
```

## Testing CLI Commands

```go
func TestCLI_CreateUser(t *testing.T) {
    // Capture stdout
    old := os.Stdout
    r, w, _ := os.Pipe()
    os.Stdout = w

    t.Cleanup(func() {
        w.Close()
        os.Stdout = old
    })

    // Run command
    rootCmd.SetArgs([]string{"user", "create", "--name", "Alice"})
    err := rootCmd.Execute()
    require.NoError(t, err)

    w.Close()
    var buf bytes.Buffer
    io.Copy(&buf, r)

    assert.Contains(t, buf.String(), "User created")
}
```
