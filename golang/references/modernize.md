# Go Code Modernization

Keep codebases current with the latest Go idioms and standard library improvements. Prioritize safety and correctness fixes first, then readability.

## When to Load

- Reviewing or refactoring existing Go code
- After a Go version upgrade
- When linter reports `modernize` warnings
- Asking about Go upgrades or deprecated APIs

## Version Reference

| Version | Release | Key features |
|---|---|---|
| Go 1.21 | Aug 2023 | `slices`, `maps`, `cmp`, `log/slog`, `min`/`max` builtins |
| Go 1.22 | Feb 2024 | Range over int, loop var fix, `math/rand/v2`, `cmp.Or` |
| Go 1.23 | Aug 2024 | Range-over-func iterators, `unique`, `iter` package |
| Go 1.24 | Feb 2025 | `weak.Pointer`, `os.Root`, `runtime.AddCleanup`, `b.Loop()`, `t.Context()` |
| Go 1.25 | Aug 2025 | `sync.WaitGroup.Go`, `testing/synctest.Test` |
| Go 1.26 | Feb 2026 | `encoding/json/v2`, `modernize` linter in `go fix` |

## Migration Priority

### 1. Safety & Correctness (Do First)

```go
// Replace math/rand with math/rand/v2 (Go 1.22+)
// Old — requires Seed, predictable sequence
rand.Seed(time.Now().UnixNano())
n := rand.Intn(100)

// New — auto-seeded, better algorithm
n := rand.N(100)  // math/rand/v2
```

```go
// Use errors.Is / errors.As instead of direct comparison
if err == sql.ErrNoRows { ... }          // bad
if errors.Is(err, sql.ErrNoRows) { ... } // good
```

```go
// Use os.Root for user-supplied file paths (Go 1.24+) — prevents path traversal
root, err := os.OpenRoot("/var/data")
f, err := root.Open(userPath)  // confined to /var/data
```

### 2. Readability & Maintainability

```go
// Replace interface{} with any (Go 1.18+)
func process(v interface{}) { ... }   // old
func process(v any) { ... }           // new

// Use min/max builtins (Go 1.21+)
result := math.Min(float64(a), float64(b))  // old
result := min(a, b)                          // new (works with any ordered type)

// Range over integer (Go 1.22+)
for i := 0; i < 10; i++ { ... }   // old
for i := range 10 { ... }          // new
```

```go
// Use slices package (Go 1.21+) instead of sort
sort.Slice(users, func(i, j int) bool {  // old
    return users[i].Name < users[j].Name
})
slices.SortFunc(users, func(a, b User) int {  // new
    return cmp.Compare(a.Name, b.Name)
})

// Contains check
found := false
for _, u := range users {
    if u.ID == id { found = true; break }
}
// becomes:
found := slices.ContainsFunc(users, func(u User) bool { return u.ID == id })
```

```go
// Use cmp.Or for default values (Go 1.22+)
name := value
if name == "" { name = defaultValue }
// becomes:
name := cmp.Or(value, defaultValue)
```

```go
// sync.OnceValue for lazy initialization (Go 1.21+)
var once sync.Once
var config *Config
getConfig := func() *Config {
    once.Do(func() { config = loadConfig() })
    return config
}
// becomes:
getConfig := sync.OnceValue(loadConfig)
```

```go
// sync.WaitGroup.Go (Go 1.25+)
var wg sync.WaitGroup
wg.Add(1)
go func() {
    defer wg.Done()
    process()
}()
// becomes:
wg.Go(process)
```

### 3. Testing Modernization

```go
// t.Context() (Go 1.24+) — test context that cancels on test cleanup
ctx := context.Background()           // old
ctx, cancel := context.WithCancel(context.Background())
defer cancel()

ctx := t.Context()                    // new — automatically cancelled on test end

// b.Loop() (Go 1.24+) — replaces b.N loop in benchmarks
for i := 0; i < b.N; i++ { ... }    // old
for b.Loop() { ... }                  // new
```

### 4. Observability Modernization

```go
// Migrate from zap/logrus/zerolog to log/slog (Go 1.21+)
zap.L().Info("event", zap.String("key", val))   // old
slog.Info("event", "key", val)                   // new

// Use slog.InfoContext for trace correlation
slog.Info("event", "key", val)          // old — no context
slog.InfoContext(ctx, "event", "key", val) // new — injects trace_id
```

## Deprecated Packages Migration

| Deprecated | Replacement | Since |
|---|---|---|
| `math/rand` | `math/rand/v2` | Go 1.22 |
| `ioutil.ReadAll` | `io.ReadAll` | Go 1.16 |
| `ioutil.ReadFile` | `os.ReadFile` | Go 1.16 |
| `ioutil.WriteFile` | `os.WriteFile` | Go 1.16 |
| `ioutil.TempFile` | `os.CreateTemp` | Go 1.16 |
| `ioutil.TempDir` | `os.MkdirTemp` | Go 1.16 |
| `sort.Slice` | `slices.SortFunc` | Go 1.21 |
| `sort.Search` | `slices.BinarySearchFunc` | Go 1.21 |
| `reflect.SliceHeader` | `unsafe.Slice` | Go 1.21 |
| `runtime.SetFinalizer` | `runtime.AddCleanup` | Go 1.24 |
| `crypto/elliptic` (most) | `crypto/ecdh` | Go 1.21 |

## Linter: modernize

The `modernize` linter (golangci-lint v2.6.0+) automatically detects code patterns that have modern replacements:

```yaml
# .golangci.yml
linters:
  enable:
    - modernize
```

Also available via `gopls` (IDE) and `go fix` (Go 1.26+).

## References

- [Go Release Notes](https://go.dev/doc/devel/release)
- [golangci-lint modernize](https://golangci-lint.run/usage/linters/#modernize)
- [golang.org/x/tools/modernize](https://pkg.go.dev/golang.org/x/tools/gopls/internal/analysis/modernize)
