# Laravel + React/Inertia OWASP Security

Dual-purpose: full OWASP Top 10 audit procedure, and secure-coding reference. Covers Laravel 13 backends and React/Inertia.js front-ends.

## How to Audit

### Step 1 — Detect Stack

Check for React + Inertia.js:
- `app/Http/Middleware/HandleInertiaRequests.php` exists
- `resources/js/` contains `.tsx` or `.jsx`
- `inertiajs/inertia-laravel` in `composer.json`
- `@inertiajs/react` in `package.json`

State the result at the top of the report.

### Step 2 — Scope

- If arguments provided → review only those files / features
- Otherwise → review the whole codebase

### Step 3 — Run the Checklist

For each item output **PASS** / **FAIL** / **N/A** with `file:line` and a fix recommendation on failure. **Never reproduce secrets, tokens, or `.env` content in the report.**

---

## OWASP Top 10 Checklist

### 1. Broken Access Control (A01)

- [ ] Middleware protects all route groups by role
- [ ] Queries scoped to the authenticated user (`->where('user_id', auth()->id())`)
- [ ] No direct object reference without ownership check
- [ ] Gates and Policies used
- [ ] Frontend role checks mirrored server-side

### 2. Cryptographic Failures (A02)

- [ ] Passwords hashed with `Hash::make()` or the `'hashed'` cast
- [ ] No MD5 / SHA1 for password hashing
- [ ] Sensitive fields encrypted with `Crypt::encryptString()` or `'encrypted'` cast
- [ ] `APP_KEY` long, random, unique per environment
- [ ] `URL::signedRoute()` for one-time sensitive actions

### 3. Injection (A03)

**SQL / Mass Assignment:**
- [ ] No string concatenation in `whereRaw`/`selectRaw`/`orderByRaw` — `?` bindings only
- [ ] Column names never from user input without a whitelist
- [ ] No `$request->all()` to `create`/`fill`/`update`
- [ ] No `forceFill`/`forceCreate` with unvalidated input
- [ ] Models define `$fillable` explicitly (never `$guarded = []`)
- [ ] Controllers use `$request->validated()`

**XSS (Blade & React):**
- [ ] No `{!! $userInput !!}` with untrusted data
- [ ] `{{ }}` for all user output in Blade
- [ ] No `dangerouslySetInnerHTML` without `DOMPurify.sanitize()`
- [ ] `href` / `src` never from unvalidated user input
- [ ] No `eval` / `new Function` / `setTimeout(string)` on user input
- [ ] External CDN scripts use Subresource Integrity

### 4. Insecure Design (A04)

- [ ] Prices, totals, discounts enforced server-side
- [ ] Sensitive ops require secondary confirmation
- [ ] No mass action endpoints without per-item auth
- [ ] Admin features isolated by middleware (not just hidden in UI)
- [ ] Payment amounts computed server-side, not passed as inputs

### 5. Security Misconfiguration (A05)

- [ ] `APP_DEBUG=false` in production
- [ ] `.env` in `.gitignore`
- [ ] Non-root DB user in production
- [ ] `storage/` and `bootstrap/cache/` not world-writable
- [ ] `APP_KEY` set and unique
- [ ] CORS `allowed_origins` not `['*']` for authenticated routes

### 6. Vulnerable Components (A06)

- [ ] `composer audit` passes
- [ ] `npm audit` passes
- [ ] Laravel on a supported version

### 7. Authentication Failures (A07)

**Auth:**
- [ ] Uses Breeze / Fortify / Jetstream, not custom
- [ ] bcrypt / argon2
- [ ] Login throttled
- [ ] Password reset + email verify throttled
- [ ] Payment routes throttled
- [ ] `session()->regenerate()` after login

**Cookie / Session:**
- [ ] `http_only = true`, `same_site = lax|strict`, `secure = true|null`
- [ ] `lifetime` reasonable (15–30 min)
- [ ] `domain = null` unless subdomains needed
- [ ] `EncryptCookies` in web group

### 8. Software & Data Integrity (A08)

**CSRF:**
- [ ] `VerifyCsrfToken` active in web group
- [ ] Only stateless routes excluded from CSRF
- [ ] `@csrf` on non-Inertia POST forms
- [ ] Excluded routes justified

**Deserialization:**
- [ ] No `unserialize`/`eval`/`extract` on user input

### 9. Logging & Monitoring (A09)

