---
name: api-design-patterns
description: RESTful API design, error handling, versioning, security, pagination, response format, and documentation. Use when designing new APIs, reviewing endpoints, implementing error responses, choosing pagination / versioning strategies, or setting up API security and docs. Triggers on "design API", "review API", "REST best practices", "API patterns".
model: inherit
---

# API Design Patterns

RESTful API design principles for consistent, developer-friendly APIs. 38 rules across 7 categories, each rule with bad / good examples in `rules/`. Per-category guides live in `references/`.

## Specialized Agents

Specialized personas for different API design roles. Load these from `agents/` to provide expert context.

| Agent | Role | Focus |
|-------|------|-------|
| **api-design-pro** | API Architect | Resource design, REST/GraphQL/gRPC patterns, versioning, security. |

## When to Use

- Designing a new API or endpoint
- Reviewing existing endpoint structure
- Implementing error handling and validation
- Choosing pagination, filtering, or sorting strategies
- Planning API versioning and deprecation
- Configuring API security (auth, CORS, rate limiting)
- Writing or generating OpenAPI docs

## Basic Coverage

```
GET    /users          # list       ← rest-http-methods
POST   /users          # create     ← rest-nouns-not-verbs
GET    /users/123      # read       ← rest-plural-resources
PUT    /users/123      # replace    ← rest-status-codes
PATCH  /users/123      # update
DELETE /users/123      # delete     → 204 No Content

# Error envelope (every endpoint, same shape) ← error-consistent-format
{ "error": { "code": "VALIDATION_ERROR", "message": "...", "details": [...], "request_id": "req_..." } }

# List envelope ← resp-consistent-structure + page-metadata
{ "data": [...], "meta": { "current_page": 1, "per_page": 20, "total_count": 42 }, "links": {...} }

# Auth ← sec-authentication + sec-https-only
Authorization: Bearer <jwt>
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## Core Directives

### MUST DO

- Use plural nouns for resources (e.g., `/users`, not `/user`)
- Follow standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Implement consistent error envelopes with structured error codes and `request_id`
- Use cursor-based pagination for large, dynamic datasets
- Version APIs via URL path (e.g., `/v1/`) or headers
- Always use HTTPS and implement proper rate limiting
- Provide machine-readable documentation (OpenAPI/Swagger)

### MUST NOT DO

- Use verbs in URI paths (e.g., `/getUser`, `/createOrder`)
- Return 200 OK for errors or 404 for empty lists (return 200 with empty array)
- Expose internal stack traces in error responses
- Perform destructive operations via GET requests
- Use sequential IDs in public URLs (prefer UUIDs/ULIDs)
- Store sensitive data (keys, tokens) in plain text or log them

## Category Index — When to Load Which Reference

| # | Category | Impact | Load when… | Reference | Prefix | Rules |
|--:|----------|:------:|------------|-----------|--------|:-----:|
| 1 | Resource Design | CRITICAL | Designing / renaming endpoints, choosing HTTP methods & status codes | [`references/resource-design.md`](references/resource-design.md) | `rest-` | 8 |
| 2 | Error Handling | CRITICAL | Wiring error envelope, validation details, request-id tracing | [`references/error-handling.md`](references/error-handling.md) | `error-` | 6 |
| 3 | Security | CRITICAL | Auth, RBAC, CORS, rate limits, input validation, HTTPS, secret hygiene | [`references/security.md`](references/security.md) | `sec-` | 7 |
| 4 | Pagination & Filtering | HIGH | Adding a list endpoint, filtering, sorting, cursor vs offset | [`references/pagination-filtering.md`](references/pagination-filtering.md) | `page-`, `filter-`, `sort-` | 6 |
| 5 | Versioning | HIGH | Launching v1, breaking changes, sunset windows | [`references/versioning.md`](references/versioning.md) | `ver-` | 4 |
| 6 | Response Format | MEDIUM | Picking envelope, casing, sparse fields, compression | [`references/response-format.md`](references/response-format.md) | `resp-` | 4 |
| 7 | Documentation | MEDIUM | OpenAPI spec, examples, changelog | [`references/documentation.md`](references/documentation.md) | `doc-` | 3 |

## Rule Index — Direct Jumps

### 1. Resource Design (`rest-`) — CRITICAL
`rest-nouns-not-verbs` · `rest-plural-resources` · `rest-http-methods` · `rest-nested-resources` · `rest-status-codes` · `rest-idempotency` · `rest-hateoas` · `rest-resource-actions`

### 2. Error Handling (`error-`) — CRITICAL
`error-consistent-format` · `error-meaningful-messages` · `error-validation-details` · `error-error-codes` · `error-no-stack-traces` · `error-request-id`

### 3. Security (`sec-`) — CRITICAL
`sec-authentication` · `sec-authorization` · `sec-rate-limiting` · `sec-input-validation` · `sec-cors-config` · `sec-https-only` · `sec-sensitive-data`

### 4. Pagination & Filtering (`page-` / `filter-` / `sort-`) — HIGH
`page-cursor-based` · `page-offset-based` · `page-consistent-params` · `page-metadata` · `filter-query-params` · `sort-flexible`

### 5. Versioning (`ver-`) — HIGH
`ver-url-path` · `ver-header-based` · `ver-backward-compatible` · `ver-deprecation`

### 6. Response Format (`resp-`) — MEDIUM
`resp-consistent-structure` · `resp-json-conventions` · `resp-partial-responses` · `resp-compression`

### 7. Documentation (`doc-`) — MEDIUM
`doc-openapi` · `doc-examples` · `doc-changelog`

## Validation Checklist

- [ ] All resource paths use plural nouns and no verbs
- [ ] Correct HTTP methods are used for all actions (e.g., DELETE for removal)
- [ ] Error responses follow the standard envelope with a `request_id`
- [ ] Authentication is required for all non-public endpoints
- [ ] Rate limiting is configured and headers are present
- [ ] Pagination is implemented for all list endpoints
- [ ] API is versioned (URL or Header)
- [ ] OpenAPI specification is up to date and reflects all changes

## External References

- [RESTful API Guidelines](https://restfulapi.net)
- [Zalando RESTful API Guidelines](https://zalando.github.io/restful-api-guidelines)
- [Microsoft API Guidelines](https://github.com/microsoft/api-guidelines)
- [Google API Design Guide](https://cloud.google.com/apis/design)
- [OpenAPI Specification](https://swagger.io/specification)
