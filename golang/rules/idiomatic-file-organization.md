---
title: Code Organisation Within Files
impact: MEDIUM
impactDescription: Consistent layout makes navigation predictable across the entire codebase
tags: idiomatic, file-organisation, package, layout
---

## Code Organisation Within Files

**Impact: MEDIUM — Consistent layout makes navigation predictable across the entire codebase**

Follow a consistent ordering within each Go file. One primary type per file (when it has significant methods). Unexport aggressively — exported names are a commitment.

## Standard File Layout

```go
// 1. Package documentation comment (for the file's primary type or the package)
// Package user provides user management operations.
package user

// 2. Imports — grouped and sorted by goimports
import (
    // stdlib
    "context"
    "fmt"

    // external
    "github.com/lib/pq"

    // internal
    "github.com/example/app/internal/db"
)

// 3. Constants
const (
    defaultTimeout = 30 * time.Second
    MaxRetries     = 3
)

// 4. Package-level variables (minimise these)
var ErrNotFound = errors.New("user not found")

// 5. Type definitions
type User struct {
    ID    int
    Name  string
    Email string
}

// 6. Constructors / factory functions
func New(name, email string) *User {
    return &User{Name: name, Email: email}
}

// 7. Methods — exported first, then unexported
func (u *User) IsActive() bool { return u.active }

func (u *User) validate() error { ... }

// 8. Package-level helper functions (unexported)
func parseEmail(s string) (string, error) { ... }
```

## One Primary Type Per File

When a type has significant methods, give it its own file named after the type:

```
user/
  user.go          ← User type, constructor, methods
  user_repo.go     ← UserRepository interface + implementation
  user_service.go  ← UserService (business logic)
  user_test.go     ← tests for all of the above
```

Small helper types (options structs, errors) can live in the same file as their primary type.

## Unexport Aggressively

- Start unexported; export only when a consumer outside the package needs it
- Unexporting a name is a breaking change; exporting is always backward-compatible
- An unexported API can be changed freely without versioning concerns

```go
// Bad — exporting everything
type UserCache struct{ ... }
func (c *UserCache) Evict(key string) { ... }
func (c *UserCache) internalReset() { ... } // should never have been exported

// Good — export the minimum
type userCache struct{ ... }         // unexported — internal detail
func (c *userCache) evict(key string) { ... }
```

## Avoid util / common / helpers Packages

These become dumping grounds with no clear ownership:

```
// Bad
internal/util/strings.go      ← what lives here? who maintains it?
internal/helpers/time.go

// Good — put helpers close to where they're used
internal/user/format.go       ← string helpers for the user package
internal/order/time.go        ← time helpers for the order package
```

## Why

- **Navigation**: Consistent layout means every Go file can be scanned top-to-bottom in the same order
- **Discoverability**: One type per file matches the filename — `user.go` has `User`
- **Minimal surface**: Unexported names are free to refactor; exported names lock in contracts
- **Package cohesion**: Avoiding `util` packages keeps related code together

Reference: [Effective Go — Package names](https://go.dev/doc/effective_go#package-names) | [Go Project Layout](https://github.com/golang-standards/project-layout) | [Code Style reference](../references/code-style.md) | [Project Layout reference](../references/project-layout.md)
See also: `golang/references/code-style.md` | `golang/references/project-layout.md`
