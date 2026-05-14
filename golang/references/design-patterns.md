# Go Design Patterns & Idioms

Idiomatic Go patterns for production-ready code. Functional options, constructors, resource management, resilience, string/byte handling, and streaming.

## When to Load

- Designing constructor APIs
- Choosing between architectural patterns
- Setting up graceful shutdown or timeout patterns
- Implementing functional options vs builder pattern
- Working with strings, bytes, or large data sets

## Best Practices Summary

1. Constructors SHOULD use **functional options** — they scale better as APIs evolve
2. **Avoid `init()`** — runs implicitly, cannot return errors, makes testing unpredictable
3. Enums SHOULD **start at 1** (or Unknown sentinel at 0) — Go's zero value silently passes
4. Error cases MUST be **handled first** with early return — keep happy path flat
5. **`defer Close()` immediately after opening** — later code changes can skip cleanup
6. Every external call SHOULD **have a timeout** — a slow upstream hangs your goroutine indefinitely
7. **Limit everything** — pool sizes, queue depths, buffers — unbounded resources crash
8. Retry logic MUST **check context cancellation** between attempts
9. Use **`[]byte` for mutation and I/O**, `string` for display and keys
10. **Compile regexp once** at package level — compilation is O(n) and allocates
11. **Stream large data** — loading millions of rows causes OOM; streaming keeps memory constant
12. **`//go:embed` for static assets** — eliminates runtime file I/O errors

## Functional Options (Preferred Constructor Pattern)

```go
type Server struct {
    addr         string
    readTimeout  time.Duration
    writeTimeout time.Duration
    maxConns     int
}

type Option func(*Server)

func WithReadTimeout(d time.Duration) Option {
    return func(s *Server) { s.readTimeout = d }
}

func WithWriteTimeout(d time.Duration) Option {
    return func(s *Server) { s.writeTimeout = d }
}

func WithMaxConns(n int) Option {
    return func(s *Server) { s.maxConns = n }
}

func NewServer(addr string, opts ...Option) *Server {
    s := &Server{
        addr:         addr,
        readTimeout:  5 * time.Second,
        writeTimeout: 10 * time.Second,
        maxConns:     100,
    }
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// Usage — clean, backward-compatible, self-documenting
srv := NewServer(":8080",
    WithReadTimeout(30*time.Second),
    WithMaxConns(500),
)
```

**Why functional options over a config struct?**
- Adding a new option is backward-compatible — callers don't change
- Options can validate and return errors
- Zero value is meaningful (defaults applied in the constructor)
- Options can compose and override

## Avoid init()

```go
// Bad — hidden global state, cannot return errors
var db *sql.DB

func init() {
    var err error
    db, err = sql.Open("postgres", os.Getenv("DATABASE_URL"))
    if err != nil {
        log.Fatal(err) // only option — no error return
    }
}

// Good — explicit initialization, injectable, testable
func NewUserRepository(db *sql.DB) *UserRepository {
    return &UserRepository{db: db}
}
```

`init()` problems: runs before tests, ordering is by filename alphabetically (fragile), cannot return errors, hidden side effects.

## Compile Regexp Once

```go
// Bad — recompiles on every call
func ValidateEmail(email string) bool {
    re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
    return re.MatchString(email)
}

// Good — compile once at package level
var emailRegex = regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)

func ValidateEmail(email string) bool {
    return emailRegex.MatchString(email)
}
```

## Compile-Time Interface Check

```go
// Verify at compile time that *MyHandler implements http.Handler
var _ http.Handler = (*MyHandler)(nil)
```

Place near the type definition. Compilation fails with a clear message if the interface contract is broken.

## Resource Management — defer Immediately

```go
// Bad — resource may be leaked if later code panics before Close
f, err := os.Open(path)
if err != nil {
    return err
}
// ... other code that might return early ...
defer f.Close()  // may never execute if we returned early above

// Good — defer immediately after successful open
f, err := os.Open(path)
if err != nil {
    return err
}
defer f.Close()  // guaranteed to run when function exits
```

## defer in Loops — Extract to Function

`defer` runs at function exit, not at the end of each loop iteration:

```go
// Bad — file handles accumulate, all closed at function end
for _, path := range paths {
    f, _ := os.Open(path)
    defer f.Close()      // wrong: all defers run when outer function returns
    process(f)
}

// Good — close at end of each iteration
for _, path := range paths {
    if err := processFile(path); err != nil {
        return err
    }
}

func processFile(path string) error {
    f, err := os.Open(path)
    if err != nil {
        return err
    }
    defer f.Close()  // runs when processFile returns
    return process(f)
}
```

## Resilience — Timeouts on Every External Call

```go
// Bad — a slow upstream hangs the goroutine indefinitely
resp, err := http.Get(url)

// Good — every external call has a deadline
ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
defer cancel()

req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
if err != nil {
    return fmt.Errorf("build request: %w", err)
}
resp, err := http.DefaultClient.Do(req)
```

## string vs []byte vs []rune

| Type | Use for |
|---|---|
| `string` | Immutable text, map keys, display, comparison |
| `[]byte` | I/O operations, mutation, building output |
| `[]rune` | Character-by-character Unicode processing |

Avoid repeated conversions — each `string([]byte)` or `[]byte(string)` allocates.

## Static Assets with //go:embed

```go
import "embed"

//go:embed templates/*
var templateFS embed.FS

//go:embed static/version.txt
var version string
```

Embeds at compile time — no runtime file path errors, single binary deployment.

## References

- [Effective Go](https://go.dev/doc/effective_go)
- [Go Patterns](https://github.com/tmrts/go-patterns)
- [Functional Options — Dave Cheney](https://dave.cheney.net/2014/10/17/functional-options-for-friendly-apis)
