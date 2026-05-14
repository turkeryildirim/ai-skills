---
title: Always Initialise Slices and Maps Explicitly
impact: CRITICAL
impactDescription: Nil maps panic on write; nil slices serialise to JSON null instead of []
tags: idiomatic, slice, map, nil, json, initialisation
---

## Always Initialise Slices and Maps Explicitly

**Impact: CRITICAL — Nil maps panic on write; nil slices serialise to JSON null instead of []**

Never leave a slice or map at its nil zero value when it will be written to or returned from an API. Nil maps cause a runtime panic on the first write. Nil slices marshal to JSON `null`, which surprises API consumers expecting an empty array `[]`.

## Bad Example

```go
// Nil map — panics on first write
func groupByRole(users []User) map[string][]User {
    var m map[string][]User  // nil!
    for _, u := range users {
        m[u.Role] = append(m[u.Role], u) // PANIC: assignment to entry in nil map
    }
    return m
}

// Nil slice — marshals to JSON null
type Response struct {
    Users []User `json:"users"`
}

func emptyResponse() Response {
    return Response{} // Users is nil → JSON: {"users": null}
                      // API consumers expecting [] are surprised
}

// Speculative pre-allocation — wastes memory when actual count differs
results := make([]string, 0, 1000) // but only 5 items arrive
```

## Good Example

```go
// Initialised map — safe to write
func groupByRole(users []User) map[string][]User {
    m := make(map[string][]User, len(users)) // pre-size for efficiency
    for _, u := range users {
        m[u.Role] = append(m[u.Role], u)
    }
    return m
}

// Initialised slice — marshals to JSON []
type Response struct {
    Users []User `json:"users"`
}

func emptyResponse() Response {
    return Response{
        Users: []User{}, // JSON: {"users": []}
    }
}

// Pre-allocate when capacity is known
func toNames(users []User) []string {
    names := make([]string, 0, len(users))
    for _, u := range users {
        names = append(names, u.Name)
    }
    return names
}
```

## Decision Guide

| Situation | Form |
|-----------|------|
| Size known in advance | `make([]T, 0, n)` / `make(map[K]V, n)` |
| Size unknown, will be written | `[]T{}` / `map[K]V{}` |
| Read-only, nil is acceptable | `var s []T` (document the intent) |
| Returned in an API response | Always initialise |

## Do Not Pre-allocate Speculatively

Only pre-allocate when you have a **known or well-estimated** capacity. `make([]T, 0, 1000)` wastes memory if the common case is 5 items.

## Why

- **Correctness**: Nil map write is a runtime panic — not a compile error
- **API contracts**: JSON consumers should receive `[]` not `null` for empty collections
- **Performance**: Pre-allocation with known capacity eliminates growth reallocations (see `perf-prealloc`)
- **Explicitness**: An initialised empty slice communicates "this is intentionally empty"

Reference: [Go Slices internals](https://go.dev/blog/slices-intro) | [encoding/json](https://pkg.go.dev/encoding/json) | [Code Style reference](../references/code-style.md) | [Safety reference](../references/safety.md) | [Data Structures reference](../references/data-structures.md)
See also: `golang/references/code-style.md` | `golang/references/safety.md` | `golang/references/data-structures.md`
