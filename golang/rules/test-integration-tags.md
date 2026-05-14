---
title: Separate Integration Tests with Build Tags
impact: HIGH
impactDescription: Mixing integration and unit tests slows the fast feedback loop and requires external dependencies
tags: testing, integration, build-tags, go:build
---

## Separate Integration Tests with Build Tags

**Impact: HIGH — Mixing integration and unit tests slows the fast feedback loop and requires external dependencies**

Integration tests that connect to real databases, message queues, or external services must be separated from unit tests using `//go:build integration`. This keeps `go test ./...` fast and self-contained, while `go test -tags=integration ./...` runs the full suite in CI.

## Bad Example

```go
// Mixed with unit tests — everyone who runs go test ./... needs a live database
package user

func TestGetUser(t *testing.T) {
    // Unit test — fast, no deps
    u := &User{Name: "alice"}
    assert.Equal(t, "alice", u.Name)
}

func TestGetUserFromDB(t *testing.T) {
    // Integration test — silently fails if DATABASE_URL isn't set
    db, _ := sql.Open("postgres", os.Getenv("DATABASE_URL"))
    // ...
}
```

## Good Example

```go
// user_test.go — unit test, always runs
package user

func TestGetUser(t *testing.T) {
    u := &User{Name: "alice"}
    assert.Equal(t, "alice", u.Name)
}
```

```go
//go:build integration

// user_integration_test.go — only runs with -tags=integration
package user

import (
    "database/sql"
    "os"
    "testing"
)

func TestGetUserFromDB(t *testing.T) {
    dsn := os.Getenv("DATABASE_URL")
    if dsn == "" {
        t.Skip("DATABASE_URL not set")
    }

    db, err := sql.Open("postgres", dsn)
    if err != nil {
        t.Fatal(err)
    }
    defer db.Close()

    // ... real database test
}
```

## Running Tests

```bash
# Unit tests only — fast, no external deps
go test ./...

# Integration tests — requires live services
go test -tags=integration ./...

# Both together
go test -tags=integration -race ./...
```

## CI Configuration

```yaml
# GitHub Actions example
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - run: go test -race ./...

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
    steps:
      - run: go test -tags=integration -race ./...
        env:
          DATABASE_URL: postgres://postgres:test@localhost/testdb
```

## File Naming Convention

```
internal/user/
  user.go
  user_test.go              ← no build tag — always runs
  user_integration_test.go  ← //go:build integration
```

## Why

- **Developer experience**: `go test ./...` must be fast and work offline
- **CI separation**: Unit tests give fast PR feedback; integration tests run in the full pipeline
- **Reliability**: Unit tests never fail due to missing environment variables or services
- **Documentation**: The build tag makes the dependency explicit and discoverable

Reference: [Go build constraints](https://pkg.go.dev/cmd/go#hdr-Build_constraints) | [testing package](https://pkg.go.dev/testing)
