# Versioning

**Impact:** HIGH · **Prefix:** `ver-` · **4 rules**

Evolve an API without breaking existing consumers. Choose a versioning scheme, document backward-compatibility rules, and plan deprecation with `Sunset` headers.

## Load When

- Launching v1 and deciding where the version number goes
- Introducing a breaking change
- Planning a deprecation / sunset window
- Reviewing whether a change is actually breaking

## Rules

| Rule | Summary |
|------|---------|
| [`ver-url-path`](../rules/ver-url-path.md) | `/api/v1/users` — simple, cache-friendly, discoverable |
| [`ver-header-based`](../rules/ver-header-based.md) | `Accept: application/vnd.example.v2+json` |
| [`ver-backward-compatible`](../rules/ver-backward-compatible.md) | Additive changes never bump version |
| [`ver-deprecation`](../rules/ver-deprecation.md) | `Deprecation` + `Sunset` + `Link` headers |

## Breaking vs Non-Breaking

**Non-breaking (no version bump):**
- Adding a new endpoint
- Adding a new optional field to a request
- Adding a new field to a response
- Adding a new optional query parameter
- Accepting a new enum value on input

**Breaking (new version required):**
- Removing or renaming a field / endpoint / parameter
- Changing a field's type (string → object)
- Tightening validation
- Changing response status codes or error shape
- Removing an enum value the server returns

## Deprecation Headers

```
HTTP/1.1 200 OK
Deprecation: Sat, 31 Dec 2026 23:59:59 GMT
Sunset:      Sat, 30 Jun 2027 23:59:59 GMT
Link:        <https://api.example.com/v2/users>; rel="successor-version"
Warning:     299 - "This endpoint is deprecated. Migrate to /v2/users before 2027-06-30."
```

## URL-Path vs Header

| | URL path (`/v1/`) | Accept header |
|--|---|---|
| Discoverability | ✓ visible in every request | ✗ hidden |
| Browser-friendly | ✓ works in curl / URL bar | ✗ needs client support |
| Caching | ✓ different URLs = different cache entries | △ requires `Vary: Accept` |
| Clean | △ "REST purist" complaint | ✓ same URI forever |
| **Recommendation** | **Default** for public APIs | Internal / hypermedia APIs |

## Lifecycle

1. **Launch v1** with path versioning
2. **Additive changes** ship in place — no new version
3. When a breaking change is unavoidable → **ship v2 alongside v1**
4. **Announce deprecation** with headers and changelog
5. **Sunset window** ≥ 6 months (longer for widely-adopted APIs)
6. **Remove v1** after the sunset date
