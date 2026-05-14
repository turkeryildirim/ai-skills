# Go Security

Security best practices and vulnerability prevention for Go. Defense in depth: validate all inputs, use secure defaults, leverage the standard library's security-aware design.

## When to Load

- Handling user input or external data
- Writing database queries, executing shell commands, rendering HTML
- Implementing authentication or encryption
- Managing secrets, cookies, or session tokens
- Configuring TLS / HTTPS
- Performing security audits or code review

## Security Thinking Model

Before writing or reviewing code, ask three questions:

1. **What are the trust boundaries?** — Where does untrusted data enter? (HTTP requests, file uploads, env vars, DB rows written by other services)
2. **What can an attacker control?** — Which inputs flow into sensitive operations? (SQL queries, shell commands, HTML output, file paths, crypto operations)
3. **What is the blast radius?** — If this defense fails, what's the worst outcome? (Data leak, RCE, privilege escalation, DoS)

## Severity (DREAD)

| Level | Score | Meaning |
|---|---|---|
| Critical | 8–10 | RCE, full data breach, credential theft — fix immediately |
| High | 6–7.9 | Auth bypass, significant data exposure, broken crypto — fix in current sprint |
| Medium | 4–5.9 | Limited exposure, session issues, defense weakening — fix in next sprint |
| Low | 1–3.9 | Minor info disclosure, best-practice deviations — fix opportunistically |

## Quick Reference

| Severity | Vulnerability | Defense | Go Standard Solution |
|---|---|---|---|
| Critical | SQL Injection | Parameterized queries | `database/sql` with `$1`/`?` placeholders |
| Critical | Command Injection | Pass args separately | `exec.Command` with separate args |
| High | XSS | Auto-escaping | `html/template` |
| High | Path Traversal | Scope to root | `os.Root` (Go 1.24+), `filepath.Clean` |
| High | Broken Crypto | Vetted algorithms | `crypto/aes` GCM, `golang.org/x/crypto/argon2` |
| Medium | Timing Attacks | Constant-time compare | `crypto/subtle.ConstantTimeCompare` |
| Medium | HTTP Security | TLS + security headers | `crypto/tls` with `MinVersion: tls.VersionTLS12` |
| Critical | Hardcoded Secrets | Env vars / secret manager | Never in source code or git history |
| High | Race Conditions | Protect shared state | `sync.Mutex`, channels |

## Injection Vulnerabilities

### SQL Injection

```go
// Bad — SQL injection vulnerability
query := fmt.Sprintf("SELECT * FROM users WHERE name = '%s'", name)

// Good — parameterized (PostgreSQL)
err := db.QueryRowContext(ctx, "SELECT * FROM users WHERE name = $1", name).Scan(&user)

// Good — dynamic column name (use allowlist, never user input directly)
allowed := map[string]bool{"name": true, "email": true}
if !allowed[sortCol] {
    return fmt.Errorf("invalid sort column: %s", sortCol)
}
query := fmt.Sprintf("SELECT id, name FROM users ORDER BY %s", sortCol)
```

### Command Injection

```go
// Bad — shell interprets metacharacters (;, |, `, &&)
cmd := exec.Command("bash", "-c", "convert " + userInput)

// Good — pass args as separate elements, never via shell
cmd := exec.Command("convert", inputFile, "-resize", "800x600", outputFile)
```

### XSS — HTML Template Injection

```go
// Bad — text/template does NOT escape HTML
import "text/template"  // wrong for HTML

// Good — html/template auto-escapes context-aware
import "html/template"

tmpl := template.Must(template.ParseFiles("page.html"))
tmpl.Execute(w, userData)  // userData is safely escaped in HTML context

// If you MUST render trusted HTML, use template.HTML explicitly
trustedHTML := template.HTML("<b>Safe Markup</b>")
```

### Path Traversal

```go
// Bad — user can escape the upload directory with ../../../etc/passwd
path := filepath.Join(uploadDir, userFilename)

// Good — os.Root confines access to a directory (Go 1.24+)
root, err := os.OpenRoot("/var/uploads")
if err != nil {
    return fmt.Errorf("opening root: %w", err)
}
f, err := root.Open(userFilename) // fails if userFilename escapes /var/uploads

// Good — pre-1.24: validate path stays within root
clean := filepath.Clean(filepath.Join(uploadDir, userFilename))
if !strings.HasPrefix(clean, uploadDir) {
    return fmt.Errorf("path traversal detected: %s", userFilename)
}
```

## Cryptography

### Token Generation

```go
// Bad — math/rand is predictable; output can be reproduced by attacker
n := rand.Intn(100)

// Good — cryptographically secure random
import crypto_rand "crypto/rand"

b := make([]byte, 32)
if _, err := crypto_rand.Read(b); err != nil {
    return fmt.Errorf("generate token: %w", err)
}
token := hex.EncodeToString(b)
```

### Password Hashing

```go
import "golang.org/x/crypto/bcrypt"

// Hash — use bcrypt, scrypt, or argon2 (intentionally slow, memory-hard)
hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
if err != nil {
    return fmt.Errorf("hashing password: %w", err)
}

// Verify
err = bcrypt.CompareHashAndPassword(hash, []byte(password))
if errors.Is(err, bcrypt.ErrMismatchedHashAndPassword) {
    return ErrInvalidCredentials
}
```

### Symmetric Encryption

```go
import (
    "crypto/aes"
    "crypto/cipher"
    crypto_rand "crypto/rand"
)

