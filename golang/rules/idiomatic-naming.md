---
title: Naming Conventions
impact: CRITICAL
impactDescription: Non-idiomatic names break tooling, docs, and team expectations
tags: naming, idiomatic, exported, MixedCaps
---

## Naming Conventions

**Impact: CRITICAL — Non-idiomatic names break tooling, docs, and team expectations**

Go uses `MixedCaps` (not `snake_case`) for all identifiers. Exported names start with an uppercase letter; unexported names start with lowercase. Acronyms are consistently cased (`URL`, `HTTP`, `userID`).

## Bad Example

```go
// snake_case — not Go
func get_user_by_id(user_id int) (*User, error) { ... }

// Inconsistent acronym casing
type HttpClient struct{}         // should be HTTPClient
type UserId struct{ val int }    // should be UserID
func parseUrl(s string) {}       // should be parseURL

// Stuttering package names
package user
type UserUser struct{} // "user.UserUser" — redundant

// All-caps constant that's not a global
const MAX_SIZE = 100 // should be MaxSize (exported) or maxSize (unexported)
```

## Good Example

```go
// MixedCaps throughout
func getUserByID(userID int) (*User, error) { ... }

// Correct acronym casing
type HTTPClient struct{}
type UserID struct{ val int }
func parseURL(s string) {}

// Package names don't stutter
package user
type User struct{} // "user.User" — clear

// Constants follow the same MixedCaps rule
const MaxRetries = 3        // exported
const defaultTimeout = 30   // unexported
```

## Naming Guidelines

| Concept | Convention | Example |
|---------|-----------|---------|
| Exported type | UpperMixedCaps | `UserService` |
| Unexported type | lowerMixedCaps | `userCache` |
| Acronym (2+ letters) | All-upper or all-lower | `URL`, `HTTP`, `userID` |
| Interface | Often `-er` suffix | `Reader`, `Stringer`, `Closer` |
| Error variable | `Err` prefix | `ErrNotFound`, `ErrTimeout` |
| Boolean | `is-`, `has-`, `can-` | `isActive`, `hasChildren` |
| Receiver | Short, 1-2 char abbrev | `u *User`, `s *Server` |

## Why

- **Tooling**: `godoc` and `go doc` surface exported names — bad names mean bad docs
- **Readability**: Go code is read far more than it is written — names matter
- **Convention**: All Go code follows this; deviating signals unfamiliarity
- **`golint` / `staticcheck`**: Flags naming violations automatically

Reference: [Effective Go — Names](https://go.dev/doc/effective_go#names) | [Go Code Review Comments — Naming](https://github.com/golang/go/wiki/CodeReviewComments#mixed-caps) | [Naming reference](../references/naming.md)
See also: `golang/references/naming.md`
