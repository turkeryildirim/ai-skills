# Go Data Structures

Built-in and standard library data structures: internals, correct usage, and selection guidance.

## When to Load

- Choosing between slice, array, map, or container/ packages
- Optimizing collection access patterns or memory usage
- Using generics for type-safe containers (Go 1.18+)
- Working with `strings.Builder`, `bytes.Buffer`, or `bufio`

## Quick Reference — When to Use What

| Structure | Use When | Avoid When |
|---|---|---|
| `[]T` slice | General ordered collection, growable | Fixed-size (use array) |
| `[N]T` array | Compile-time-known fixed size, map key | Dynamic size needed |
| `map[K]V` | Key-value lookup, deduplication | Ordered iteration needed |
| `container/list` | Frequent middle insertion/removal | Random access needed |
| `container/heap` | Priority queue, top-K, scheduling | Random access needed |
| `container/ring` | Fixed-size circular buffer, round-robin | Variable size needed |
| `strings.Builder` | Building strings in a loop | Need `io.Reader` interface |
| `bytes.Buffer` | Bidirectional I/O (`io.Reader`+`io.Writer`) | Pure string building |

## Slice Internals

A slice is a 3-word header: `(pointer, length, capacity)`. Multiple slices can share the same backing array — mutations to one are visible in the other (→ see safety.md for aliasing traps).

### Capacity Growth

- < 256 elements: capacity doubles
- ≥ 256 elements: grows by ~25%
- Each growth copies the entire backing array — O(n) cost

**Never rely on when a growth occurs** — the algorithm changed between Go versions.

### Preallocation

```go
// Exact size known
users := make([]User, 0, len(ids))

// Approximate size known
results := make([]Result, 0, estimatedCount)

// Pre-grow before bulk append (Go 1.21+)
s = slices.Grow(s, additionalNeeded)
```

### slices Package (Go 1.21+)

```go
// Sort
slices.Sort(nums)
slices.SortFunc(users, func(a, b User) int {
    return cmp.Compare(a.Name, b.Name)
})

// Search
idx, found := slices.BinarySearch(sortedNums, target)
found := slices.Contains(nums, target)
idx := slices.Index(users, target) // -1 if not found

// Transform
compact := slices.Compact(s)        // remove adjacent duplicates
slices.Reverse(s)                    // in-place reverse
clone := slices.Clone(s)            // independent copy (shallow)
filtered := slices.DeleteFunc(s, func(u User) bool { return !u.Active })

// Check
equal := slices.Equal(a, b)
```

## Map Internals

Maps are hash tables with 8-entry buckets and overflow chains. They are **reference types** — assigning a map copies the pointer, not the data.

```go
// Maps never shrink — use a new map after bulk deletion
m := make(map[string]*User, len(users)) // preallocate to avoid rehashing

// Existence check — comma-ok idiom
value, ok := m[key]
if !ok {
    // key not present
}

// Safe delete (deleting a missing key is a no-op)
delete(m, key)
```

### maps Package (Go 1.21+)

```go
clone := maps.Clone(m)          // shallow copy
equal := maps.Equal(a, b)

// Go 1.23+
for k, v := range maps.All(m) { ... }   // iterator
keys := slices.Collect(maps.Keys(m))    // collect keys
```

## Arrays — Fixed-Size Value Types

Use for compile-time-known fixed sizes only. Copied entirely on assignment.

```go
type Digest [32]byte           // SHA-256 — fixed size, value semantics
var grid [3][3]int             // multi-dimensional
cache := map[[2]int]Result{}   // arrays are comparable — usable as map keys
```

Prefer slices for everything dynamic — arrays can't grow and are expensive to pass by value when large.

## container/ Standard Library

### container/heap — Priority Queue

```go
type IntHeap []int

func (h IntHeap) Len() int           { return len(h) }
func (h IntHeap) Less(i, j int) bool { return h[i] < h[j] } // min-heap
func (h IntHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *IntHeap) Push(x any)        { *h = append(*h, x.(int)) }
func (h *IntHeap) Pop() any {
    old := *h; n := len(old)
    x := old[n-1]; *h = old[:n-1]
    return x
}

h := &IntHeap{3, 1, 4, 1, 5}
heap.Init(h)
heap.Push(h, 2)
top := heap.Pop(h).(int) // 1 — minimum
```

### container/list — Doubly-Linked List