// Good — AES-GCM provides authenticated encryption
func Encrypt(key, plaintext []byte) ([]byte, error) {
    block, err := aes.NewCipher(key) // key must be 16, 24, or 32 bytes
    if err != nil {
        return nil, err
    }
    gcm, err := cipher.NewGCM(block)
    if err != nil {
        return nil, err
    }
    nonce := make([]byte, gcm.NonceSize())
    if _, err := crypto_rand.Read(nonce); err != nil {
        return nil, err
    }
    return gcm.Seal(nonce, nonce, plaintext, nil), nil
}

// Bad — AES-ECB / AES-CBC without authentication; attacker can modify ciphertext
```

### Constant-Time Comparison

```go
import "crypto/subtle"

// Bad — == short-circuits on first differing byte, leaks timing info
if token == expectedToken { ... }

// Good — constant-time, no timing oracle
if subtle.ConstantTimeCompare([]byte(token), []byte(expectedToken)) == 1 { ... }
```

## TLS Configuration

```go
// Good — minimum TLS 1.2, strong ciphers
tlsCfg := &tls.Config{
    MinVersion: tls.VersionTLS12,
    CipherSuites: []uint16{
        tls.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
        tls.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
    },
}

// Server
srv := &http.Server{
    Addr:      ":443",
    TLSConfig: tlsCfg,
    ReadTimeout:  5 * time.Second,
    WriteTimeout: 10 * time.Second,
    IdleTimeout:  120 * time.Second,
}

// Client
transport := &http.Transport{TLSClientConfig: tlsCfg}
client := &http.Client{Transport: transport, Timeout: 30 * time.Second}
```

## HTTP Security Headers

```go
func SecurityHeadersMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        w.Header().Set("Content-Security-Policy", "default-src 'self'")
        w.Header().Set("X-Content-Type-Options", "nosniff")
        w.Header().Set("X-Frame-Options", "DENY")
        w.Header().Set("Referrer-Policy", "strict-origin-when-cross-origin")
        next.ServeHTTP(w, r)
    })
}
```

## Cookie Security

```go
http.SetCookie(w, &http.Cookie{
    Name:     "session",
    Value:    sessionToken,
    Path:     "/",
    HttpOnly: true,              // not accessible via JavaScript
    Secure:   true,              // HTTPS only
    SameSite: http.SameSiteLaxMode, // CSRF protection
    MaxAge:   3600,
})
```

## Secrets Management

```go
// Bad — hardcoded secrets end up in git history and CI logs
const apiKey = "sk-1234567890abcdef"

// Good — load from environment
apiKey := os.Getenv("API_KEY")
if apiKey == "" {
    return fmt.Errorf("API_KEY environment variable not set")
}

// Better — secret manager (AWS Secrets Manager, GCP Secret Manager, Vault)
secret, err := secretManager.GetSecret(ctx, "api-key")
```

## Error Responses

```go
// Bad — leaks internal details to attacker
if err := db.QueryRow(...).Scan(&user); err != nil {
    http.Error(w, err.Error(), http.StatusInternalServerError) // exposes DB errors
}

// Good — generic message to client, details in server log
if err := db.QueryRow(...).Scan(&user); err != nil {
    slog.ErrorContext(ctx, "querying user", "error", err, "userID", id)
    http.Error(w, "internal server error", http.StatusInternalServerError)
}
```

## Common Mistakes

| Severity | Mistake | Fix |
|---|---|---|
| Critical | SQL string concatenation | Parameterized queries keep data and code separate |
| Critical | `exec.Command("bash -c ...")` | Shell interprets metacharacters — pass args separately |
| Critical | Hardcoded secrets | Use env vars or secret managers |
| Critical | Ignoring crypto errors | Always check errors — fail closed, never open |
| Critical | Rolling your own crypto | Use `crypto/aes` GCM, `golang.org/x/crypto/argon2` |
| High | `math/rand` for tokens | Output is predictable — use `crypto/rand` |
| High | MD5/SHA1 for passwords | Fast to brute-force — use bcrypt or argon2 |
| High | AES without GCM | CBC/ECB lack authentication — use GCM |
| High | Trusting `X-Forwarded-For` | Headers are trivially forged — use server-side identity |
| Medium | `==` for secret comparison | Leaks timing info — use `crypto/subtle.ConstantTimeCompare` |
| Medium | Returning detailed errors | Stack traces help attackers map your system |

## Security Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Security through obscurity | Hidden URLs discoverable via fuzzing | Authentication + authorization on all endpoints |
| Client-side authorization | JS checks bypassed by any HTTP client | Server-side permission checks on every handler |
| Shared secrets across envs | Staging breach compromises production | Per-environment secrets via secret manager |
| Trusting client-supplied headers | `X-Is-Admin` is trivially forged | Server-side identity verification |

## Tooling

```bash
# Security linter (SAST)
go install github.com/securego/gosec/v2/cmd/gosec@latest
gosec ./...

# Vulnerability scanner
go install golang.org/x/vuln/cmd/govulncheck@latest
govulncheck ./...

# Race detector
go test -race ./...
```

## References

- [Go Security Best Practices](https://go.dev/doc/security/best-practices)
- [gosec Security Linter](https://github.com/securego/gosec)
- [govulncheck](https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck)
- [OWASP Go Secure Coding Practices](https://owasp.org/www-project-go-secure-coding-practices-guide/)
- [golang.org/x/crypto](https://pkg.go.dev/golang.org/x/crypto)
