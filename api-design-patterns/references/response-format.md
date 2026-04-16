# Response Format

**Impact:** MEDIUM · **Prefix:** `resp-` · **4 rules**

Consistent response shape and JSON conventions. Envelope format, casing, sparse fieldsets, and compression reduce payload size and surprise.

## Load When

- Picking an envelope shape for the whole API
- Settling on `camelCase` vs `snake_case`
- Optimising bandwidth for mobile or IoT clients
- Reviewing response consistency across endpoints

## Rules

| Rule | Summary |
|------|---------|
| [`resp-consistent-structure`](../rules/resp-consistent-structure.md) | Single envelope across all endpoints |
| [`resp-json-conventions`](../rules/resp-json-conventions.md) | `snake_case` vs `camelCase` — pick one and stick |
| [`resp-partial-responses`](../rules/resp-partial-responses.md) | `?fields=id,name,email` sparse fieldsets |
| [`resp-compression`](../rules/resp-compression.md) | gzip / Brotli with `Accept-Encoding` |

## Success Envelope

```json
{
  "data": { "id": 123, "name": "Alice" },
  "meta": { "request_id": "req_abc" }
}
```

## Collection Envelope

```json
{
  "data": [ { "id": 1 }, { "id": 2 } ],
  "meta":  { "current_page": 1, "per_page": 20, "total_count": 42 },
  "links": { "self": "/users?page=1", "next": "/users?page=2" }
}
```

## Error Envelope

See [`references/error-handling.md`](error-handling.md) — keep `data` and `error` mutually exclusive.

## Casing

- **`snake_case`** — common in Python, Rails, Laravel, Django REST Framework
- **`camelCase`** — common in JavaScript / TypeScript / iOS / Android ecosystems
- Pick one at launch; changing later is a breaking change

## Sparse Fieldsets

```
GET /users?fields=id,name,email
```
```json
{ "data": [ { "id": 1, "name": "Alice", "email": "a@x.com" } ] }
```

## Compression

```
# Client
GET /users HTTP/1.1
Accept-Encoding: br, gzip

# Server
HTTP/1.1 200 OK
Content-Encoding: br
Vary: Accept-Encoding
```

Rule of thumb: enable gzip/br for responses > 1 KiB — skip compressing pre-compressed payloads (images, video).
