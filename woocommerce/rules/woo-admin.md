---
title: WooCommerce Admin Customization
impact: MEDIUM
impactDescription: Admin customizations improve store management efficiency
tags: woocommerce, admin, list-table, settings, meta-boxes
---

## WooCommerce Admin Customization

**Impact: MEDIUM (admin customizations affect store management workflows)**

Use `manage_{$screen->id}_columns` for list table columns. `woocommerce_get_settings_{$id}` for settings pages. `add_meta_boxes_{$screen_id}` for order/product meta boxes.

## Bad Example

```php
add_filter( 'manage_edit-shop_order_columns', function( $columns ) {
    $columns['my_col'] = 'My Column';
    return $columns;
} );
```

## Good Example

```php
// Add custom column to orders list table
add_filter( 'manage_woocommerce_page_wc-orders_columns', function( $columns ) {
    $columns['shipping_method'] = __( 'Shipping Method', 'my-plugin' );
    return $columns;
} );

add_action( 'manage_woocommerce_page_wc-orders_custom_column', function( $column, $order_id ) {
    if ( 'shipping_method' === $column ) {
        $order = wc_get_order( $order_id );
        if ( $order ) {
            $items = $order->get_items( 'shipping' );
            foreach ( $items as $item ) {
                echo esc_html( $item->get_method_title() );
            }
        }
    }
}, 10, 2 );

// Add meta box to order edit screen
add_action( 'add_meta_boxes_woocommerce_page_wc-orders', function() {
    add_meta_box( 'my-order-meta', 'Custom Info', 'my_render_order_meta', null, 'side' );
} );

// Custom settings tab
add_filter( 'woocommerce_settings_tabs_array', function( $tabs ) {
    $tabs['my_settings'] = 'My Settings';
    return $tabs;
} );

add_action( 'woocommerce_settings_tabs_my_settings', function() {
    woocommerce_admin_fields( my_get_settings() );
} );

add_action( 'woocommerce_update_options_settings_my_settings', function() {
    woocommerce_update_options( my_get_settings() );
} );
```

## Why

- **HPOS (High-Performance Order Storage)** — WC 8.0+ uses custom tables; screen IDs changed from `shop_order` to `woocommerce_page_wc-orders`
- **`woocommerce_admin_order_preview_*`** — 34 hooks for customizing order preview in list table
- **Settings API** — `woocommerce_get_settings_{$id}` returns settings array
- **Meta boxes** — `add_meta_boxes_{$screen_id}` for order/product edit screens
- **Always check HPOS compatibility** — use `wc_get_order()` instead of post functions

Reference: [WooCommerce Admin](https://developer.woocommerce.com/docs/woocommerce-admin-customization/)
