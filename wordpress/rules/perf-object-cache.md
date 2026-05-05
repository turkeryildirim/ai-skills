---
title: Object Cache
impact: HIGH
impactDescription: Persistent object cache reduces database load by 80%+ on high-traffic sites
tags: performance, object-cache, redis, memcached
---

## Object Cache

**Impact: HIGH (persistent object cache eliminates repeated database queries across requests)**

Default WordPress object cache is per-request only. Persistent cache requires a drop-in (`wp-content/object-cache.php`) backed by Redis or Memcached. Use explicit invalidation and set expirations.

## Bad Example

```php
function my_get_option_cache() {
    static $cache = [];
    if ( isset( $cache['my_data'] ) ) {
        return $cache['my_data'];
    }
    $cache['my_data'] = get_option( 'my_data' );
    return $cache['my_data'];
}
```

## Good Example

```php
function my_get_settings() {
    $settings = wp_cache_get( 'my_settings', 'my_plugin' );
    if ( false === $settings ) {
        $settings = get_option( 'my_plugin_settings', [] );
        wp_cache_set( 'my_settings', $settings, 'my_plugin', HOUR_IN_SECONDS );
    }
    return $settings;
}

function my_update_settings( $settings ) {
    update_option( 'my_plugin_settings', $settings );
    wp_cache_set( 'my_settings', $settings, 'my_plugin', HOUR_IN_SECONDS );
}
```

## Why

- **Default cache is per-request** — no persistence between requests without a drop-in
- **Persistent cache via drop-in** — Redis or Memcached backed `object-cache.php`
- **Always check `false ===`** — `wp_cache_get()` returns `false` on miss, not `null`
- **Set expirations** — prevents stale data from accumulating indefinitely
- **Invalidate on writes** — update or delete cache when source data changes
- **Use cache groups** — namespace entries (`'my_plugin'`) for targeted invalidation
- **`wp cache flush`** is nuclear — impacts all sites in multisite, causes load spikes

Reference: [Object Cache](https://developer.wordpress.org/reference/classes/wp_object_cache/) | [Redis Object Cache](https://wordpress.org/plugins/redis-cache/)
