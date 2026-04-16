# Resource Design

**Impact:** CRITICAL · **Prefix:** `rest-` · **8 rules**

Foundational REST principles for endpoint design. Proper resource naming with nouns, plural collections, correct HTTP method semantics, appropriate status codes, idempotency, and HATEOAS links make APIs intuitive and predictable.

## Load When

- Designing new endpoints or an entire new API surface
- Renaming or refactoring existing routes
- Deciding which HTTP method / status code to use
- Modelling hierarchical (nested) resources
- Adding non-CRUD operations (publish, approve, cancel, …)
- Implementing retry-safe write endpoints

## Rules

| Rule | Summary |
|------|---------|
| [`rest-nouns-not-verbs`](../rules/rest-nouns-not-verbs.md) | Endpoints are nouns; HTTP methods are the verbs |
| [`rest-plural-resources`](../rules/rest-plural-resources.md) | Collections are plural: `/users`, not `/user` |
| [`rest-http-methods`](../rules/rest-http-methods.md) | GET / POST / PUT / PATCH / DELETE semantics |
| [`rest-nested-resources`](../rules/rest-nested-resources.md) | Max 2 levels of nesting; break out at 3+ |
| [`rest-status-codes`](../rules/rest-status-codes.md) | 2xx success, 4xx client error, 5xx server error |
| [`rest-idempotency`](../rules/rest-idempotency.md) | `Idempotency-Key` header for safe retries |
| [`rest-hateoas`](../rules/rest-hateoas.md) | Hypermedia links for discoverability (HAL) |
| [`rest-resource-actions`](../rules/rest-resource-actions.md) | Non-CRUD as sub-resources: `POST /orders/123/cancel` |

## Quick Patterns

```
GET    /users          # List
POST   /users          # Create
GET    /users/123      # Read
PUT    /users/123      # Replace (full)
PATCH  /users/123      # Update (partial)
DELETE /users/123      # Delete

POST   /orders/123/cancel          # Non-CRUD action
GET    /users/123/posts            # Nested (1 level)
GET    /users/123/posts/456/comments  # Nested (2 levels — max)
```

## HTTP Method Semantics

| Method | Safe | Idempotent | Use for |
|--------|:----:|:----------:|---------|
| GET | ✓ | ✓ | Read |
| POST | ✗ | ✗ | Create, actions |
| PUT | ✗ | ✓ | Full replacement |
| PATCH | ✗ | ✗ | Partial update |
| DELETE | ✗ | ✓ | Remove |

## Common Status Codes

| Code | Meaning | Typical use |
|-----:|---------|------|
| 200 | OK | Successful GET / PUT / PATCH |
| 201 | Created | Successful POST |
| 202 | Accepted | Async work queued |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Malformed request |
| 401 | Unauthorized | Missing / invalid auth |
| 403 | Forbidden | Authenticated but not allowed |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | State conflict (duplicate, version) |
| 422 | Unprocessable | Semantic validation failed |
| 429 | Too Many Requests | Rate limited |
| 500 | Server Error | Unhandled exception |
| 503 | Service Unavailable | Upstream / maintenance |
