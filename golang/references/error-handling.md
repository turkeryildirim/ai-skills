# Go Error Handling

Error creation, wrapping, inspection, single handling rule, sentinel errors, custom types, panic discipline, and structured logging.

## When to Load

- Implementing functions that can fail
- Reviewing error handling patterns
- Designing error hierarchies for a package
- Setting up structured logging at error boundaries

## Best Practices Summary

1. **Always check returned errors** — NEVER discard with `_`
2. **Wrap with context**: `fmt.Errorf("operation: %w", err)`
3. **Error strings MUST be lowercase**, without trailing punctuation, including acronyms
4. **Use `%w` internally, `%v` at system boundaries** to control chain exposure
5. **Use `errors.Is` and `errors.As`** — never direct comparison or type assertion
6. **Use `errors.Join`** (Go 1.20+) to combine independent errors
7. **Log OR return — NEVER both** (single handling rule)
8. **Sentinel errors** for expected conditions; **custom types** for structured data
9. **NEVER `panic` for expected conditions** — reserve for truly unrecoverable states
10. **Use `slog`** (Go 1.21+) for structured error logging
11. **Keep error messages low-cardinality** — don't interpolate IDs, paths, counts into message strings

## Error Creation

### `errors.New` — static error messages

```go
var ErrNotFound = errors.New("not found")
var ErrUnauthorized = errors.New("unauthorized")
```

### `fmt.Errorf` — dynamic wrapping

```go
return fmt.Errorf("getting user %s: %w", id, err)
```

### Decision Table

| Situation | Strategy |
|---|---|
| Caller needs to match a specific condition | Sentinel (`var ErrNotFound = errors.New(...)`) |
| Caller needs to extract structured data | Custom error type with `Unwrap()` |
| Error is purely informational | `fmt.Errorf` or `errors.New` |
| Need stack traces, user context, structured attrs | `samber/oops` |

## Error Wrapping with `%w`

```go
func (s *UserService) GetUser(id string) (*User, error) {
    user, err := s.repo.FindByID(id)
    if err != nil {
        return nil, fmt.Errorf("getting user %s: %w", id, err)
    }
    return user, nil
}
```

### `%w` vs `%v`: Controlling Chain Exposure

```go
// Internal — wrap to preserve chain
return fmt.Errorf("querying database: %w", err)

// Public API boundary — break chain to hide internals
return fmt.Errorf("item unavailable: %v", err)  // callers cannot unwrap
```

## Inspecting Errors

```go
// errors.Is — match sentinel (traverses chain)
if errors.Is(err, sql.ErrNoRows) {
    return nil, ErrNotFound
}

// errors.As — extract typed error (traverses chain)
var ve *ValidationError
if errors.As(err, &ve) {
    log.Printf("field %s: %s", ve.Field, ve.Message)
}
```

## Combining Errors — errors.Join (Go 1.20+)

```go
func validateUser(u User) error {
    var errs []error
    if u.Name == "" {
        errs = append(errs, errors.New("name is required"))
    }
    if u.Email == "" {
        errs = append(errs, errors.New("email is required"))
    }
    return errors.Join(errs...)  // nil if errs is empty
}
```

## Custom Error Types

```go
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation on %s: %s", e.Field, e.Message)
}

// For wrapping another error — implement Unwrap()
type QueryError struct {
    Query string
    Err   error
}

func (e *QueryError) Error() string  { return fmt.Sprintf("query %q: %v", e.Query, e.Err) }
func (e *QueryError) Unwrap() error  { return e.Err }
```

## The Single Handling Rule — Log OR Return

An error MUST be handled exactly once: either log it or return it, NEVER both. Doing both causes duplicate log entries.

```go
// Bad — logs AND returns
func processOrder(id string) error {
    err := chargeCard(id)
    if err != nil {
        log.Printf("failed to charge card: %v", err)  // logged here
        return fmt.Errorf("charging card: %w", err)    // AND returned
    }
    return nil
}

// Good — return with context; let the top-level handler log
func processOrder(id string) error {
    if err := chargeCard(id); err != nil {
        return fmt.Errorf("charging card: %w", err)
    }
    return nil
}

// Top-level boundary (HTTP handler, main) — log once
func handleOrder(w http.ResponseWriter, r *http.Request) {
    if err := processOrder(r.FormValue("id")); err != nil {
        slog.Error("order failed", "error", err)
        http.Error(w, "internal error", http.StatusInternalServerError)
        return
    }
    w.WriteHeader(http.StatusOK)
}
```

See rule `error-single-handling`.

## Low-Cardinality Error Messages

APM tools (Datadog, Loki, Sentry) group errors by message. Interpolating variable data creates unique messages per request — dashboards become unusable.

```go
// Bad — every user/file combo is a unique error message
return fmt.Errorf("error in %s at line %d of the csv", csvPath, line)

// Good (stdlib) — static message, variable data attached at log site
err := errors.New("csv parsing error")
slog.Error("csv parsing failed", "error", err, "path", csvPath, "line", line)

// Good (samber/oops) — attributes travel with the error
return oops.With("csv_path", csvPath).With("csv_line", line).Errorf("csv parsing error")
```

See rule `error-low-cardinality`.

## Structured Logging with slog (Go 1.21+)

```go
// Basic structured error log
slog.Error("operation failed",
    "error", err,
    "user_id", userID,
    "request_id", requestID,
)

// Log levels for severity
slog.Debug("cache miss", "key", key)
slog.Info("user logged in", "user_id", id)
slog.Warn("rate limit approaching", "remaining", n)
slog.Error("payment failed", "error", err, "order_id", orderID)
```

## Panic Discipline

```go
// Acceptable — package-level init with invalid programmer input
var compiled = regexp.MustCompile(`^\d{4}-\d{2}-\d{2}$`)

// Acceptable — invariant violation (programmer error)
func (s *Stack) Pop() any {
    if s.Len() == 0 {
        panic("stack: Pop called on empty stack")
    }
    // ...
}

// Never — panic for an expected runtime failure
func GetUser(id string) *User {
    user, err := db.Find(id)
    if err != nil {
        panic(err)  // WRONG — return the error instead
    }
    return user
}
```

## References

- [Working with Errors in Go 1.13](https://go.dev/blog/go1.13-errors)
- [errors package](https://pkg.go.dev/errors)
- [log/slog package](https://pkg.go.dev/log/slog)
- [samber/oops](https://github.com/samber/oops)
