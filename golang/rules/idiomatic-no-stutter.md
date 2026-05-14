---
title: Avoid Package Name Stuttering
impact: HIGH
impactDescription: Repeating the package name forces callers to read the same word twice
tags: idiomatic, naming, stuttering, package
---

## Avoid Package Name Stuttering

**Impact: HIGH — Repeating the package name forces callers to read the same word twice**

Go call sites always include the package name. A name MUST NOT repeat information already present in the package qualifier. `http.HTTPClient` forces the reader to parse "HTTP" twice; `http.Client` reads naturally.

This applies to ALL exported names in a package — types, functions, variables, and constants.

## Bad Example

```go
// In package http:
type HTTPClient struct{}     // callers write: http.HTTPClient — "HTTP" twice
type HTTPServer struct{}     // callers write: http.HTTPServer

// In package json:
type JSONDecoder struct{}    // callers write: json.JSONDecoder

// In package user:
func NewUser() *User         // callers write: user.NewUser — "User" twice
type UserRepository interface{}  // callers write: user.UserRepository
const UserMaxAge = 120       // callers write: user.UserMaxAge

// In package config:
func ParseConfig() {}        // callers write: config.ParseConfig — "Config" twice

// In package dbpool:
type DBPool struct{}         // callers write: dbpool.DBPool
type PoolStatus int          // callers write: dbpool.PoolStatus — "Pool" in both
type PoolOption func(*DBPool)// callers write: dbpool.PoolOption
```

## Good Example

```go
// In package http:
type Client struct{}         // callers write: http.Client — clean
type Server struct{}         // callers write: http.Server

// In package json:
type Decoder struct{}        // callers write: json.Decoder

// In package user:
func New() *User             // callers write: user.New
type Repository interface{}  // callers write: user.Repository
const MaxAge = 120           // callers write: user.MaxAge

// In package config:
func Parse() {}              // callers write: config.Parse

// In package dbpool:
type Pool struct{}           // callers write: dbpool.Pool
type Status int              // callers write: dbpool.Status
type Option func(*Pool)      // callers write: dbpool.Option
```

## When Multiple Types Need Constructors

Use `NewTypeName()` only when the package exports multiple constructible types — this distinguishes them at the call site:

```go
// In package http — multiple types need constructors
func NewRequest(method, url string, body io.Reader) (*Request, error)
func NewServeMux() *ServeMux
func NewResponseRecorder() *ResponseRecorder
```

When there's a single primary type, use plain `New()`:

```go
// In package ring — one primary type
func New(n int) *Ring  // caller: ring.New(10)
```

## The Anti-Stutter Rule Extends to Embedded Context

Avoid stuttering even when context makes it "feel" necessary:

```go
// In package auth:
type Token struct{}          // not: AuthToken — "auth" is the package
type Permission int          // not: AuthPermission
func Validate(t Token) bool  // not: ValidateAuthToken — "auth" + "Token" both redundant
```

## Why

- **Readability**: Callers read the package name at every use site — redundant information is noise
- **Go idiom**: The entire standard library follows this (`io.Reader` not `io.IOReader`)
- **`revive` linter**: The `exported` and `stutters` rules catch this automatically
- **Consistency**: Names that follow this convention feel idiomatic and professional

Reference: [Effective Go — Package Names](https://go.dev/doc/effective_go#package-names) | [Go Code Review Comments — Package Names](https://github.com/golang/go/wiki/CodeReviewComments#package-names) | [Naming reference](../references/naming.md)
See also: `golang/references/naming.md`
