# Go Test Patterns

Canonical patterns for structuring Go tests: table-driven tests, subtests, parallel execution, helpers, fixtures, and golden files.

## File Conventions

```go
// White-box test — same package, can access unexported identifiers
package mypackage

// Black-box test — separate _test package, tests public API only (preferred)
package mypackage_test
```

Use black-box tests (`_test` suffix) by default. Switch to white-box only when testing unexported behavior that matters.

## Naming Conventions

```go
func TestAdd(t *testing.T) { ... }                  // function test
func TestMyStruct_MyMethod(t *testing.T) { ... }    // method test
func TestMyStruct_MyMethod_EdgeCase(t *testing.T) { ... } // variant
func BenchmarkAdd(b *testing.B) { ... }             // benchmark
func FuzzAdd(f *testing.F) { ... }                  // fuzz test
func ExampleAdd() { ... }                           // runnable example
```

Test case names within `t.Run` should describe the scenario:
- `"returns error when quantity is zero"`
- `"applies bulk discount for orders over 100"`
- `"propagates context cancellation"`

## Table-Driven Tests

The canonical Go testing pattern. Define all cases as a slice of structs, iterate with `t.Run`.

```go
func TestCalculatePrice(t *testing.T) {
    t.Parallel()

    tests := []struct {
        name      string
        quantity  int
        unitPrice float64
        want      float64
        wantErr   bool
    }{
        {
            name:      "single item at full price",
            quantity:  1,
            unitPrice: 10.0,
            want:      10.0,
        },
        {
            name:      "bulk discount applies over 100 items",
            quantity:  100,
            unitPrice: 10.0,
            want:      900.0,
        },
        {
            name:      "zero quantity returns zero",
            quantity:  0,
            unitPrice: 10.0,
            want:      0.0,
        },
        {
            name:      "negative quantity returns error",
            quantity:  -1,
            unitPrice: 10.0,
            wantErr:   true,
        },
    }

    for _, tt := range tests {
        tt := tt // capture range variable (required before Go 1.22)
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()

            got, err := CalculatePrice(tt.quantity, tt.unitPrice)

            if tt.wantErr {
                require.Error(t, err)
                return
            }
            require.NoError(t, err)
            assert.Equal(t, tt.want, got)
        })
    }
}
```

**Filtering a single case:**
```bash
go test -run TestCalculatePrice/bulk_discount ./...
```

## Subtests and t.Run

```go
func TestUserService(t *testing.T) {
    t.Parallel()

    // Shared setup for all subtests
    svc := NewUserService(newFakeStore(), slog.Default())

    t.Run("creates user with valid input", func(t *testing.T) {
        t.Parallel()
        user, err := svc.Create(t.Context(), CreateUserInput{
            Name:  "Alice",
            Email: "alice@example.com",
        })
        require.NoError(t, err)
        assert.NotEmpty(t, user.ID)
        assert.Equal(t, "Alice", user.Name)
    })

    t.Run("returns error for duplicate email", func(t *testing.T) {
        t.Parallel()
        // ...
    })

    t.Run("returns error for empty name", func(t *testing.T) {
        t.Parallel()
        _, err := svc.Create(t.Context(), CreateUserInput{Email: "x@example.com"})
        require.Error(t, err)
        assert.ErrorIs(t, err, ErrInvalidInput)
    })
}
```

## Test Helpers with t.Helper()

Always call `t.Helper()` as the first line of test helper functions. This causes failures to be reported at the call site, not inside the helper.

```go
// Bad — failure points to line inside makeUser, not the test
func makeUser(t *testing.T, name string) *User { ... }

// Good — failure points to the test that called makeUser
func makeUser(t *testing.T, name string) *User {
    t.Helper()
    user, err := NewUser(name, "test@example.com")
    require.NoError(t, err)
    return user
}
```

Helpers for setup/teardown:

```go
func setupDB(t *testing.T) *sql.DB {
    t.Helper()
    db, err := sql.Open("pgx", os.Getenv("TEST_DATABASE_URL"))
    require.NoError(t, err)
    t.Cleanup(func() { db.Close() }) // automatic teardown
    return db
}

func TestUserRepository(t *testing.T) {
    db := setupDB(t) // cleaned up automatically when test ends
    // ...
}
```

## t.Cleanup — Resource Teardown

Use `t.Cleanup` instead of `defer` for test resource cleanup. Cleanup runs after the test and all its subtests finish.

```go
func TestWithTempFile(t *testing.T) {
    // t.TempDir() creates a temp directory and registers cleanup automatically
    dir := t.TempDir()

    // t.Cleanup for manual cleanup
    server := startTestServer()
    t.Cleanup(func() {
        server.Close()
    })
}
```

## t.Context() — Test Context (Go 1.24+)

```go
// t.Context() returns a context that is cancelled when the test ends
// Use instead of context.Background() in tests
func TestWithContext(t *testing.T) {
    ctx := t.Context() // cancelled when test ends (including t.Cleanup)

    result, err := svc.Process(ctx, input)
    require.NoError(t, err)
    // ...
}
```

For Go < 1.24, use a helper:

```go
func testContext(t *testing.T) context.Context {
    t.Helper()
    ctx, cancel := context.WithCancel(context.Background())
    t.Cleanup(cancel)
    return ctx
}
```

## Fixtures and testdata/

```
internal/user/
  user.go
  user_test.go              ← unit tests (white-box or black-box)
  user_integration_test.go  ← //go:build integration
  testdata/
    valid_user.json
    invalid_user_missing_email.json
    golden/
      create_response.json
```

Loading fixtures:

```go
func loadFixture(t *testing.T, name string) []byte {
    t.Helper()
    data, err := os.ReadFile(filepath.Join("testdata", name))
    require.NoError(t, err, "loading fixture %s", name)
    return data
}
```

## Golden Files

Golden files store expected output for complex values (JSON, HTML, CLI output). Update them intentionally with a flag.

```go
var update = flag.Bool("update", false, "update golden files")

func TestRenderInvoice(t *testing.T) {
    invoice := buildTestInvoice()
    got := RenderInvoice(invoice)

    golden := filepath.Join("testdata", "golden", "invoice.html")

    if *update {
        require.NoError(t, os.WriteFile(golden, []byte(got), 0644))
        return
    }

    want, err := os.ReadFile(golden)
    require.NoError(t, err, "golden file missing — run with -update to create")
    assert.Equal(t, string(want), got)
}
```

```bash
go test -run TestRenderInvoice -update ./...  # regenerate golden files
go test -run TestRenderInvoice ./...          # verify against golden files
```

## require.Eventually — Async Assertions

Never use `time.Sleep` to wait for async operations. Use `require.Eventually`:

```go
// Bad — fragile, adds latency
time.Sleep(100 * time.Millisecond)
assert.True(t, worker.IsRunning())

// Good — polls until condition is true or timeout
require.Eventually(t,
    func() bool { return worker.IsRunning() },
    5*time.Second,   // timeout
    10*time.Millisecond, // poll interval
    "worker did not start within 5 seconds",
)
```

## Test File Layout

```
pkg/
  order/
    order.go
    order_test.go              ← unit tests
    order_integration_test.go  ← //go:build integration
    testdata/
      fixtures/
        valid_order.json
      golden/
        invoice_output.txt
  user/
    user.go
    user_test.go
```
