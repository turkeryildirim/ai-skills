---
title: Table-Driven Tests
impact: HIGH
impactDescription: Eliminates duplicate test boilerplate; new cases are one line
tags: testing, table-driven, t.Run
---

## Table-Driven Tests

**Impact: HIGH — Eliminates duplicate test boilerplate; new cases are one line**

Define all inputs and expected outputs in a slice of structs, then loop over them with `t.Run`. This is the canonical Go testing pattern endorsed by the standard library itself.

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

    // Adding a new case means copy-pasting all of the above
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
        {name: "fractional", a: 7, b: 2, want: 3.5},
    }

    for _, tt := range tests {
        tt := tt // capture range variable (required before Go 1.22)
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

- **Conciseness**: Adding a case = adding one struct literal
- **Filtering**: `go test -run TestDivide/divide_by_zero` runs a single case
- **Parallelism**: `t.Parallel()` inside subtests runs cases concurrently
- **Readability**: Intent is visible in the named test cases
- **Standard**: Used throughout the Go standard library

Reference: [Table Driven Tests](https://github.com/golang/go/wiki/TableDrivenTests) | [testing package](https://pkg.go.dev/testing)
