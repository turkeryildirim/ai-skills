---
title: Boolean Fields and Methods — is/has/can Prefix
impact: MEDIUM
impactDescription: Bare adjective fields are ambiguous; is/has/can reads as a question
tags: idiomatic, naming, boolean, fields, methods
---

## Boolean Fields and Methods — is/has/can Prefix

**Impact: MEDIUM — Bare adjective fields are ambiguous; is/has/can reads as a question**

Unexported boolean struct fields MUST use `is`, `has`, or `can` prefix. Exported getter methods keep the prefix. This distinguishes boolean fields from other types at a glance and reads naturally as a true/false question.

## Bad Example

```go
type Server struct {
    running     bool  // is it running or a runner? ambiguous
    tls         bool  // flag or TLS config struct?
    permission  bool  // bool or Permission type?
    connected   bool  // ambiguous — could be a noun
}

// Exported getter with no prefix — looks like it returns a value, not a bool
func (s *Server) Running() bool { return s.running }
func (s *Server) TLS() bool { return s.tls }

// Usage — it's not obvious these return booleans
if server.Running() { ... }  // "Running" could return a runner object
if server.TLS() { ... }      // "TLS" could return TLS config
```

## Good Example

```go
type Server struct {
    isRunning    bool  // obviously a boolean flag
    hasTLS       bool  // obviously a boolean flag
    canAccept    bool  // obviously a boolean flag
}

// Exported getters keep the prefix — reads as a yes/no question
func (s *Server) IsRunning() bool { return s.isRunning }
func (s *Server) HasTLS() bool    { return s.hasTLS }
func (s *Server) CanAccept() bool { return s.canAccept }

// Usage — immediately readable
if server.IsRunning() { ... }  // clearly a boolean check
if server.HasTLS() { ... }     // clearly a boolean check
```

## Prefix Selection Guide

| Prefix | Use for | Examples |
|---|---|---|
| `is` | State or condition | `isActive`, `isVerified`, `isClosed`, `isEmpty` |
| `has` | Possession or presence | `hasPermission`, `hasTLS`, `hasChildren`, `hasErrors` |
| `can` | Capability | `canWrite`, `canRetry`, `canAccept` |

## Exception: Interface Methods

Standard library interfaces use bare names for boolean-like methods (`io.Reader.Read` returns `n, err`, not a bool). For your own domain predicates, keep the prefix:

```go
// Implementing a standard interface — no prefix (follow the interface contract)
func (v Validator) Validate() error { ... }

// Domain predicate — use prefix
func (u User) IsActive() bool { ... }
func (u User) HasSubscription() bool { ... }
```

## Exported Fields

If you must export a boolean field directly (usually avoid this — prefer a getter), follow the same convention:

```go
type Config struct {
    IsDebug    bool
    HasMetrics bool
}
```

## Why

- **Readability**: `if server.IsRunning()` reads like a sentence; `if server.Running()` is ambiguous
- **Type signals**: `isRunning bool` immediately tells the reader it's a flag, not a struct or function
- **Convention**: Used throughout the standard library (`net.Conn`, `os.FileInfo`) for bool-returning methods
- **Distinction**: Separates state predicates from value-returning methods

Reference: [Effective Go — Names](https://go.dev/doc/effective_go#names) | [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments#mixed-caps) | [Naming reference](../references/naming.md)
See also: `golang/references/naming.md`