- [ ] Failed logins logged with IP + identifier
- [ ] Payment failures logged
- [ ] Logs contain no raw passwords / secrets
- [ ] Monitoring (Telescope, Sentry, etc.)

### 10. SSRF (A10)

- [ ] No `Http::get($request->input('url'))` without validation
- [ ] User URLs validated against allowlist / scheme check
- [ ] Internal network addresses blocked

---

## Additional Checks

### Command Injection & Dangerous Functions

- [ ] No `exec`/`shell_exec`/`system`/`passthru` on user input
- [ ] No open redirects (`redirect($request->input('url'))`)
- [ ] File uploads validate `mimes:`, `max:`; filenames never raw

### Security Headers

- [ ] `Content-Security-Policy` (with `Vite::useCspNonce()` where possible)
- [ ] `X-Frame-Options`
- [ ] `X-Content-Type-Options`
- [ ] `Strict-Transport-Security` (HTTPS)
- [ ] `Referrer-Policy`
- [ ] `Permissions-Policy`

---

## React + Inertia.js Checks

### R1. XSS in React

- [ ] No `dangerouslySetInnerHTML` without `DOMPurify.sanitize()`
- [ ] `href` / `src` validated (`http(s)://` only)
- [ ] No `eval`/`new Function`/`setTimeout(string)` on user strings

### R2. Inertia Data Exposure (Critical)

- [ ] `HandleInertiaRequests::share()` does not expose passwords, tokens, admin flags
- [ ] Controllers use `->only([...])` or API Resources — never raw `toArray()`
- [ ] All Inertia props treated as public (rendered into `data-page`)
- [ ] Payment keys / admin creds never passed as Inertia props
- [ ] Inertia v2 History Encryption enabled for sensitive pages

### R3. CSRF in Inertia

- [ ] `X-XSRF-TOKEN` header not disabled
- [ ] Custom `fetch` / `axios` includes CSRF token
- [ ] Only webhooks excluded from CSRF

### R4. Auth State in React

- [ ] `auth.user` excludes password hash, remember tokens, 2FA secrets
- [ ] Role checks enforced server-side
- [ ] `auth.user` contains only needed fields

### R5. Sensitive Data in Browser

- [ ] No API keys / secrets in React or TypeScript files
- [ ] No sensitive data in `localStorage`/`sessionStorage`
- [ ] `VITE_*` env vars contain no secrets

### R6. Dependency Security

- [ ] `npm audit` passes (no high/critical)
- [ ] React on a supported version
- [ ] Third-party libs reviewed for CVEs

---

## Report Format

```
## Laravel OWASP Security Audit Report

> React + Inertia.js detected — full Laravel + React/Inertia checks applied.

### 1. Broken Access Control (A01)
- **PASS** app/Http/Middleware/RoleMiddleware.php — role middleware applied
- **FAIL** app/Http/Controllers/PaymentController.php:42 — payment fetched without ownership check. Fix: scope query to authenticated user.

[continue for all OWASP + Additional + R1–R6]

---

## Summary

### Critical (fix immediately)
1. …

### Warnings (fix soon)
1. …

### Passed
X checks passed.

### Recommended
composer audit
npm audit
```

---

## Rule Files

Priority map:

| Priority | Category | Rule |
|----------|----------|------|
| 1 | Broken Access Control | [`sec-broken-access-control`](../rules/sec-broken-access-control.md) |
| 2 | Cryptographic Failures | [`sec-cryptographic-failures`](../rules/sec-cryptographic-failures.md) |
| 3 | Injection Prevention | [`sec-injection-prevention`](../rules/sec-injection-prevention.md) |
| 4 | XSS & React/Inertia | [`sec-xss-react-inertia`](../rules/sec-xss-react-inertia.md) |
| 5 | CSRF Protection | [`sec-csrf-protection`](../rules/sec-csrf-protection.md) |
| 6 | Security Misconfiguration | [`sec-security-misconfiguration`](../rules/sec-security-misconfiguration.md) |
| 7 | Auth & Rate Limiting | [`sec-authentication-rate-limiting`](../rules/sec-authentication-rate-limiting.md) |
| 8 | Inertia Data Exposure | [`sec-inertia-data-exposure`](../rules/sec-inertia-data-exposure.md) |
| — | Mass Assignment | [`sec-mass-assignment`](../rules/sec-mass-assignment.md) |
