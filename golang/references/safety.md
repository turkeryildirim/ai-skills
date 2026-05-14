# Go Safety — Correctness & Defensive Coding

Prevents panics, silent data corruption, and subtle runtime bugs. Covers nil traps, slice aliasing, numeric overflow, and zero-value design.

## When to Load

- Writing code involving pointers, interfaces, maps, slices, or channels
- Performing numeric conversions
- Using `defer` in loops
- Reviewing code for correctness

## Best Practices Summary

1. **Prefer generics over `any`** when the type set is known — compiler catches mismatches
2. **Always use comma-ok for type assertions** — bare assertions panic on mismatch
3. **Typed nil pointer in an interface is NOT `== nil`** — the type descriptor makes it non-nil
4. **Writing to a nil map panics** — always initialize before use
5. **`append` may reuse the backing array** — both slices share memory if capacity allows
6. **Return defensive copies** from exported functions — prevent callers mutating internals
7. **`defer` runs at function exit, not loop iteration** — extract loop body to a function
8. **Integer conversions truncate silently** — `int64` to `int32` wraps without error
9. **Float arithmetic is not exact** — use epsilon comparison or `math/big`
10. **Design useful zero values** — nil map fields panic on first write; use lazy init

## The nil Interface Trap

The most subtle nil bug in Go — an interface stores `(type, value)`. It is nil only when BOTH are nil:

```go
// Bad — interface{type: *MyHandler, value: nil} is NOT == nil
func getHandler(enabled bool) http.Handler {
    var h *MyHandler  // nil pointer
    if !enabled {
        return h  // returns non-nil interface!
    }
    return &MyHandler{}
}

// Caller
handler := getHandler(false)
if handler == nil {
    // NEVER reaches here — handler is non-nil
}
handler.ServeHTTP(w, r)  // panics: nil pointer dereference

// Good — return nil explicitly
func getHandler(enabled bool) http.Handler {
    if !enabled {
        return nil  // interface{type: nil, value: nil} == nil ✓
    }
    return &MyHandler{}
}
```

## Nil Behavior Quick Reference

| Type | Read from nil | Write to nil | Range over nil |
|---|---|---|---|
| Map | Returns zero value | **panic** | 0 iterations |
| Slice | **panic** (indexed) | **panic** (indexed) | 0 iterations |
| Channel (unbuffered) | Blocks forever | Blocks forever | Blocks forever |
| Pointer | **panic** (dereference) | **panic** | N/A |

```go
// Nil map — read is safe, write panics
var m map[string]int
_ = m["key"]   // ok — returns 0
m["key"] = 1   // PANIC

// Initialize before use
m := make(map[string]int)
// or lazy-init in methods:
func (r *Registry) Add(name string) {
    if r.items == nil {
        r.items = make(map[string]int)
    }
    r.items[name]++
}
```

## Type Assertion — Always Use Comma-Ok

```go
// Bad — panics if the interface holds a different type
handler := i.(http.Handler)

// Good — check first
handler, ok := i.(http.Handler)
if !ok {
    return fmt.Errorf("expected http.Handler, got %T", i)
}
```

## Slice Aliasing — The Append Trap

`append` reuses the backing array if capacity allows. Multiple slices can then share memory:

```go
a := make([]int, 3, 5)  // len=3, cap=5
b := append(a, 4)        // reuses backing array (capacity available)
b[0] = 99               // ALSO modifies a[0] — silent data corruption

// Safe: force a new backing array with full-slice expression
b := append(a[:len(a):len(a)], 4)  // len==cap forces allocation

// Or use slices.Clone (Go 1.21+)
b := slices.Clone(a)
b = append(b, 4)
```

## Defensive Copies in Exported APIs

```go
// Bad — caller can mutate the internal slice
func (c *Cache) Keys() []string {
    return c.keys  // returns the internal slice
}

// Good — return a copy
func (c *Cache) Keys() []string {
    return slices.Clone(c.keys)
}
```

## Numeric Conversion Pitfalls

```go
// Silent truncation — int64 to int32 wraps around without error
var val int64 = 3_000_000_000
i32 := int32(val)  // -1294967296 — silent wraparound

// Safe — check bounds before converting
if val > math.MaxInt32 || val < math.MinInt32 {
    return fmt.Errorf("value %d overflows int32", val)
}
i32 := int32(val)
```

## Float Comparison

```go
// Bad — floating point arithmetic is not exact
0.1 + 0.2 == 0.3  // false

// Good — epsilon comparison
const epsilon = 1e-9
math.Abs((0.1+0.2)-0.3) < epsilon  // true

// For financial: use integer cents or math/big.Rat
```

## Zero-Value Design

Design types so their zero value is useful and safe:

```go
// Good zero value — sync.Mutex, sync.WaitGroup, bytes.Buffer are ready at zero
var mu sync.Mutex
var wg sync.WaitGroup
var buf bytes.Buffer

// Problematic zero value — nil map panics on write
type Cache struct {
    items map[string]any  // nil at zero value
}

// Fix: lazy-init with sync.Once
type Cache struct {
    once  sync.Once
    items map[string]any
}

func (c *Cache) init() {
    c.once.Do(func() {
        c.items = make(map[string]any)
    })
}
```

## References

- [Go Spec — Comparison operators](https://go.dev/ref/spec#Comparison_operators)
- [Go FAQ — nil interface](https://go.dev/doc/faq#nil_error)
- [The Go Memory Model](https://go.dev/ref/mem)
- [slices.Clone](https://pkg.go.dev/slices#Clone)
