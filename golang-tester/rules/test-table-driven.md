---
title: Table-Driven Tests
impact: CRITICAL
impactDescription: Eliminates duplicate test boilerplate; adding a case is one struct literal; subtests are filterable by name
tags: testing, table-driven, t.Run, subtests
---

## Table-Driven Tests

**Impact: CRITICAL — Eliminates duplicate test boilerplate; adding a case is one struct literal; subtests are filterable by name**

Define all inputs and expected outputs in a slice of structs, iterate with `t.Run`. This is the canonical Go testing pattern endorsed by the standard library.

## Bad Example

```go
func TestDivide(t *testing.T) {
    result, err := Divide(10, 2)
    if err != nil {
        t.Fatal(err)
    }
    if result != 5 {
        t.Errorf("got %f; want 5", result)
    }

    result, err = Divide(10, 0)
    if err == nil {
        t.Error("expected error for division by zero")
    }
    // Adding a new case means copy-pasting the entire structure
}
```

## Good Example

```go
func TestDivide(t *testing.T) {
    t.Parallel()

    tests := []struct {
        name    string
        a, b    float64
        want    float64
        wantErr bool
    }{
        {name: "basic division", a: 10, b: 2, want: 5},
        {name: "divide by zero", a: 10, b: 0, wantErr: true},
        {name: "negative result", a: -6, b: 3, want: -2},
        {name: "fractional result", a: 7, b: 2, want: 3.5},
    }

    for _, tt := range tests {
        tt := tt // capture (required before Go 1.22)
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()

            got, err := Divide(tt.a, tt.b)
            if (err != nil) != tt.wantErr {
                t.Fatalf("Divide() error = %v; wantErr %v", err, tt.wantErr)
            }
            if !tt.wantErr && got != tt.want {
                t.Errorf("Divide() = %v; want %v", got, tt.want)
            }
        })
    }
}
```

## Why

- **Conciseness** — adding a case = adding one struct literal
- **Filterability** — `go test -run TestDivide/divide_by_zero` runs exactly one case
- **Parallelism** — `t.Parallel()` inside subtests runs cases concurrently
- **Readability** — intent is visible in the named test cases
- **Standard** — used throughout the Go standard library

Reference: [Go Wiki — TableDrivenTests](https://github.com/golang/go/wiki/TableDrivenTests) | [Patterns reference](../references/patterns.md)
See also: `golang-tester/references/patterns.md`
