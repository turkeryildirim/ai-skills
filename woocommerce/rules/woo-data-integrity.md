---
title: WooCommerce Data Integrity
impact: CRITICAL
impactDescription: Race conditions and unverified mutations cause data corruption in orders and inventory
tags: woocommerce, data-integrity, crud, race-conditions
---

## WooCommerce Data Integrity

**Impact: CRITICAL (concurrent order processing can corrupt inventory and payment data)**

Always verify entity state and ownership before mutations. Handle race conditions in concurrent operations. Use WooCommerce CRUD objects, never direct database queries for entity updates.

## Bad Example

```php
global $wpdb;
$wpdb->update( $wpdb->prefix . 'woocommerce_order_items', [
    'order_item_name' => $new_name,
], [ 'order_item_id' => $item_id ] );

$stock = get_post_meta( $product_id, '_stock', true );
update_post_meta( $product_id, '_stock', $stock - $qty );
```

## Good Example

```php
$order = wc_get_order( $order_id );
if ( ! $order || ! $order->get_id() ) {
    return false;
}

foreach ( $order->get_items() as $item_id => $item ) {
    $product = $item->get_product();
    if ( ! $product || ! $product->managing_stock() ) {
        continue;
    }

    $qty = $item->get_quantity();
    wc_update_product_stock( $product, $qty, 'decrease' );
}

$order->set_status( 'completed' );
$order->save();
```

## Why

- **Use WC CRUD objects** — `wc_get_order()`, `wc_get_product()`, `$order->save()` — handles caches, hooks, validation
- **Never direct DB updates** — bypasses WooCommerce's data layer, invalidates caches, skips hooks
- **`wc_update_product_stock()`** — atomic stock operations with race condition handling
- **Verify before mutate** — check entity exists, check ownership, check state before changes
- **`$order->save()` once** — batch all changes, save once to trigger hooks efficiently
- **Check `managing_stock()`** — not all products manage stock; always check before stock operations
- **Idempotent operations** — order processing may retry; ensure operations are safe to repeat

Reference: [WooCommerce CRUD](https://developer.woocommerce.com/docs/woocommerce-crud-objects/)
