---
title: Constructor Naming — New() vs NewTypeName()
impact: MEDIUM
impactDescription: Inconsistent constructor names break caller expectations and create stutter
tags: idiomatic, naming, constructor, New
---

## Constructor Naming — New() vs NewTypeName()

**Impact: MEDIUM — Inconsistent constructor names break caller expectations and create stutter**

When a package exports a **single primary type**, the constructor is `New()`. When a package exports **multiple constructible types**, use `NewTypeName()` to distinguish them. Never use `NewTypeName()` for a single type — it creates stutter at the call site.

## Bad Example

```go
// In package ring — single primary type, but uses NewRing()
package ring

type Ring struct { ... }

func NewRing(n int) *Ring { ... }
// Caller writes: ring.NewRing(10) — "Ring" appears twice

// In package apiclient — single primary type
package apiclient

type Client struct { ... }

func NewClient(url string) *Client { ... }
// Caller writes: apiclient.NewClient(...) — "client" appears in both package and function
```

## Good Example

```go
// In package ring — single primary type, use New()
package ring

type Ring struct { ... }

func New(n int) *Ring { ... }
// Caller writes: ring.New(10) — clean, no stutter

// In package apiclient — single primary type
package apiclient

type Client struct { ... }

func New(url string) *Client { ... }
// Caller writes: apiclient.New(...) — no stutter

// In package http — multiple constructible types, NewTypeName() is correct
package http

func NewRequest(method, url string, body io.Reader) (*Request, error) { ... }
func NewServeMux() *ServeMux { ... }
func NewResponseRecorder() *ResponseRecorder { ... }
// Each name is necessary because the package has multiple types
```

## Decision Rule

| Package exports | Constructor pattern | Example |
|---|---|---|
| Single primary type | `New()` | `ring.New(n)`, `apiclient.New(url)` |
| Multiple constructible types | `NewTypeName()` | `http.NewRequest(...)`, `http.NewServeMux()` |

## Secondary Constructors

When a type has multiple construction strategies, name them descriptively:

```go
package user

type User struct { ... }

func New(name, email string) *User { ... }              // primary constructor
func FromJSON(data []byte) (*User, error) { ... }       // from serialized form
func Anonymous() *User { ... }                          // zero-config variant
```

## Must-Panic Variants

Constructors that panic instead of returning errors use `Must` prefix:

```go
func New(pattern string) (*Regexp, error) { ... }
func MustNew(pattern string) *Regexp {
    re, err := New(pattern)
    if err != nil {
        panic(err)
    }
    return re
}
```

## Why

- **No stutter**: `ring.New(10)` reads naturally; `ring.NewRing(10)` repeats "ring"
- **Consistency**: Go standard library (`ring.New`, `list.New`, `bytes.NewBuffer`) follows this convention
- **Discoverability**: `New()` is the obvious entry point for a single-type package
- **`revive` linter**: Flags constructor stutter with the `exported` rule

Reference: [Effective Go — Package Names](https://go.dev/doc/effective_go#package-names) | [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments) | [Naming reference](../references/naming.md)
See also: `golang/references/naming.md`
