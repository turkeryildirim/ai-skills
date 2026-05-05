---
title: WooCommerce Email Customization
impact: HIGH
impactDescription: Email is the primary post-purchase communication channel
tags: woocommerce, email, templates, notification
---

## WooCommerce Email Customization

**Impact: HIGH (emails are the primary customer communication channel)**

WooCommerce has per-email-type variable hooks for recipients, subjects, headings, and content. Override templates via `woocommerce/templates/` path in theme. Use `woocommerce_email_` hooks for programmatic customization.

## Bad Example

```php
add_filter( 'woocommerce_email_subject_new_order', function( $subject ) {
    return 'New Order!';
} );

// Editing core template files directly
```

## Good Example

```php
// Per-email-type customization via variable hooks
add_filter( 'woocommerce_email_recipient_customer_processing_order', function( $recipient, $order ) {
    if ( ! $order ) {
        return $recipient;
    }
    return $recipient . ', bcc@example.com';
}, 10, 2 );

add_filter( 'woocommerce_email_subject_customer_processing_order', function( $subject, $order ) {
    return sprintf( 'Your order #%s is being processed', $order->get_order_number() );
}, 10, 2 );

// Add content to all WooCommerce emails
add_action( 'woocommerce_email_after_order_table', function( $order, $sent_to_admin, $plain_text, $email ) {
    if ( ! $sent_to_admin ) {
        echo '<p>Thank you for shopping with us!</p>';
    }
}, 10, 4 );

// Template override: place in theme/woocommerce/emails/customer-processing-order.php
// Or use woocommerce_locate_template filter for plugin-based overrides
```

## Why

- **Variable hooks per email** — `woocommerce_email_recipient_{email_id}`, `woocommerce_email_subject_{email_id}`, `woocommerce_email_heading_{email_id}`
- **Email IDs:** `new_order`, `customer_processing_order`, `customer_completed_order`, `customer_on_hold_order`, `customer_refunded_order`, `customer_invoice`, `cancelled_order`, `failed_order`, etc.
- **Template override** — copy from `woocommerce/templates/emails/` to `theme/woocommerce/emails/`
- **`$sent_to_admin`** — check this flag to differentiate admin vs customer emails
- **`$email` object** — access email ID, settings, and template via the `$email` parameter
- **HTML format** — WooCommerce emails are HTML by default; use `$plain_text` to check format

Reference: [WooCommerce Emails](https://developer.woocommerce.com/docs/woocommerce-emails/)
