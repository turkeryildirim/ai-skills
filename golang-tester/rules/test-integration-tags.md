---
title: Use Build Tags to Separate Integration Tests
impact: HIGH
impactDescription: Without build tags, integration tests run with go test ./... and fail in CI environments without external services
tags: testing, integration, build tags, ci
---

## Use Build Tags to Separate Integration Tests

**Impact: HIGH — Integration tests without build tags run with `go test ./...` and fail on machines without external services**

Use `//go:build integration` to mark tests that require databases, HTTP services, or any external dependency. This allows developers to run fast unit tests locally with `go test ./...` and opt into integration tests explicitly.

## Bad Example

```go
// No build tag — runs with go test ./...
// Fails for any developer without a local Postgres running
package order_test

func TestCreateOrderInDatabase(t *testing.T) {
    db, err := sql.Open("postgres", os.Getenv("DATABASE_URL"))
    if err != nil {
        t.Fatal(err)  // fails locally if DATABASE_URL not set
    }
    // ...
}
```

## Good Example

```go
//go:build integration

package order_test

import (
    "testing"
    "github.com/stretchr/testify/require"
)

func TestCreateOrderInDatabase(t *testing.T) {
    url := os.Getenv("TEST_DATABASE_URL")
    if url == "" {
        t.Skip("TEST_DATABASE_URL not set — skipping integration test")
    }

    db, err := sql.Open("pgx", url)
    require.NoError(t, err)
    t.Cleanup(func() { db.Close() })

    repo := NewOrderRepository(db)
    order, err := repo.Create(t.Context(), testOrder)
    require.NoError(t, err)
    require.NotEmpty(t, order.ID)
}
```

## Running Tests

```bash
go test ./...                       # unit tests only (no integration tag)
go test -tags=integration ./...     # includes integration tests
go test -tags=integration -race ./... # integration + race detector

# In Makefile
test:
	go test -race -count=1 ./...

test-integration:
	go test -tags=integration -race -count=1 ./...
```

## Build Tag Placement

```go
//go:build integration   ← must be on the first line before package declaration
                         ← blank line required between tag and package

package order_test
```

## Multiple Tags

```go
//go:build integration && postgres

//go:build e2e

//go:build !unit          // run this test when NOT running unit tests
```

## Why

- **Developer experience** — `go test ./...` should always be fast and work without external services
- **CI isolation** — integration tests can run in a separate CI job with proper service setup
- **Explicit opt-in** — developers know they need the full environment when using `-tags=integration`

Reference: [Go Build Tags](https://pkg.go.dev/go/build) | [Integration reference](../references/integration.md)
See also: `golang-tester/references/integration.md`
