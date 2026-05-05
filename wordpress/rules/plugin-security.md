---
title: Plugin Security
impact: CRITICAL
impactDescription: Security vulnerabilities in plugins are the #1 WordPress attack vector
tags: plugin, security, nonce, sanitization, escaping, sql
---

## Plugin Security

**Impact: CRITICAL (security vulnerabilities are the #1 attack vector in WordPress plugins)**

Always pair nonces with capability checks. Sanitize on input, escape on output. Use `$wpdb->prepare()` for all SQL. Never process entire `$_POST`/`$_GET` arrays.

## Bad Example

```php
if ( isset( $_POST['submit'] ) ) {
    update_option( 'my_setting', $_POST['my_setting'] );
}

$wpdb->query( "DELETE FROM {$wpdb->prefix}my_table WHERE id = " . $_GET['id'] );

echo '<div>' . $user_input . '</div>';
```

## Good Example

```php
if ( isset( $_POST['submit'] ) ) {
    if ( ! isset( $_POST['my_nonce'] ) || ! wp_verify_nonce( $_POST['my_nonce'], 'my_action' ) ) {
        wp_die( 'Nonce verification failed' );
    }
    if ( ! current_user_can( 'manage_options' ) ) {
        wp_die( 'Unauthorized' );
    }
    $value = sanitize_text_field( wp_unslash( $_POST['my_setting'] ) );
    update_option( 'my_setting', $value );
}

$wpdb->delete( $wpdb->prefix . 'my_table', [ 'id' => absint( $_GET['id'] ) ] );

echo '<div>' . esc_html( $user_input ) . '</div>';
```

## Why

- **Nonce + capability check** — nonces prevent CSRF, `current_user_can()` prevents authorization bypass. Both required.
- **Sanitize on input, escape on output** — the golden rule of WordPress security
- **`wp_unslash()` before sanitizing** — WordPress magic-quotes all `$_POST`/`$_GET`
- **`$wpdb->prepare()`** for all SQL — prevents SQL injection. Use `$wpdb->delete()` / `$wpdb->insert()` for simple operations.
- **Never interpolate user input into SQL** — even numeric values
- **Context-specific escaping:** `esc_html()` for body, `esc_attr()` for attributes, `esc_url()` for URLs, `wp_kses_post()` for HTML content

Reference: [Plugin Security](https://developer.wordpress.org/plugins/security/) | [Data Validation](https://developer.wordpress.org/plugins/security/data-validation/)
