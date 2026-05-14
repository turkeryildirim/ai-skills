---
title: The nil Interface Trap — Typed nil Is Not nil
impact: CRITICAL
impactDescription: Returning a typed nil pointer wrapped in an interface causes unexpected panics at the call site
tags: safety, nil, interface, pointer, correctness
---

## The nil Interface Trap — Typed nil Is Not nil

**Impact: CRITICAL — Returning a typed nil pointer wrapped in an interface causes unexpected panics at the call site**

An interface in Go stores two things: a type descriptor and a value pointer. An interface is `== nil` only when BOTH are nil. When you return a typed nil pointer via an interface, the type descriptor is set — the interface is non-nil even though the underlying value is nil.

This is one of the most common sources of "unexpected nil pointer dereference" panics in Go.

## Bad Example

```go
type MyError struct {
    Code    int
    Message string
}

func (e *MyError) Error() string {
    return e.Message
}

// This function LOOKS like it returns nil on success, but it doesn't
func validate(input string) error {
    var err *MyError  // typed nil pointer

    if input == "" {
        err = &MyError{Code: 400, Message: "input required"}
    }

    return err  // returns interface{type: *MyError, value: nil}
                // NOT the same as nil!
}

// Caller
err := validate("valid input")
if err != nil {  // ← this is TRUE even for valid input!
    log.Printf("validation failed: %v", err)  // "validation failed: <nil>"
}
```

The same trap with interfaces:

```go
func getHandler(enabled bool) http.Handler {
    var h *MyHandler  // nil pointer

    if enabled {
        h = &MyHandler{}
    }

    return h  // if enabled==false: interface{type: *MyHandler, value: nil}
              // caller's nil check passes, then ServeHTTP panics
}
```

## Good Example

```go
// Return nil explicitly — not a typed nil variable
func validate(input string) error {
    if input == "" {
        return &MyError{Code: 400, Message: "input required"}
    }
    return nil  // interface{type: nil, value: nil} — truly nil
}

// With interface return types — always return nil directly
func getHandler(enabled bool) http.Handler {
    if !enabled {
        return nil  // NOT: var h *MyHandler; return h
    }
    return &MyHandler{}
}
```

## How to Detect This Pattern

```go
// Red flag: a variable of concrete pointer type returned as an interface
func something() error {
    var e *ConcreteError   // ← danger: this will be a non-nil error interface
    // ...
    return e               // ← WRONG
}

// Safe: the zero value of the return variable should be the interface itself
func something() error {
    var e error  // ← this is the nil interface — zero value is truly nil
    // ...
    return e
}
```

## The Rule

**Never assign a concrete pointer variable to a nil interface and return it as an interface.**

When you need a variable to accumulate an error conditionally, declare it as the interface type, not the concrete type:

```go
// Bad
var err *MyError
if condition {
    err = &MyError{...}
}
return err  // non-nil interface when condition is false

// Good
var err error  // interface type — zero value is truly nil
if condition {
    err = &MyError{...}
}
return err  // nil interface when condition is false
```

## Why

- **Interface semantics**: `interface{}` is `(type, value)` — both must be nil for the interface to be nil
- **Common pattern**: returning typed nil from error-returning functions is extremely common in Go codebases
- **Silent bug**: the compiler does not warn about this; it compiles and runs, but with unexpected behavior
- **Detection**: `staticcheck` and `nilnil` linter can catch some cases; careful code review catches the rest

Reference: [Go FAQ — Why is my nil error value not equal to nil?](https://go.dev/doc/faq#nil_error) | [staticcheck](https://staticcheck.io)
