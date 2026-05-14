---
title: String Handling
impact: MEDIUM
impactDescription: Wrong string tool causes unnecessary allocations or unreadable formatting
tags: style, string, strconv, fmt, strings.Builder
---

## String Handling

**Impact: MEDIUM — Wrong string tool causes unnecessary allocations or unreadable formatting**

Use the right tool for each string operation: `strconv` for simple type conversions (fastest), `fmt.Sprintf` for formatted output, `strings.Builder` for building strings in loops, and `+` only for trivial one-off concatenation.

## Bad Example

```go
// fmt.Sprintf for a simple int-to-string conversion — allocates format machinery
id := fmt.Sprintf("%d", userID)

// + concatenation in a loop — O(n²) allocations
var result string
for _, part := range parts {
    result += part
}

// fmt.Println buries the value in the output — use %q to show boundaries
log.Printf("processing file: " + path) // hard to see trailing spaces or empty string

// String conversion via fmt for a known type
s := fmt.Sprintf("%v", myInt) // use strconv.Itoa
```

## Good Example

```go
// strconv for simple conversions — no format parsing overhead
id := strconv.Itoa(userID)
f  := strconv.FormatFloat(price, 'f', 2, 64)
b  := strconv.FormatBool(active)

// strings.Builder for loops — single allocation
var sb strings.Builder
sb.Grow(estimatedSize) // optional but avoids reallocations
for _, part := range parts {
    sb.WriteString(part)
}
result := sb.String()

// %q in error/log messages — makes empty strings and whitespace visible
log.Printf("processing file: %q", path)
// output: processing file: "/tmp/data.csv"

// fmt.Sprintf for mixed-type formatting
msg := fmt.Sprintf("user %d (%s) logged in from %s", id, name, ip)
```

## Decision Guide

| Use case | Tool |
|----------|------|
| `int` → `string` | `strconv.Itoa` |
| `float64` → `string` | `strconv.FormatFloat` |
| `bool` → `string` | `strconv.FormatBool` |
| `string` → `int` | `strconv.Atoi` |
| Mixed-type formatting | `fmt.Sprintf` |
| Error message with a string value | `fmt.Errorf("...: %q", s, err)` |
| Building in a loop | `strings.Builder` |
| Two strings | `s1 + s2` |
| Contains / HasPrefix / TrimSpace | `strings.*` package |

## Why

- **Performance**: `strconv.Itoa(n)` is 3–5× faster than `fmt.Sprintf("%d", n)` — no format string parsing
- **Allocations**: `strings.Builder` with `Grow` does one allocation; `+=` in a loop does n
- **Debuggability**: `%q` reveals invisible characters (tabs, trailing spaces, empty strings) in logs
- **Clarity**: Using the right tool signals intent to the reader

Reference: [strconv package](https://pkg.go.dev/strconv) | [strings package](https://pkg.go.dev/strings) | [strings.Builder](https://pkg.go.dev/strings#Builder)
