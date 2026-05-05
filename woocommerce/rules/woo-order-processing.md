---
title: WooCommerce Order Processing
impact: CRITICAL
impactDescription: Order processing errors cause payment disputes and customer dissatisfaction
tags: woocommerce, order, status, refund, fulfillment
---

## WooCommerce Order Processing

**Impact: CRITICAL (order processing is the most sensitive WooCommerce domain)**

Use `wc_get_order()` and CRUD methods. Status transitions trigger variable hooks. Always verify order exists before operations. Use `$order->save()` once after all mutations.

## Bad Example

```php
global $wpdb;
$wpdb->update( $wpdb->posts, [ 'post_status' => 'wc-completed' ], [ 'ID' => $order_id ] );
```

## Good Example

```php
$order = wc_get_order( $order_id );
if ( ! $order ) {
    return new \WP_Error( 'invalid_order', 'Order not found' );
}

// Status transitions trigger hooks:
// woocommerce_order_status_pending_to_processing
// woocommerce_order_status_processing
// woocommerce_order_status_changed
$order->update_status( 'processing', 'Payment received via gateway.' );

// Add note
$order->add_order_note( 'Custom processing note.' );

// Line items
foreach ( $order->get_items() as $item_id => $item ) {
    $product   = $item->get_product();
    $qty       = $item->get_quantity();
    $subtotal  = $item->get_subtotal();
}

// Refund
wc_create_refund( [
    'amount'   => $refund_amount,
    'reason'   => 'Customer request',
    'order_id' => $order->get_id(),
] );

// Save once
$order->save();
```

## Why

- **`update_status()`** — triggers all transition hooks properly (`woocommerce_order_status_{from}_to_{to}`)
- **Never direct DB updates** — bypasses hooks, caches, email notifications, and inventory adjustments
- **`wc_create_refund()`** — handles stock restoration, totals recalculation, and refund hooks
- **`$order->save()` once** — batch mutations, save once to avoid multiple hook firings
- **Verify order exists** — `wc_get_order()` returns `false` if not found
- **Status transition hooks are variable** — `woocommerce_order_status_completed`, `woocommerce_order_status_pending_to_processing`
- **Payment complete** — `$order->payment_complete( $transaction_id )` triggers `woocommerce_payment_complete`

Reference: [WC_Order](https://woocommerce.github.io/code-reference/classes/WC-Order.html) | [Order Hooks](https://woocommerce.github.io/code-reference/hooks/hooks.html)
