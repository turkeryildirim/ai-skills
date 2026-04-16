---
name: api-design-patterns
description: RESTful API design, error handling, versioning, security, pagination, response format, and documentation. Use when designing new APIs, reviewing endpoints, implementing error responses, choosing pagination / versioning strategies, or setting up API security and docs. Triggers on "design API", "review API", "REST best practices", "API patterns".
license: MIT
metadata:
  author: agent-skills
  version: "3.0.0"
  ruleCount: 38
  categoryCount: 7
---

# API Design Patterns

RESTful API design principles for consistent, developer-friendly APIs. 38 rules across 7 categories, each rule with bad / good examples in `rules/`. Per-category guides live in `references/`.

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

# Rate limit ← sec-rate-limiting
X-RateLimit-Limit: 1000 / X-RateLimit-Remaining: 998 / X-RateLimit-Reset: 1640995200
```

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

Load only the reference(s) relevant to the current task — don't pull all seven.

## Rule Index — Direct Jumps

Each `rules/<name>.md` file has YAML frontmatter (title, impact, tags) and a bad/good example pair.

### Resource Design (`rest-`) — CRITICAL
`rest-nouns-not-verbs` · `rest-plural-resources` · `rest-http-methods` · `rest-nested-resources` · `rest-status-codes` · `rest-idempotency` · `rest-hateoas` · `rest-resource-actions`

### Error Handling (`error-`) — CRITICAL
`error-consistent-format` · `error-meaningful-messages` · `error-validation-details` · `error-error-codes` · `error-no-stack-traces` · `error-request-id`

### Security (`sec-`) — CRITICAL
`sec-authentication` · `sec-authorization` · `sec-rate-limiting` · `sec-input-validation` · `sec-cors-config` · `sec-https-only` · `sec-sensitive-data`

### Pagination & Filtering (`page-` / `filter-` / `sort-`) — HIGH
`page-cursor-based` · `page-offset-based` · `page-consistent-params` · `page-metadata` · `filter-query-params` · `sort-flexible`

### Versioning (`ver-`) — HIGH
`ver-url-path` · `ver-header-based` · `ver-backward-compatible` · `ver-deprecation`

### Response Format (`resp-`) — MEDIUM
`resp-consistent-structure` · `resp-json-conventions` · `resp-partial-responses` · `resp-compression`

### Documentation (`doc-`) — MEDIUM
`doc-openapi` · `doc-examples` · `doc-changelog`

## How to Read a Rule File

Each `rules/<name>.md`:
- **Frontmatter** — `title`, `impact`, `impactDescription`, `tags`
- **Why it matters** — short rationale
- **Incorrect** — bad example with the problem called out
- **Correct** — good example with the benefit explained
- **Context** — language-specific notes and spec references

## External References

- [RESTful API Guidelines](https://restfulapi.net)
- [Zalando RESTful API Guidelines](https://zalando.github.io/restful-api-guidelines)
- [Microsoft API Guidelines](https://github.com/microsoft/api-guidelines)
- [Google API Design Guide](https://cloud.google.com/apis/design)
- [OpenAPI Specification](https://swagger.io/specification)
