# API Security

**Impact:** CRITICAL · **Prefix:** `sec-` · **7 rules**

API security fundamentals: authentication, authorization, rate limiting, input validation, CORS, HTTPS, and sensitive data protection.

## Load When

- Choosing an auth mechanism (OAuth2, JWT, API keys, sessions)
- Implementing RBAC or resource-level permission checks
- Configuring CORS for a browser-facing API
- Setting up rate limits / quotas
- Validating or sanitising request input
- Reviewing whether secrets / PII leak in responses or logs

## Rules

| Rule | Summary |
|------|---------|
| [`sec-authentication`](../rules/sec-authentication.md) | OAuth2 / JWT / API key patterns |
| [`sec-authorization`](../rules/sec-authorization.md) | RBAC, resource-level checks |
| [`sec-rate-limiting`](../rules/sec-rate-limiting.md) | Per-user / per-IP throttles |
| [`sec-input-validation`](../rules/sec-input-validation.md) | Schema + sanitisation at the edge |
| [`sec-cors-config`](../rules/sec-cors-config.md) | Whitelist origins, never `*` with creds |
| [`sec-https-only`](../rules/sec-https-only.md) | HSTS, redirect HTTP → HTTPS |
| [`sec-sensitive-data`](../rules/sec-sensitive-data.md) | Never return passwords, hashes, tokens |

## Rate-Limit Headers

```
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 998
X-RateLimit-Reset: 1640995200

HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

## Auth Quick Picks

| Use case | Recommended |
|----------|-------------|
| Third-party integrations | OAuth 2.0 (authorization code + PKCE) |
| First-party SPA / mobile | OAuth 2.0 + short-lived JWT access + refresh token |
| Server-to-server | OAuth 2.0 client credentials, or signed API key |
| Internal admin tools | Session cookies (HttpOnly, SameSite=Lax) |

## Do / Don't

- ✓ Enforce HTTPS everywhere; set HSTS with `max-age=31536000; includeSubDomains`
- ✓ Validate input against an explicit schema (JSON Schema / OpenAPI / Pydantic / Zod)
- ✓ Separate authentication (who you are) from authorization (what you can do)
- ✓ Use allowlists for CORS `Access-Control-Allow-Origin` when `credentials: true`
- ✗ Don't log request bodies that may contain passwords, tokens, or PII
- ✗ Don't put secrets in URL query params — they end up in server + proxy logs
- ✗ Don't rely on "obscure endpoint" as a security boundary
