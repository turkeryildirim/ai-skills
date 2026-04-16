# Documentation

**Impact:** MEDIUM · **Prefix:** `doc-` · **3 rules**

How consumers discover and track changes to your API. OpenAPI (Swagger), examples, and a changelog.

## Load When

- Publishing a new API
- Adding a significant new endpoint or feature
- Shipping a breaking change (must land in the changelog)
- Onboarding new consumers / partners

## Rules

| Rule | Summary |
|------|---------|
| [`doc-openapi`](../rules/doc-openapi.md) | Machine-readable OpenAPI 3.1 spec as the source of truth |
| [`doc-examples`](../rules/doc-examples.md) | Realistic request + response examples for every endpoint |
| [`doc-changelog`](../rules/doc-changelog.md) | Dated changelog, linked from docs and release notes |

## OpenAPI Skeleton

```yaml
openapi: 3.1.0
info:
  title: Example API
  version: 1.4.0
  description: …
servers:
  - url: https://api.example.com/v1
paths:
  /users:
    get:
      summary: List users
      parameters:
        - $ref: '#/components/parameters/Page'
        - $ref: '#/components/parameters/PerPage'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema: { $ref: '#/components/schemas/UserList' }
              examples:
                default: { $ref: '#/components/examples/UserListExample' }
components:
  schemas: { ... }
  parameters: { ... }
  examples: { ... }
  securitySchemes:
    bearerAuth: { type: http, scheme: bearer, bearerFormat: JWT }
security:
  - bearerAuth: []
```

## Example Shape

```yaml
examples:
  UserListExample:
    summary: Typical list response
    value:
      data:
        - { id: 1, name: "Alice", email: "alice@example.com" }
        - { id: 2, name: "Bob",   email: "bob@example.com"   }
      meta:  { current_page: 1, per_page: 20, total_count: 2 }
      links: { self: /users?page=1, next: null }
```

## Changelog Entry Template

```md
## [1.4.0] — 2026-03-14

### Added
- `GET /reports` — new reporting endpoint.
- `fields` query parameter on `/users` (sparse fieldsets).

### Changed
- `POST /orders` now returns `201 Created` with a `Location` header (previously `200`).

### Deprecated
- `GET /customers/legacy` — use `GET /customers` instead. Sunset: 2026-12-31.

### Removed
- `GET /v0/...` — removed after 2026-01-01 sunset window.

### Fixed
- `meta.total_count` was off-by-one when filters were active.

### Security
- Tightened `Idempotency-Key` parser; see advisory GHSA-xxxx.
```

## Do / Don't

- ✓ Generate SDKs / client libs from the OpenAPI spec — don't hand-maintain both
- ✓ Validate the spec in CI (`redocly lint`, `spectral lint`)
- ✓ Keep examples in sync with the schema (lint will catch drift)
- ✗ Don't let the docs site and the spec diverge — docs are generated, not authored
