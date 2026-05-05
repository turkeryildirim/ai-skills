---
title: WooCommerce Checkout Customization
impact: HIGH
impactDescription: Checkout modifications directly impact conversion rates
tags: woocommerce, checkout, fields, validation, order-creation
---

## WooCommerce Checkout Customization

**Impact: HIGH (checkout is the conversion bottleneck; errors lose sales)**

Use `woocommerce_checkout_fields` to modify fields. Validate with `woocommerce_checkout_process`. Create orders via `woocommerce_checkout_create_order` hook. Never bypass WooCommerce's checkout flow.

## Bad Example

```php
add_action( 'wp_ajax_custom_checkout', function() {
    global $wpdb;
    $wpdb->insert( $wpdb->prefix . 'posts', [
        'post_type'   => 'shop_order',
        'post_status' => 'wc-processing',
    ] );
} );
```

## Good Example

```php
// Add custom checkout field
add_filter( 'woocommerce_checkout_fields', function( $fields ) {
    $fields['billing']['billing_vat'] = [
        'label'       => __( 'VAT Number', 'my-plugin' ),
        'type'        => 'text',
        'required'    => false,
        'priority'    => 120,
        'class'       => [ 'form-row-wide' ],
    ];
    return $fields;
} );

// Validate
add_action( 'woocommerce_checkout_process', function() {
    if ( ! empty( $_POST['billing_vat'] ) && ! my_validate_vat( $_POST['billing_vat'] ) ) {
        wc_add_notice( 'Invalid VAT number.', 'error' );
    }
} );

// Save to order
add_action( 'woocommerce_checkout_update_order_meta', function( $order_id ) {
    if ( ! empty( $_POST['billing_vat'] ) ) {
        $order = wc_get_order( $order_id );
        $order->update_meta_data( '_billing_vat', sanitize_text_field( $_POST['billing_vat'] ) );
        $order->save();
    }
} );
```

## Why

- **`woocommerce_checkout_fields`** — add, remove, or modify billing/shipping/account fields
- **`woocommerce_checkout_process`** — server-side validation before order creation
- **`woocommerce_checkout_create_order`** — modify order data during creation (before save)
- **`woocommerce_checkout_update_order_meta`** — save custom fields to order
- **Never bypass checkout flow** — direct DB inserts skip payment, inventory, emails, taxes
- **`wc_add_notice()`** — display validation errors to customer
- **Field priority** — controls field ordering in the form

Reference: [WooCommerce Checkout](https://developer.woocommerce.com/docs/woocommerce-checkout/)
