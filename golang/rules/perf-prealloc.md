---
title: Pre-allocate Slices and Maps with Known Capacity
impact: MEDIUM
impactDescription: Eliminates repeated memory reallocations in hot paths
tags: performance, allocation, slice, map, make
---

## Pre-allocate Slices and Maps with Known Capacity

**Impact: MEDIUM — Eliminates repeated memory reallocations in hot paths**

When the final size of a slice or map is known (or estimable) in advance, pass the capacity to `make`. This prevents repeated doubling reallocations as elements are appended.

## Bad Example

```go
func toNames(users []User) []string {
    var names []string           // zero-length, zero-capacity
    for _, u := range users {
        names = append(names, u.Name)
        // Go doubles capacity on each reallocation: 0→1→2→4→8→16...
        // For 1000 users: ~10 reallocations and copies
    }
    return names
}

func indexByID(users []User) map[int]User {
    m := make(map[int]User)     // no hint — rehashes as it grows
    for _, u := range users {
        m[u.ID] = u
    }
    return m
}
```

## Good Example

```go
func toNames(users []User) []string {
    names := make([]string, 0, len(users)) // single allocation
    for _, u := range users {
        names = append(names, u.Name)
    }
    return names
}

func indexByID(users []User) map[int]User {
    m := make(map[int]User, len(users)) // pre-size the hash table
    for _, u := range users {
        m[u.ID] = u
    }
    return m
}
```

## When to Apply

- Slice/map is built by iterating over another collection of **known** length
- In benchmarked hot paths where allocation pressure is measured
- When `b.ReportAllocs()` shows more allocations than expected

## Do Not Pre-allocate Speculatively

Only pre-allocate with a known or well-estimated capacity. `make([]T, 0, 1000)` wastes memory when the common case is 10 items. Measure first.

## Scope: Performance Only

This rule is about **performance** — eliminating reallocations on a hot path. For the correctness reason to always initialise slices and maps (nil maps panic; nil slices serialise to JSON `null`), see `idiomatic-slice-map-init`.

## Why

- **Allocation count**: `make([]T, 0, n)` → 1 allocation regardless of n
- **GC pressure**: Fewer short-lived objects means less GC work
- **CPU**: No `memmove` of growing arrays
- **golangci-lint**: `prealloc` linter detects these automatically

Reference: [Go Slices internals](https://go.dev/blog/slices-intro) | [prealloc linter](https://github.com/alexkohler/prealloc) | [Performance reference](../references/performance.md) | [Data Structures reference](../references/data-structures.md)
See also: `golang/references/performance.md` | `golang/references/data-structures.md`
