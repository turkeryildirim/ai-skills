# Pagination, Filtering & Sorting

**Impact:** HIGH · **Prefixes:** `page-`, `filter-`, `sort-` · **6 rules**

Efficient navigation of collections. Cursor pagination for large or live datasets, offset pagination for simple cases, consistent parameter names, response metadata, query-param filters, and a flexible sort syntax.

## Load When

- Adding a list endpoint for a collection
- The table behind an endpoint grows unboundedly
- Clients need to filter / search / sort over a list
- Infinite-scroll or "load more" UI
- Migrating from offset → cursor pagination for scale

## Rules

| Rule | Summary |
|------|---------|
| [`page-cursor-based`](../rules/page-cursor-based.md) | Cursor pagination (default for scale) |
| [`page-offset-based`](../rules/page-offset-based.md) | Offset pagination (simple / small) |
| [`page-consistent-params`](../rules/page-consistent-params.md) | Standard param names across endpoints |
| [`page-metadata`](../rules/page-metadata.md) | `meta` + `links` in every list response |
| [`filter-query-params`](../rules/filter-query-params.md) | Filter via `?status=active&role=admin` |
| [`sort-flexible`](../rules/sort-flexible.md) | `?sort=-created_at,name` (`-` = descending) |

## Offset Pagination

```
GET /users?page=2&per_page=20
```
```json
{
  "data": [ ... ],
  "meta":  { "current_page": 2, "per_page": 20, "total_pages": 10, "total_count": 195 },
  "links": {
    "first": "/users?page=1&per_page=20",
    "prev":  "/users?page=1&per_page=20",
    "next":  "/users?page=3&per_page=20",
    "last":  "/users?page=10&per_page=20"
  }
}
```

## Cursor Pagination

```
GET /users?cursor=eyJpZCI6MTIzfQ&limit=20
```
```json
{
  "data": [ ... ],
  "meta": { "limit": 20, "has_more": true },
  "links": { "next": "/users?cursor=eyJpZCI6MTQzfQ&limit=20" }
}
```

## Filtering & Sorting

```
GET /users?status=active&role=admin&created_after=2026-01-01
GET /users?sort=-created_at,name          # desc by created_at, asc by name
GET /users?fields=id,name,email           # sparse fieldset
```

## Choose Cursor When

- Table is > ~10 000 rows
- New rows are inserted frequently (offsets drift)
- Client does infinite scroll / real-time feed
- Deep pages are common (`page=500` is O(N) without an index trick)

## Choose Offset When

- Small, bounded table
- User needs random access ("jump to page 7")
- Admin UIs with page numbers
