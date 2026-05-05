---
title: Plugin Lifecycle Hooks
impact: CRITICAL
impactDescription: Incorrect lifecycle handling causes 404s, data loss, and failed activations
tags: plugin, lifecycle, activation, deactivation, uninstall
---

## Plugin Lifecycle Hooks

**Impact: CRITICAL (activation/deactivation/uninstall must be handled correctly)**

Activation and deactivation hooks must be registered at the **top level** (not nested in other hooks). Uninstall must check `WP_UNINSTALL_PLUGIN` constant. Flush rewrite rules only after CPTs are registered.

## Bad Example

```php
add_action( 'init', function() {
    register_activation_hook( __FILE__, 'my_plugin_activate' );
} );

function my_plugin_activate() {
    flush_rewrite_rules();
}
```

## Good Example

```php
register_activation_hook( __FILE__, 'my_plugin_activate' );
register_deactivation_hook( __FILE__, 'my_plugin_deactivate' );

function my_plugin_activate() {
    my_plugin_register_post_types();
    flush_rewrite_rules();
    add_option( 'my_plugin_db_version', '1.0' );
}

function my_plugin_deactivate() {
    flush_rewrite_rules();
}
```

```php
// uninstall.php (in plugin root)
if ( ! defined( 'WP_UNINSTALL_PLUGIN' ) ) {
    exit;
}
delete_option( 'my_plugin_db_version' );
delete_option( 'my_plugin_settings' );
```

## Why

- **Top-level registration** — `register_activation_hook()` inside another hook never fires
- **Register CPTs before flushing** — flushing before post types are registered causes 404s
- **`add_option()` over `update_option()`** for activation — avoids overwriting existing settings
- **`uninstall.php` preferred** over `register_uninstall_hook()` — simpler, no callback overhead
- **Always check `WP_UNINSTALL_PLUGIN`** — prevents accidental data deletion
- **Deactivation should clean up** — flush rewrite rules, remove transients

Reference: [Activation/Deactivation](https://developer.wordpress.org/plugins/plugin-basics/activation-deactivation-hooks/) | [Uninstall](https://developer.wordpress.org/plugins/plugin-basics/uninstall-methods/)
