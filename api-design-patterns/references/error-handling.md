# Error Handling

**Impact:** CRITICAL · **Prefix:** `error-` · **6 rules**

Consistent error response format across every endpoint. Machine-readable codes, field-level validation details, meaningful messages, request IDs for debugging, and never leaking stack traces enable clients to handle errors programmatically.

## Load When

- Designing an error envelope or error taxonomy
- Wiring up validation error responses
- Setting up global exception handling
- Debugging a production incident (request ID tracing)
- Reviewing whether clients can distinguish error types

## Rules

| Rule | Summary |
|------|---------|
| [`error-consistent-format`](../rules/error-consistent-format.md) | Same envelope on every endpoint |
| [`error-meaningful-messages`](../rules/error-meaningful-messages.md) | Helpful, actionable human text |
| [`error-validation-details`](../rules/error-validation-details.md) | Field-level `details[]` array |
| [`error-error-codes`](../rules/error-error-codes.md) | Stable machine-readable codes |
| [`error-no-stack-traces`](../rules/error-no-stack-traces.md) | Never expose traces in production |
| [`error-request-id`](../rules/error-request-id.md) | `X-Request-Id` header + body for tracing |

## Canonical Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid data.",
    "details": [
      {
        "field": "email",
        "code": "INVALID_FORMAT",
        "message": "Please provide a valid email address."
      },
      {
        "field": "age",
        "code": "OUT_OF_RANGE",
        "message": "Age must be between 0 and 150."
      }
    ],
    "request_id": "req_abc123",
    "documentation_url": "https://api.example.com/docs/errors#VALIDATION_ERROR"
  }
}
```

## Error Code Taxonomy

Use `SCREAMING_SNAKE_CASE`, namespaced by domain when helpful:

- Auth: `UNAUTHENTICATED`, `TOKEN_EXPIRED`, `FORBIDDEN`
- Validation: `VALIDATION_ERROR`, `INVALID_FORMAT`, `OUT_OF_RANGE`, `REQUIRED_FIELD`
- Resource: `NOT_FOUND`, `ALREADY_EXISTS`, `CONFLICT`
- Rate / quota: `RATE_LIMITED`, `QUOTA_EXCEEDED`
- Server: `INTERNAL_ERROR`, `UPSTREAM_UNAVAILABLE`

## Do / Don't

- ✓ Include `request_id` in every response (success and error) — via header and body
- ✓ Log the full stack trace server-side; surface only `code` + `message` to the client
- ✓ Map each code to an HTTP status; don't use 200 with `{"error": ...}`
- ✗ Don't expose DB error strings, file paths, or internal class names
- ✗ Don't return different shapes from different endpoints
