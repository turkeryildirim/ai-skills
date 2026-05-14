---
title: Use Functional Options for Constructor APIs
impact: HIGH
impactDescription: Functional options scale better than config structs and add no breaking changes
tags: style, constructor, functional-options, API design
---

## Use Functional Options for Constructor APIs

**Impact: HIGH — Functional options scale better than config structs and add no breaking changes**

When a constructor takes more than 2-3 optional parameters, use the functional options pattern. Each option is a function that mutates the target struct. New options can be added without changing the constructor signature — fully backward-compatible.

## Bad Example

```go
// Config struct — adding a field breaks no callers, but is verbose to use
type ServerConfig struct {
    Addr         string
    ReadTimeout  time.Duration
    WriteTimeout time.Duration
    MaxConns     int
    TLSEnabled   bool
    TLSCertPath  string
}

func NewServer(cfg ServerConfig) *Server {
    return &Server{cfg: cfg}
}

// Caller must construct a config even for one option
srv := NewServer(ServerConfig{
    Addr:        ":8080",
    ReadTimeout: 30 * time.Second,
})

// Positional params — caller must remember order, breaks on change
func NewServer(addr string, readTimeout, writeTimeout time.Duration, maxConns int) *Server
```

## Good Example

```go
type Server struct {
    addr         string
    readTimeout  time.Duration
    writeTimeout time.Duration
    maxConns     int
}

type Option func(*Server)

func WithReadTimeout(d time.Duration) Option {
    return func(s *Server) { s.readTimeout = d }
}

func WithWriteTimeout(d time.Duration) Option {
    return func(s *Server) { s.writeTimeout = d }
}

func WithMaxConns(n int) Option {
    return func(s *Server) { s.maxConns = n }
}

func NewServer(addr string, opts ...Option) *Server {
    // Defaults
    s := &Server{
        addr:         addr,
        readTimeout:  5 * time.Second,
        writeTimeout: 10 * time.Second,
        maxConns:     100,
    }
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// Caller — self-documenting, only specify what differs from defaults
srv := NewServer(":8080",
    WithReadTimeout(30*time.Second),
    WithMaxConns(500),
)

// Adding a new option later never breaks existing callers
```

## Validation in Options

Options can validate and return errors when the constructor signature allows it:

```go
type Option func(*Server) error

func WithMaxConns(n int) Option {
    return func(s *Server) error {
        if n <= 0 {
            return fmt.Errorf("WithMaxConns: n must be positive, got %d", n)
        }
        s.maxConns = n
        return nil
    }
}

func NewServer(addr string, opts ...Option) (*Server, error) {
    s := &Server{addr: addr, maxConns: 100}
    for _, opt := range opts {
        if err := opt(s); err != nil {
            return nil, fmt.Errorf("NewServer: %w", err)
        }
    }
    return s, nil
}
```

## When to Use a Config Struct Instead

Use a config struct when:
- All fields are required (no defaults)
- The config is loaded from YAML/JSON/env and passed around
- The type is a data transfer object, not a constructor API

## Why

- **Backward-compatible**: adding a new `WithFoo()` option never changes existing callers
- **Self-documenting**: `WithReadTimeout(30*time.Second)` is clear; positional `30*time.Second` is not
- **Composable**: options can be combined, stored, reused, and passed around as slices
- **Default values**: the constructor applies defaults; callers only override what they need
- **Go idiom**: used throughout the Go standard library and popular libraries (grpc, zap, etc.)

Reference: [Functional Options — Dave Cheney](https://dave.cheney.net/2014/10/17/functional-options-for-friendly-apis) | [Effective Go](https://go.dev/doc/effective_go)
