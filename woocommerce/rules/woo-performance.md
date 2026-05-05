---
title: WooCommerce Performance Optimization
impact: HIGH
impactDescription: Cache priming reduces query count by 80%+ on product listing pages
tags: woocommerce, performance, cache-priming, query-optimization
---

## WooCommerce Performance Optimization

**Impact: HIGH (WooCommerce pages are query-heavy; cache priming eliminates N+1 patterns)**

Use `_prime_post_caches()` before iterating products/orders. Use `wp_prime_option_caches()` for batched option reads. Prime product images separately. Don't re-prime already cached data.

## Bad Example

```php
$products = wc_get_products( [ 'limit' => 50 ] );
foreach ( $products as $product ) {
    $price    = $product->get_price();           // cached
    $image    = $product->get_image();            // separate query per product
    $category = $product->get_category();         // separate query per product
    $reviews  = $product->get_rating_count();     // separate query per product
}
```

## Good Example

```php
$products = wc_get_products( [ 'limit' => 50 ] );

// Prime post caches (products are post-based)
_prime_post_caches( array_map( fn( $p ) => $p->get_id(), $products ) );

// Prime product image caches separately
_prime_post_caches( array_filter(
    array_map( fn( $p ) => (int) $p->get_image_id(), $products )
) );

foreach ( $products as $product ) {
    $price    = $product->get_price();      // cached
    $image    = $product->get_image();       // cached
    $category = $product->get_category();    // cached
}

// Options cache priming for WooCommerce settings
wp_prime_option_caches( [
    'woocommerce_shop_page_display',
    'woocommerce_category_archive_display',
    'woocommerce_default_catalog_orderby',
] );
```

## Why

- **`_prime_post_caches($ids)`** — primes post, meta, and term caches in bulk queries
- **Two-phase image priming** — prime posts first, then prime image IDs from those posts
- **Don't prime after `WP_Query`** — it already primes post/meta/term caches
- **Don't prime from order line items** — `prime_caches_for_orders()` handles this
- **`wp_prime_option_caches()`** — batch option reads into one query
- **WooCommerce settings are autoloaded** — most don't need priming (check `autoload` column)
- **`update_meta_cache('post', $ids)`** — primes only meta cache if needed separately

Reference: [WooCommerce Performance Skill](https://github.com/woocommerce/woocommerce/tree/trunk/.ai/skills/woocommerce-performance)
