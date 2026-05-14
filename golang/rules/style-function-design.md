---
title: Function Design — Short, Focused, ≤4 Parameters
impact: HIGH
impactDescription: Long functions with many parameters are hard to test, read, and call correctly
tags: style, function, parameters, context, options-struct
---

## Function Design — Short, Focused, ≤4 Parameters

**Impact: HIGH — Long functions with many parameters are hard to test, read, and call correctly**

Functions should do one thing. Limit parameters to 4; beyond that, group related inputs into a struct. Always put `context.Context` first. Prefer `range` over index-based loops.

## Bad Example

```go
// 7 parameters — caller must remember position and type of each
func CreateUser(
    firstName string,
    lastName string,
    email string,
    age int,
    role string,
    sendWelcomeEmail bool,
    referrerID int,
) (*User, error) {
    // ...
}

// Naked return in a non-trivial function — reader must scroll to find what's returned
func fetchAndProcess(ctx context.Context, id int) (result *Result, err error) {
    result, err = fetch(ctx, id)
    if err != nil {
        return // what is result here?
    }
    result, err = process(ctx, result)
    return
}
```

## Good Example

```go
// Options struct — named, extensible, backward-compatible
type CreateUserOptions struct {
    FirstName       string
    LastName        string
    Email           string
    Age             int
    Role            string
    SendWelcomeEmail bool
    ReferrerID      int
}

func CreateUser(ctx context.Context, opts CreateUserOptions) (*User, error) {
    // ...
}

// Explicit returns — always clear
func fetchAndProcess(ctx context.Context, id int) (*Result, error) {
    raw, err := fetch(ctx, id)
    if err != nil {
        return nil, fmt.Errorf("fetch id=%d: %w", id, err)
    }

    result, err := process(ctx, raw)
    if err != nil {
        return nil, fmt.Errorf("process id=%d: %w", id, err)
    }

    return result, nil
}
```

## Parameter Ordering

1. `context.Context` — always first
2. Required inputs — in logical order
3. Optional configuration — last (or in an options struct)

```go
func FetchUser(ctx context.Context, id string) (*User, error)
func SendEmail(ctx context.Context, msg EmailMessage) error
func Search(ctx context.Context, query string, opts SearchOptions) ([]Result, error)
```

## Prefer range

```go
// Bad — index-based when index isn't needed
for i := 0; i < len(users); i++ {
    process(users[i])
}

// Good
for _, user := range users {
    process(user)
}

// Go 1.22+ — range over integer
for i := range 10 {
    fmt.Println(i)
}
```

## Naked Returns

Naked returns are acceptable **only** in very short functions (≤3 lines) where the named return variables are obvious. In any longer function, return values explicitly.

## Why

- **Callability**: 4+ positional arguments require the caller to remember order and type — error-prone
- **Options struct**: Adding a new option is backward-compatible; adding a new parameter is not
- **Testability**: Small, focused functions have fewer code paths to test
- **`context.Context` first**: Convention followed by every Go stdlib and popular library

Reference: [Effective Go — Functions](https://go.dev/doc/effective_go#functions) | [Uber Go Style Guide — Function Grouping and Ordering](https://github.com/uber-go/guide/blob/master/style.md) | [Code Style reference](../references/code-style.md) | [style-functional-options rule](style-functional-options.md)
See also: `golang/references/code-style.md`
