---
title: Settings API
impact: HIGH
impactDescription: Proper Settings API usage ensures secure and functional admin options
tags: plugin, settings, admin, options
---

## Settings API

**Impact: HIGH (settings pages are the primary plugin configuration interface)**

Use the Settings API trio: `register_setting()` → `add_settings_section()` → `add_settings_field()`. Always provide `sanitize_callback`. Check capabilities on settings pages.

## Bad Example

```php
add_action( 'admin_menu', function() {
    add_menu_page( 'My Plugin', 'My Plugin', 'read', 'my-plugin', 'my_plugin_page' );
} );

function my_plugin_page() {
    if ( isset( $_POST['my_option'] ) ) {
        update_option( 'my_option', $_POST['my_option'] );
    }
    echo '<input name="my_option" value="' . get_option( 'my_option' ) . '">';
}
```

## Good Example

```php
add_action( 'admin_init', function() {
    register_setting( 'my_plugin_group', 'my_plugin_option', [
        'sanitize_callback' => 'sanitize_text_field',
    ] );
    add_settings_section( 'my_section', 'General', '__return_null', 'my_plugin_page' );
    add_settings_field( 'my_field', 'My Field', 'my_field_render', 'my_plugin_page', 'my_section' );
} );

function my_field_render() {
    $value = get_option( 'my_plugin_option' );
    printf(
        '<input type="text" name="my_plugin_option" value="%s" class="regular-text">',
        esc_attr( $value )
    );
}
```

## Why

- **`register_setting()` with `sanitize_callback`** — validation/sanitization is automatic
- **Capability checks** — settings pages require `manage_options` or custom capability
- **Escape on output** — `esc_attr()` for form values, `esc_html()` for display text
- **`wp_unslash()` before sanitizing** — WordPress adds slashes to `$_POST`/`$_GET`
- **Never trust `$_POST` directly** — use specific keys after nonce verification
- **Settings API handles nonces** — `settings_fields()` outputs the nonce automatically

Reference: [Settings API](https://developer.wordpress.org/plugins/settings/)
