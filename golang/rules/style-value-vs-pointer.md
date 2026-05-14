---
title: Value vs Pointer Arguments
impact: HIGH
impactDescription: Wrong choice causes unnecessary allocations or unintended mutation
tags: style, pointer, value, receiver, memory
---

## Value vs Pointer Arguments

**Impact: HIGH — Wrong choice causes unnecessary allocations or unintended mutation**

Pass small, immutable types by value. Use pointers when you need to mutate the argument, when the struct is large, or when `nil` is a meaningful value.

## Rules of Thumb

| Scenario | Use |
|----------|-----|
| Small scalars (`int`, `bool`, `string`, `time.Time`) | Value |
| Struct you need to mutate | Pointer |
| Large struct (~128+ bytes) | Pointer |
| Nil is meaningful (optional parameter) | Pointer |
| Implementing an interface with pointer receivers | Pointer |
| Immutable data shared across goroutines | Value (or pointer to immutable) |

## Bad Example

```go
// Pointer to small type — unnecessary allocation, nil-check burden
func IsExpired(t *time.Time) bool {
    if t == nil {
        return false
    }
    return time.Now().After(*t)
}

// Value of large struct — expensive copy on every call
type HeavyReport struct {
    Data   [1024]byte
    Meta   map[string]string
    Lines  []string
}

func render(r HeavyReport) string { // copies ~1 KB+ on each call
    // ...
}

// Value receiver mutates a copy — caller sees no change
type Counter struct{ n int }

func (c Counter) Increment() { // mutation is invisible to caller
    c.n++
}
```

## Good Example

```go
// Value for small, immutable type — no allocation, no nil check
func IsExpired(t time.Time) bool {
    return time.Now().After(t)
}

// Pointer for large struct
func render(r *HeavyReport) string {
    // no copy
}

// Pointer receiver for mutation
func (c *Counter) Increment() {
    c.n++
}

// Pointer when nil is meaningful
func findUser(db *sql.DB, filter *UserFilter) (*User, error) {
    // filter == nil means "no filter, return any user"
}
```

## Receiver Consistency

If any method of a type uses a pointer receiver, **all** methods should use pointer receivers. Mixed receivers confuse the compiler's method set rules for interface satisfaction.

```go
// Bad — mixed receivers
type Service struct{ ... }
func (s Service) Name() string     { return s.name }  // value
func (s *Service) Start() error    { ... }             // pointer

// Good — consistent pointer receivers
func (s *Service) Name() string    { return s.name }
func (s *Service) Start() error    { ... }
```

## Why

- **Performance**: Passing `time.Time` by pointer costs an allocation; by value it's free
- **Correctness**: Value receivers silently discard mutations — a common source of bugs
- **Nil safety**: Pointer parameters require nil checks; value parameters do not
- **Interface satisfaction**: Pointer receivers are only in the method set of `*T`, not `T`

Reference: [Effective Go — Pointers vs Values](https://go.dev/doc/effective_go#pointers_vs_values) | [Go FAQ — Pointer vs Value receivers](https://go.dev/doc/faq#methods_on_values_or_pointers)
