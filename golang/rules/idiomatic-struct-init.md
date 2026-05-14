---
title: Always Use Named Fields in Composite Literals
impact: CRITICAL
impactDescription: Positional fields break silently when a struct is extended or reordered
tags: idiomatic, struct, composite-literal, named-fields
---

## Always Use Named Fields in Composite Literals

**Impact: CRITICAL — Positional fields break silently when a struct is extended or reordered**

Always specify field names when creating struct literals. Positional initialisation compiles as long as the argument count matches, but silently assigns values to the wrong fields if the struct is reordered or extended.

## Bad Example

```go
// Positional — breaks silently if http.Server fields are reordered
srv := &http.Server{":8080", mux, nil, nil, 5 * time.Second, 10 * time.Second, 0, nil, nil}

// What happens when a new field is added between Addr and Handler?
// The compiler shifts all values one position — silent bug.

// Single-field struct — still requires a name for clarity
point := Point{10, 20} // what's x, what's y?
```

## Good Example

```go
// Named fields — safe against struct evolution
srv := &http.Server{
    Addr:         ":8080",
    Handler:      mux,
    ReadTimeout:  5 * time.Second,
    WriteTimeout: 10 * time.Second,
}

// Zero values for unset fields are applied automatically — no need to list them
point := Point{X: 10, Y: 20}
```

## Exception: Well-Known Single-Field or Tuple Structs

The only acceptable exception is very small structs in the **same package** where the field order is obvious and stable (e.g., a `Point{x, y}` defined one line above). Even then, named fields are preferred.

## Test Structs in Table-Driven Tests

Always use named fields in test case structs — it's more readable and resilient to test case changes:

```go
tests := []struct {
    name    string
    input   int
    want    int
    wantErr bool
}{
    {name: "positive", input: 1, want: 2},
    {name: "zero", input: 0, want: 0},
}
```

## Why

- **Safety**: Adding a field to a struct does not silently misassign values in callers
- **Readability**: `Addr: ":8080"` is self-documenting; `":8080"` is not
- **Tooling**: `go vet` flags composite literals with missing keys in structs from other packages
- **Refactoring**: Field renames cause compile errors in named literals — caught immediately

Reference: [go vet — composites](https://pkg.go.dev/cmd/vet) | [Effective Go — Composite Literals](https://go.dev/doc/effective_go#composite_literals) | [Code Style reference](../references/code-style.md)
See also: `golang/references/code-style.md`
