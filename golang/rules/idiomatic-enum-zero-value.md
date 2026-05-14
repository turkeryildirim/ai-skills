---
title: Enum Zero Values — Unknown/Invalid at iota 0
impact: HIGH
impactDescription: Uninitialized enum values silently map to a meaningful state, causing subtle bugs
tags: idiomatic, enum, iota, zero-value, constants
---

## Enum Zero Values — Unknown/Invalid at iota 0

**Impact: HIGH — Uninitialized enum values silently map to a meaningful state, causing subtle bugs**

Always place an explicit `Unknown`/`Invalid`/`Unset` sentinel constant at `iota` position 0. A `var s Status` silently becomes 0 — if 0 maps to a real state like `StatusReady`, code behaves as if a status was deliberately chosen when it wasn't.

## Bad Example

```go
type Status int

const (
    StatusReady    Status = iota  // 0 — uninitialized looks "ready"
    StatusActive                  // 1
    StatusInactive                // 2
)

// Problem: uninitialized variable silently passes checks
func processIfReady(s Status) {
    if s == StatusReady {
        process() // runs for any uninitialized Status — silent bug
    }
}

var s Status               // s == 0 == StatusReady
processIfReady(s)          // process() runs — but s was never set!

// Problem: switch with no default misses truly uninitialized values
switch s {
case StatusReady:
    // executes silently even though s was never assigned
case StatusActive:
    // ...
}
```

## Good Example

```go
type Status int

const (
    StatusUnknown  Status = iota  // 0 — explicit "not set"
    StatusReady                   // 1
    StatusActive                  // 2
    StatusInactive                // 3
)

// Uninitialized value is now clearly invalid
func processIfReady(s Status) {
    if s == StatusUnknown {
        panic("processIfReady called with uninitialized status")
        // or: return an error
    }
    if s == StatusReady {
        process()
    }
}

var s Status               // s == 0 == StatusUnknown — obviously not ready
```

## Naming the Zero Value

Use whichever name best communicates "not set":

| Context | Good zero-value name |
|---|---|
| State machine | `StatusUnknown`, `StateUnset` |
| Direction | `DirectionNone` |
| Priority | `PriorityUnspecified` |
| Protocol buffer style | `TypeUNKNOWN` (for proto compat) |
| Validation error level | `SeverityNone` |

Avoid `StatusInvalid` when the zero value is a valid "no choice made" state — `Unknown` or `Unset` is clearer.

## Detecting Unhandled Zero Values

Add a `default` to every switch on a custom type to catch uninitialized or new values:

```go
switch status {
case StatusReady:
    startWork()
case StatusActive:
    continueWork()
case StatusInactive:
    pause()
case StatusUnknown:
    return fmt.Errorf("status not initialized")
default:
    panic(fmt.Sprintf("unhandled status: %d", status))
}
```

The `exhaustive` linter enforces that all enum values are covered in switch statements.

## Why

- **Correctness**: Zero value of a Go variable is always 0; without a sentinel, 0 silently maps to a real state
- **Debuggability**: `StatusUnknown` in a log immediately flags a programming error; `StatusReady` hides it
- **Protocol Buffers**: Proto3 requires the zero value to be the "unknown" variant by convention
- **`exhaustive` linter**: Catches switch statements that don't handle all declared enum values

Reference: [Effective Go — Constants](https://go.dev/doc/effective_go#constants) | [exhaustive linter](https://github.com/nishanths/exhaustive) | [Naming reference](../references/naming.md) | [Safety reference](../references/safety.md)
See also: `golang/references/naming.md` | `golang/references/safety.md`
