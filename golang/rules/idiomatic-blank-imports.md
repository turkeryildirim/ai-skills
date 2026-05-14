---
title: Restrict Blank Imports to main and Test Packages
impact: MEDIUM
impactDescription: Blank imports in library code hide side effects from callers
tags: idiomatic, imports, blank-import, init, side-effects
---

## Restrict Blank Imports to main and Test Packages

**Impact: MEDIUM — Blank imports in library code hide side effects from callers**

Blank imports (`_ "pkg"`) exist solely to trigger a package's `init()` function — registering a database driver, image decoder, or codec. When used in a library package, the side effect is invisible to the library's consumers. Restrict them to `main` packages and test files.

## Bad Example

```go
// In a library package — hides the side effect from callers
package db

import (
    "database/sql"
    _ "github.com/lib/pq" // side effect: registers postgres driver
)

func NewPool(dsn string) (*sql.DB, error) {
    return sql.Open("postgres", dsn)
    // Caller of this library has no idea a driver was registered.
    // If they import a different driver, they get a conflict they can't see.
}
```

## Good Example

```go
// In the library — no blank import
package db

import "database/sql"

func NewPool(dsn string, driverName string) (*sql.DB, error) {
    return sql.Open(driverName, dsn)
}

// In main — side effects are visible at the application root
package main

import (
    "github.com/example/app/internal/db"
    _ "github.com/lib/pq" // register postgres driver
)

func main() {
    pool, err := db.NewPool(os.Getenv("DSN"), "postgres")
    // ...
}
```

## In Tests

Blank imports in `_test.go` files are acceptable — they affect only the test binary:

```go
package integration_test

import (
    _ "github.com/mattn/go-sqlite3" // only for tests
)
```

## Dot Imports Are Never Acceptable in Library Code

Dot imports (`. "pkg"`) put all exported names from `pkg` into the current file's namespace. This makes it impossible to tell where a name comes from and pollutes completion results.

```go
// Never do this in library code
import . "github.com/example/app/types"

// UserID is now in scope — but where is it defined?
var id UserID
```

Exception: some test packages import their own package with `.` for readability in BDD-style tests. Even then, use with care.

## Why

- **Transparency**: `main` is the application root — all side effects are visible there
- **Conflicts**: Two libraries both blank-importing different drivers for the same interface cause hidden conflicts
- **Predictability**: Library callers control which drivers/codecs are registered
- **`revive` linter**: Flags blank imports outside `main` and test packages

Reference: [Effective Go — Blank identifier in imports](https://go.dev/doc/effective_go#blank_identifier) | [Go Code Review Comments — Import Blank](https://github.com/golang/go/wiki/CodeReviewComments#import-blank) | [Code Style reference](../references/code-style.md)
See also: `golang/references/code-style.md`
