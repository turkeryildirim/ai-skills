---
title: Go Project Structure Analysis
impact: HIGH
impactDescription: "Flat or inconsistent package structure makes Go codebases unmaintainable and prevents clear dependency boundaries"
tags: golang, project-structure, standard-layout, packages, layers, error-handling
---

## Go Project Structure Analysis

**Impact: HIGH (Flat or inconsistent package structure makes Go codebases unmaintainable and prevents clear dependency boundaries)**

Go projects benefit from consistent, well-known layout patterns. The absence of a deliberate structure leads to circular imports, package pollution, and difficulty enforcing internal vs. exported boundaries.

## Incorrect

```go
// ❌ Flat project — everything in root package, no separation

// main.go — 800-line monolith
package main

import (
    "database/sql"
    "encoding/json"
    "net/http"
)

var db *sql.DB  // ❌ Global state

func main() {
    db, _ = sql.Open("postgres", os.Getenv("DB_URL"))
    http.HandleFunc("/users", handleUsers)  // ❌ handler does everything
    http.ListenAndServe(":8080", nil)
}

func handleUsers(w http.ResponseWriter, r *http.Request) {
    // ❌ DB query directly in handler
    rows, _ := db.Query("SELECT id, name FROM users")
    // ❌ Business logic in handler
    // ❌ No error handling
    json.NewEncoder(w).Encode(users)
}
```

## Correct

```
// ✅ Standard Layout for a web service

myapp/
├── cmd/
│   └── api/
│       └── main.go          → entry point only: wires dependencies, starts server
├── internal/
│   ├── handler/             → HTTP in/out — no business logic
│   │   └── user_handler.go
│   ├── service/             → Business logic — no HTTP types
│   │   └── user_service.go
│   ├── repository/          → Data access only
│   │   └── user_repository.go
│   ├── domain/              → Entities and interfaces
│   │   └── user.go
│   └── config/              → Structured config, validated at startup
│       └── config.go
├── pkg/                     → Reusable packages safe for external import
│   └── pagination/
├── go.mod
└── go.sum
```

```go
// ✅ Handler delegates to service
func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
    id := chi.URLParam(r, "id")
    user, err := h.svc.GetUser(r.Context(), id)  // ✅ context propagated
    if err != nil {
        if errors.Is(err, domain.ErrNotFound) {   // ✅ errors.Is
            http.Error(w, "not found", http.StatusNotFound)
            return
        }
        http.Error(w, "internal error", http.StatusInternalServerError)
        return
    }
    json.NewEncoder(w).Encode(user)
}
```

## Structure Compliance Assessment

```
CRITICAL violations:
├── All logic in main.go (>200 lines)
├── No cmd/ separation when multiple binaries exist
└── circular package imports

HIGH violations:
├── Database queries directly in HTTP handlers
├── No internal/ boundary — all packages exported
└── panic used for input validation errors

MEDIUM violations:
├── pkg/ used for internal-only code (use internal/ instead)
├── No domain/ package — entities defined in handler or repository
└── Inconsistent error wrapping (some use %w, some do not)

LOW violations:
├── Missing Makefile or Taskfile for build/test/lint tasks
└── No build tags to separate integration tests
```

## Directory Signals

```
✅ Healthy Go project (web service):
cmd/api/main.go         → thin: NewServer(), ListenAndServe()
internal/handler/       → only http.Request/ResponseWriter, calls service
internal/service/       → pure business logic, no HTTP
internal/repository/    → only SQL/ORM calls, returns domain types
internal/domain/        → interfaces + entity types
internal/config/        → env-based config struct

❌ Warning signals:
main.go > 200 lines         → mixing concerns
no internal/ directory      → no encapsulation
handlers/ with SQL queries  → missing service layer
utils/ or helpers/ package  → grab-bag anti-pattern
```

## Why

- **Circular imports**: Go forbids circular package dependencies; poor layout forces workarounds
- **`internal/` enforcement**: Go compiler prevents external packages from importing `internal/` — this is the primary encapsulation tool
- **Testability**: A `service` package with no HTTP types can be unit tested without starting an HTTP server
