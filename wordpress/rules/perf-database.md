---
title: Database Optimization
impact: HIGH
impactDescription: N+1 queries and autoload bloat are the most common performance killers
tags: performance, database, queries, n+1, autoload
---

## Database Optimization

**Impact: HIGH (N+1 queries and autoload bloat are the #1 performance killers)**

Avoid N+1 patterns by batching queries and priming caches. Use `fields => 'ids'` when only IDs are needed. Manage autoloaded options. Index expensive meta queries.

## Bad Example

```php
// N+1 query pattern
$posts = get_posts( [ 'post_type' => 'product', 'numberposts' => 50 ] );
foreach ( $posts as $post ) {
    $price = get_post_meta( $post->ID, 'price', true );       // 50 separate queries
    $stock = get_post_meta( $post->ID, 'stock', true );       // 50 more
    $image = get_the_post_thumbnail_url( $post->ID );         // 50 more
}
```

## Good Example

```php
$ids = get_posts( [
    'post_type'   => 'product',
    'numberposts' => 50,
    'fields'      => 'ids',
] );

update_meta_cache( 'post', $ids );
update_object_term_cache( $ids, 'product' );

foreach ( $ids as $id ) {
    $price = get_post_meta( $id, 'price', true );    // cached
    $stock = get_post_meta( $id, 'stock', true );    // cached
}
```

## Why

- **`fields => 'ids'`** — avoids loading full post objects when only IDs are needed
- **`update_meta_cache()`** — primes meta cache for all IDs in one query, preventing N+1
- **`update_object_term_cache()`** — primes term cache similarly
- **Autoloaded options audit** — `wp doctor check autoload-options` identifies bloat
- **Use `$wpdb->queries` or Query Monitor** — identify slow queries and N+1 patterns
- **Index expensive meta queries** — `wp_postmeta` queries benefit from composite indexes on `meta_key, meta_value`

Reference: [WP Database Optimization](https://developer.wordpress.org/apis/database/)