```go
// Use for LRU caches, frequent middle insertion/removal
// Poor cache locality — benchmark before choosing over slice
l := list.New()
e := l.PushBack("first")
l.PushFront("zero")
l.Remove(e)

for e := l.Front(); e != nil; e = e.Next() {
    fmt.Println(e.Value)
}
```

### container/ring — Circular Buffer

```go
r := ring.New(5) // fixed-size circular buffer
for i := range 5 {
    r.Value = i
    r = r.Next()
}
// iterate
r.Do(func(v any) { fmt.Println(v) })
```

## strings.Builder vs bytes.Buffer

```go
// strings.Builder — pure string concatenation
// String() returns the accumulated string without copying
var sb strings.Builder
sb.Grow(estimatedSize) // pre-grow to avoid reallocation
for _, word := range words {
    sb.WriteString(word)
    sb.WriteByte(' ')
}
result := sb.String() // no copy

// bytes.Buffer — bidirectional I/O
// Implements io.Reader + io.Writer + io.WriterTo
var buf bytes.Buffer
buf.Grow(estimatedSize)
json.NewEncoder(&buf).Encode(data)  // write
io.Copy(w, &buf)                    // read
```

## Generic Collections (Go 1.18+)

Use the tightest constraint possible:

```go
// Set — comparable constraint
type Set[T comparable] map[T]struct{}

func NewSet[T comparable](items ...T) Set[T] {
    s := make(Set[T], len(items))
    for _, item := range items {
        s[item] = struct{}{}
    }
    return s
}

func (s Set[T]) Add(v T)           { s[v] = struct{}{} }
func (s Set[T]) Contains(v T) bool { _, ok := s[v]; return ok }
func (s Set[T]) Delete(v T)        { delete(s, v) }
```

```go
// Stack — any type
type Stack[T any] struct{ items []T }

func (s *Stack[T]) Push(v T)      { s.items = append(s.items, v) }
func (s *Stack[T]) Pop() (T, bool) {
    if len(s.items) == 0 {
        var zero T
        return zero, false
    }
    n := len(s.items) - 1
    v := s.items[n]
    s.items = s.items[:n]
    return v, true
}
```

## Pointer Types

| Type | Use case |
|---|---|
| `*T` | Mutation, optional values, large structs |
| `unsafe.Pointer` | FFI, low-level memory — only the 6 spec-valid conversion patterns |
| `weak.Pointer[T]` (Go 1.24+) | Caches and canonicalization — allows GC to reclaim |

```go
// weak.Pointer — GC-safe cache (Go 1.24+)
import "weak"

type Cache[K comparable, V any] struct {
    mu    sync.Mutex
    items map[K]weak.Pointer[V]
}

func (c *Cache[K, V]) Get(key K) (*V, bool) {
    c.mu.Lock()
    defer c.mu.Unlock()
    wp, ok := c.items[key]
    if !ok {
        return nil, false
    }
    v := wp.Value() // nil if GC has reclaimed the object
    return v, v != nil
}
```

## Copy Semantics Quick Reference

| Type | Copy behavior | Independence |
|---|---|---|
| `int`, `float`, `bool`, `string` | Value (deep copy) | Fully independent |
| `array`, `struct` | Value (deep copy) | Fully independent |
| `slice` | Header copied, backing array shared | Use `slices.Clone` |
| `map` | Reference copied | Use `maps.Clone` |
| `channel` | Reference copied | Same channel |
| `*T` | Address copied | Same underlying value |

## Common Mistakes

| Mistake | Fix |
|---|---|
| Slice growth in a loop without preallocation | Use `make([]T, 0, n)` or `slices.Grow` — each growth copies the backing array |
| `container/list` when a slice would work | Linked lists have poor cache locality — benchmark first |
| `bytes.Buffer` for pure string building | `Buffer.String()` copies; `strings.Builder.String()` does not |
| `unsafe.Pointer` stored as `uintptr` across statements | GC can move objects between statements — dangling reference |
| Large struct values in maps | Map access copies the entire value — use `map[K]*V` for large types |
| Iterating over map in sorted order without sorting keys first | Map iteration order is random — collect keys, sort, then iterate |

## Third-Party Libraries

For advanced data structures beyond stdlib:

- `emirpasic/gods` — trees, sets, lists, stacks, maps, queues
- `deckarep/golang-set` — thread-safe and non-thread-safe sets
- `gammazero/deque` — fast double-ended queue

## References

- [Go Data Structures (Russ Cox)](https://research.swtch.com/godata)
- [slices package](https://pkg.go.dev/slices)
- [maps package](https://pkg.go.dev/maps)
- [container package](https://pkg.go.dev/container)
