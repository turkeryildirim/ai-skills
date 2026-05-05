---
title: Caching Strategies
impact: HIGH
impactDescription: Proper caching dramatically reduces database load and TTFB
tags: performance, caching, transients, object-cache, page-cache
---

## Caching Strategies

**Impact: HIGH (caching is the most impactful performance optimization)**

Use Transients API for time-limited cached data. Use object cache for repeated reads with explicit invalidation. Avoid unbounded caches — set expirations or implement invalidation hooks.

## Bad Example

```php
function my_expensive_query() {
    global $wpdb;
    return $wpdb->get_results( "SELECT * FROM {$wpdb->posts} WHERE post_type = 'product'" );
}

// No cache at all — queries DB on every request
$products = my_expensive_query();

// Unbounded cache — never expires, grows stale
set_transient( 'all_products', $products );
```

## Good Example

```php
function my_get_products() {
    $cache_key = 'my_products_' . md5( serialize( $args ) );
    $products = wp_cache_get( $cache_key, 'my_plugin' );

    if ( false === $products ) {
        $products = my_expensive_query();
        wp_cache_set( $cache_key, $products, 'my_plugin', HOUR_IN_SECONDS );
    }

    return $products;
}

// Invalidate on product changes
add_action( 'save_post_product', function( $post_id ) {
    wp_cache_delete( 'my_products_' . md5( serialize( [] ) ), 'my_plugin' );
} );
```

## Why

- **`wp_cache_get/set`** — uses object cache when available (Redis/Memcached), falls back to in-request memory
- **Explicit invalidation** — delete cache when source data changes
- **Set expirations** — prevents stale data if invalidation is missed
- **Transients for time-limited data** — `set_transient( $key, $value, HOUR_IN_SECONDS )`
- **`wp cache flush`** impacts all sites in multisite — use group-based deletion instead
- **Cache groups** — namespace related cache entries for targeted invalidation

Reference: [Object Cache](https://developer.wordpress.org/reference/classes/wp_object_cache/) | [Transients API](https://developer.wordpress.org/plugins/settings/transients-api/)
