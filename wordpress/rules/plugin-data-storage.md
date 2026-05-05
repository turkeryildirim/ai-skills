---
title: Data Storage and Cron
impact: HIGH
impactDescription: Proper data storage patterns prevent performance issues and data corruption
tags: plugin, data, options, cron, database, schema
---

## Data Storage and Cron

**Impact: HIGH (improper storage causes autoload bloat, failed upgrades, and cron issues)**

Prefer Options API for small config. Custom tables only when needed — always track schema version. Cron tasks must be idempotent. Provide manual trigger paths for debugging.

## Bad Example

```php
register_activation_hook( __FILE__, function() {
    global $wpdb;
    $wpdb->query( "CREATE TABLE IF NOT EXISTS {$wpdb->prefix}my_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        data TEXT
    )" );
} );

wp_schedule_event( time(), 'hourly', 'my_cron_task' );
add_action( 'my_cron_task', function() {
    $items = my_get_unprocessed_items();
    my_process_all( $items );
} );
```

## Good Example

```php
function my_plugin_activate() {
    $version = get_option( 'my_plugin_db_version', '0' );
    if ( version_compare( $version, '1.0', '<' ) ) {
        my_plugin_create_tables();
        update_option( 'my_plugin_db_version', '1.0' );
    }
}

function my_plugin_create_tables() {
    global $wpdb;
    $charset = $wpdb->get_charset_collate();
    $table = $wpdb->prefix . 'my_data';
    $sql = "CREATE TABLE $table (
        id bigint(20) NOT NULL AUTO_INCREMENT,
        data longtext NOT NULL,
        created_at datetime DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY  (id)
    ) $charset;";
    require_once ABSPATH . 'wp-admin/includes/upgrade.php';
    dbDelta( $sql );
}

// Cron — idempotent, with manual trigger
add_action( 'my_plugin_hourly_task', 'my_plugin_process_queue' );
function my_plugin_process_queue() {
    $items = get_option( 'my_plugin_queue', [] );
    if ( empty( $items ) ) {
        return;
    }
    $processed = my_plugin_process_items( $items );
    update_option( 'my_plugin_queue', array_diff( $items, $processed ) );
}

// Manual trigger via WP-CLI
if ( defined( 'WP_CLI' ) && WP_CLI ) {
    WP_CLI::add_command( 'my-plugin process', 'my_plugin_process_queue' );
}
```

## Why

- **Schema versioning** — without it, updates fail silently or corrupt data
- **`dbDelta()` for table creation** — WordPress-standard, handles upgrades correctly
- **Options API** for simple config — avoid custom tables for key-value data
- **`autoload => false`** for large options — prevents loading on every request
- **Cron tasks must be idempotent** — WP-Cron may run late or multiple times
- **Manual trigger path** — WP-CLI command or admin action for debugging cron issues

Reference: [Options API](https://developer.wordpress.org/plugins/settings/options-api/) | [WP-Cron](https://developer.wordpress.org/plugins/cron/)
