---
title: Plugin Architecture
impact: CRITICAL
impactDescription: Proper structure prevents conflicts, enables maintenance, and follows WordPress conventions
tags: plugin, architecture, structure, bootstrap
---

## Plugin Architecture

**Impact: CRITICAL (poor architecture causes conflicts, performance issues, and maintenance nightmares)**

WordPress plugins should follow a single bootstrap file pattern with hook-based loading. Keep admin-only code behind `is_admin()` or admin hooks. Avoid heavy side effects at file load time.

## Bad Example

```php
<?php
/**
 * Plugin Name: My Plugin
 */

define( 'MY_PLUGIN_PATH', plugin_dir_path( __FILE__ ) );

require_once MY_PLUGIN_PATH . 'includes/post-types.php';
require_once MY_PLUGIN_PATH . 'includes/admin.php';
require_once MY_PLUGIN_PATH . 'includes/shortcodes.php';

add_action( 'init', 'my_plugin_register_post_types' );
add_action( 'admin_menu', 'my_plugin_add_admin_page' );
```

## Good Example

```php
<?php
/**
 * Plugin Name: My Plugin
 * Version: 1.0.0
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

require_once __DIR__ . '/class-loader.php';
MyPlugin\Loader::init();
```

```php
namespace MyPlugin;

class Loader {
    public static function init() {
        $self = new self();
        add_action( 'init', [ $self, 'register_post_types' ] );

        if ( is_admin() ) {
            add_action( 'admin_menu', [ $self, 'add_admin_page' ] );
        }
    }
}
```

## Why

- **Single bootstrap file** with plugin header — WordPress discovers plugins via this header
- **`defined('ABSPATH')` check** prevents direct file access
- **Hook-based loading** — register callbacks on hooks, don't execute at load time
- **`is_admin()` guard** — admin-only code should never load on frontend requests
- **Separate `hooks()` method** — don't register hooks in constructor to prevent double-registration
- **Namespace usage** — avoid global namespace pollution

Reference: [Plugin Handbook](https://developer.wordpress.org/plugins/)
