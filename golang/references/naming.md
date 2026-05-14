# Go Naming Conventions

> "Clear is better than clever." — Go Proverbs

Go favors short, readable names. Capitalization controls visibility — uppercase is exported, lowercase is unexported. All identifiers MUST use MixedCaps, NEVER underscores.

## When to Load

- Writing new Go code or reviewing naming decisions
- Choosing between naming alternatives (New vs NewTypeName, isConnected vs connected)
- Debating package names or identifier casing
- Asking about Go naming best practices

## Quick Reference

| Element | Convention | Example |
|---|---|---|
| Package | lowercase, single word | `json`, `http`, `tabwriter` |
| File | lowercase, underscores OK | `user_handler.go` |
| Exported name | UpperCamelCase | `ReadAll`, `HTTPClient` |
| Unexported | lowerCamelCase | `parseToken`, `userCount` |
| Interface | method name + `-er` suffix | `Reader`, `Closer`, `Stringer` |
| Struct | MixedCaps noun | `Request`, `FileHeader` |
| Constant | MixedCaps (not ALL_CAPS) | `MaxRetries`, `defaultTimeout` |
| Receiver | 1-2 letter abbreviation | `func (s *Server)`, `func (b *Buffer)` |
| Error variable | `Err` prefix | `ErrNotFound`, `ErrTimeout` |
| Error type | `Error` suffix | `PathError`, `SyntaxError` |
| Constructor | `New` (single type) or `NewTypeName` (multi) | `ring.New`, `http.NewRequest` |
| Boolean field/method | `is`, `has`, `can` prefix | `isReady`, `IsConnected()` |
| Test function | `Test` + function name | `TestParseToken` |
| Acronym | all caps or all lower | `URL`, `HTTPServer`, `xmlParser` |
| Enum (iota) | type name prefix, zero = unknown | `StatusUnknown` at 0, `StatusReady` |
| Error string | lowercase incl. acronyms, no punctuation | `"image: unknown format"`, `"invalid id"` |
| Format func | `f` suffix | `Errorf`, `Wrapf`, `Logf` |
| Option func | `With` + field name | `WithPort()`, `WithLogger()` |
| Must variant | `Must` prefix (panics on error) | `MustParse()`, `MustLoadConfig()` |
| Context variant | `WithContext` suffix | `FetchWithContext`, `QueryContext` |

## MixedCaps — Non-negotiable

All Go identifiers MUST use `MixedCaps`. NEVER use underscores — the only exceptions are test subcases (`TestFoo_InvalidInput`), generated code, and OS/cgo interop.

```go
// Good
MaxPacketSize
userCount
parseHTTPResponse

// Bad — conflicts with Go's export mechanism and tooling
MAX_PACKET_SIZE   // C/Python style
max_packet_size   // snake_case
kMaxBufferSize    // Hungarian notation
```

## Avoid Stuttering

A name MUST NOT repeat information already present in the package name, type name, or surrounding context. Go call sites always include the package name — repeating it wastes the reader's time.

```go
// Good — clean at the call site
http.Client       // not http.HTTPClient
json.Decoder      // not json.JSONDecoder
user.New()        // not user.NewUser()
config.Parse()    // not config.ParseConfig()
```

See rule `idiomatic-no-stutter`.

## Constructor Naming

When a package exports a **single primary type**, the constructor is `New()`:

```go
// In package ring:
func New(n int) *Ring { ... }   // caller: ring.New(10)

// In package http — multiple types:
func NewRequest(method, url string, body io.Reader) (*Request, error) { ... }
func NewServeMux() *ServeMux { ... }
```

See rule `idiomatic-constructor-naming`.

## Boolean Fields and Methods

Unexported boolean fields MUST use `is`/`has`/`can` prefix. Exported getters keep the prefix.

```go
type Server struct {
    isRunning   bool    // not: running
    hasTLS      bool    // not: tls
}

func (s *Server) IsRunning() bool { return s.isRunning }
func (s *Server) HasTLS() bool    { return s.hasTLS }
```

See rule `idiomatic-boolean-naming`.

## Error Strings — Fully Lowercase

Error strings MUST be fully lowercase, including acronyms, with no trailing punctuation. They are often concatenated mid-sentence.

```go
// Good
errors.New("connection refused")
fmt.Errorf("invalid message id: %w", err)  // not "ID"

// Bad
errors.New("Connection refused.")           // capitalized + punctuation
fmt.Errorf("invalid message ID: %w", err)  // uppercase acronym mid-string
```

Sentinel errors should include the package name:
```go
// Good — origin is clear
var ErrNotFound = errors.New("apiclient: not found")
```

## Enum Zero Values

Always place an explicit `Unknown`/`Invalid` sentinel at `iota` position 0:

```go
// Bad — uninitialized var s Status silently becomes StatusReady
type Status int
const (
    StatusReady Status = iota  // 0 — uninitialized looks like "ready"
    StatusActive
)

// Good — zero value is explicit "not set"
type Status int
const (
    StatusUnknown Status = iota  // 0 — clearly uninitialized
    StatusReady
    StatusActive
)
```

See rule `idiomatic-enum-zero-value`.

## Common Mistakes

| Mistake | Fix |
|---|---|
| `ALL_CAPS` constants | Use `MixedCaps` (`MaxRetries`) |
| `GetName()` getter | Use `Name()` — Go omits `Get`. Keep `Is`/`Has`/`Can` for booleans |
| `Url`, `Http`, `Json` | All caps or all lower: `URL`, `HTTP`, `xmlParser` |
| `this` or `self` receiver | Use 1-2 letter abbreviation (`s` for `Server`) |
| `util`, `helper` packages | Name by what it does, not that it's a helper |
| `http.HTTPClient` stuttering | `http.Client` — package name appears at call site |
| `user.NewUser()` | Single type → `user.New()` |
| `connected bool` field | Use `isConnected` — reads as a question |
| `"invalid ID"` error string | Must be fully lowercase: `"invalid id"` |
| `StatusReady` at iota 0 | Zero value should be `StatusUnknown` |
| Plural package names | Go convention is singular (`net/url` not `net/urls`) |
| `FetchCtx()` context variant | Use `WithContext` suffix: `FetchWithContext()` |
| Mixing `With*`, `Set*`, `Use*` options | Stick to `With*` for functional options |
| `userSlice` type in name | Use `users` — describes what, not how |
| Long names in short scopes | `i` is fine for a 3-line loop |

## Enforce with Linters

| Linter | What it catches |
|---|---|
| `revive` | Exported without doc, stuttering, receiver naming |
| `errname` | Error type/variable naming |
| `predeclared` | Names that shadow builtins |
| `misspell` | Typos in identifiers and comments |

## References

- [Effective Go — Names](https://go.dev/doc/effective_go#names)
- [Go Code Review Comments — Naming](https://github.com/golang/go/wiki/CodeReviewComments#mixed-caps)
- [Uber Go Style Guide — Naming](https://github.com/uber-go/guide/blob/master/style.md)
