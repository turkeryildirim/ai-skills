---
title: Use t.Helper() in Test Helper Functions
impact: HIGH
impactDescription: Without t.Helper(), failures point to the helper's line, not the test that called it — making failures hard to diagnose
tags: testing, helpers, t.Helper, t.Cleanup
---

## Use t.Helper() in Test Helper Functions

**Impact: HIGH — Without t.Helper(), failures point to the helper's line, not the test that called it**

Call `t.Helper()` as the first line of any helper function that calls `t.Fatal`, `t.Error`, `require`, or `assert`. This marks the function as a helper so that Go's testing framework attributes failures to the call site in the test, not inside the helper.

## Bad Example

```go
// Without t.Helper() — failure reports line 5 (inside makeUser), not the test line
func makeUser(t *testing.T, name string) *User {
    user, err := NewUser(name, "test@example.com")
    if err != nil {
        t.Fatalf("makeUser(%q) failed: %v", name, err) // line 5 — misleading
    }
    return user
}

func TestService(t *testing.T) {
    user := makeUser(t, "Alice") // failure appears at line 5, not here
    // ...
}
```

## Good Example

```go
// With t.Helper() — failure reports the line in the test that called makeUser
func makeUser(t *testing.T, name string) *User {
    t.Helper() // first line — marks this as a helper
    user, err := NewUser(name, "test@example.com")
    require.NoError(t, err, "makeUser(%q) failed", name) // failure points to caller
    return user
}

func TestService(t *testing.T) {
    user := makeUser(t, "Alice") // failure now correctly appears here
    // ...
}
```

## Helper with t.Cleanup

Use `t.Cleanup` instead of returning a teardown function — it's automatically called even if the test panics:

```go
func setupServer(t *testing.T) *httptest.Server {
    t.Helper()
    srv := httptest.NewServer(newTestHandler())
    t.Cleanup(srv.Close) // runs after test and all subtests finish
    return srv
}

func setupDB(t *testing.T) *sql.DB {
    t.Helper()
    db, err := sql.Open("pgx", os.Getenv("TEST_DATABASE_URL"))
    require.NoError(t, err)
    t.Cleanup(func() { db.Close() })
    return db
}
```

## Why

- **Precise failure attribution** — the line number in test output points to where the helper was called, not inside the helper
- **Cleaner test output** — no noise from helper internals
- **Standard practice** — `testing.T.Helper()` was added in Go 1.9 specifically for this use case

Reference: [Go Testing — t.Helper](https://pkg.go.dev/testing#T.Helper) | [Patterns reference](../references/patterns.md)
See also: `golang-tester/references/patterns.md`
