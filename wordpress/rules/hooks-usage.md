---
title: WordPress Hooks Usage Guide
impact: CRITICAL
impactDescription: Proper hook usage is the foundation of all WordPress development
tags: hooks, actions, filters, core
---

## WordPress Hooks System

WordPress hooks are the foundation of plugin and theme development. They allow developers to modify WordPress behavior without editing core files. There are two types: **actions** (do something) and **filters** (modify data).

## add_action()

```php
add_action( string $hook_name, callable $callback, int $priority = 10, int $accepted_args = 1 ): true
```

Attaches a callback function to an action hook. Actions are triggered by `do_action()` calls in WordPress core.

**Parameters:**
- `$hook_name` — The action name to hook into
- `$callback` — The function to run (callable)
- `$priority` — Execution order (lower = earlier). Default: 10
- `$accepted_args` — Number of arguments the callback accepts. Default: 1

**Finding arguments:** Search for the matching `do_action()` call:
```php
// In WordPress core:
do_action( 'save_post', $post_ID, $post, $update );

// Your hook:
add_action( 'save_post', 'my_function', 10, 3 );
function my_function( $post_ID, $post, $update ) { }
```

## add_filter()

```php
add_filter( string $hook_name, callable $callback, int $priority = 10, int $accepted_args = 1 ): true
```

Attaches a callback function to a filter hook. Filters are triggered by `apply_filters()` calls. **Must return the modified value.**

**Parameters:** Same as `add_action()`. `add_action()` internally calls `add_filter()`.

```php
add_filter( 'the_title', 'my_modify_title', 10, 2 );
function my_modify_title( $title, $id ) {
    return strtoupper( $title );
}
```

## remove_action() / remove_filter()

```php
remove_action( string $hook_name, callable $callback, int $priority = 10 ): bool
remove_filter( string $hook_name, callable $callback, int $priority = 10 ): bool
```

**Important:** The `$priority` must match the priority used when the hook was added. Closures (anonymous functions) cannot be removed unless assigned to a variable first.

## Priority

Priority determines execution order among callbacks on the same hook:
- Default: `10`
- Lower numbers run first: `1` runs before `10` runs before `99`
- Same priority: executed in registration order

```php
add_action( 'init', 'register_my_cpt', 5 );     // Runs early
add_action( 'init', 'enqueue_my_assets', 20 );   // Runs later
```

**Common priority conventions:**
- `1-9` — Early execution (setup, registration)
- `10` — Default (most callbacks)
- `11-20` — After defaults (modify what others added)
- `99+` — Late execution (cleanup, overrides)

## Accepted Args

Must match the number of arguments passed by `do_action()` / `apply_filters()`. Default is 1.

```php
// Core passes 3 arguments:
do_action( 'save_post', $post_ID, $post, $update );

// Wrong — only receives $post_ID:
add_action( 'save_post', 'my_save', 10 );

// Correct — receives all 3:
add_action( 'save_post', 'my_save', 10, 3 );
```

## Variable Hooks

Some hooks have dynamic names containing variables. These are indicated by `${variable}` patterns or hooks ending with `-`.

**Variable patterns:**
- `save_post_{$post->post_type}` — e.g., `save_post_product`, `save_post_page`
- `manage_{$screen->id}_columns` — e.g., `manage_edit-post_columns`
- `rest_prepare_{$this->post_type}` — e.g., `rest_prepare_post`
- `option_{$option}` — e.g., `option_blogname`, `option_siteurl`
- `pre_option_{$option}` — e.g., `pre_option_active_plugins`
- `{$old_status}_to_{$new_status}` — e.g., `draft_to_publish`
- `{$new_status}_{$post->post_type}` — e.g., `publish_post`, `draft_page`

**Suffix-based hooks:**
- `admin_head-{$hook_suffix}` — e.g., `admin_head-post.php`, `admin_head-plugins.php`
- `load-{$pagenow}` — e.g., `load-edit.php`, `load-plugins.php`

**Usage:**
```php
// Hook into save_post for a custom post type "product":
add_action( 'save_post_product', 'my_product_save', 10, 3 );

// Filter a specific option:
add_filter( 'option_blogname', 'my_custom_blogname' );

// Admin scripts for a specific page:
add_action( 'admin_head-post-new.php', 'my_post_new_scripts' );
```

See `references/variable-hooks.md` for the complete list of variable hooks.

## Callback Registration Patterns

### Functions (simple plugins)

```php
add_action( 'init', 'my_register_cpt' );
function my_register_cpt() {
    register_post_type( 'product', [] );
}
```

### Class methods (OOP plugins)

```php
class My_Plugin {
    public function hooks() {
        add_action( 'init', [ $this, 'register_cpt' ] );
        add_filter( 'the_content', [ $this, 'modify_content' ] );
    }

    public function register_cpt() { }
    public function modify_content( $content ) { return $content; }
}

$plugin = new My_Plugin();
$plugin->hooks();
```

**Important:** Register hooks in a separate `hooks()` method, not in the constructor. This prevents double-registration if the class is instantiated multiple times.

### Static methods

```php
add_action( 'init', [ My_Plugin::class, 'register_cpt' ] );
```

### Closures (use with caution)

```php
add_action( 'wp_footer', function() {
    echo '<!-- Custom footer -->';
});
```

**Warning:** Closures cannot be removed with `remove_action()`. Avoid in distributable plugins/themes. If needed, assign to a variable:

```php
$footer_callback = function() {
    echo '<!-- Custom footer -->';
};
add_action( 'wp_footer', $footer_callback );
// Later: remove_action( 'wp_footer', $footer_callback );
```

## Hook Reference Files

Hook references are organized by functional category. Only load relevant categories for the current task:

**Actions:**
- `references/hooks/actions-core.md` — Core lifecycle (init, plugins_loaded, wp_loaded)
- `references/hooks/actions-admin.md` — Admin UI (admin_menu, admin_enqueue_scripts)
- `references/hooks/actions-content.md` — Posts/content (save_post, transition_post_status)
- `references/hooks/actions-user.md` — Users (user_register, wp_login/logout)
- `references/hooks/actions-media.md` — Media (add_attachment, wp_handle_upload)
- `references/hooks/actions-rest-api.md` — REST API (rest_api_init)
- `references/hooks/actions-comment.md` — Comments (comment_post, wp_insert_comment)
- `references/hooks/actions-theme.md` — Themes (template_redirect, wp_enqueue_scripts)
- `references/hooks/actions-multisite.md` — Multisite (wpmu_*, network_*)
- `references/hooks/actions-other.md` — Other (cron, xmlrpc, feed, customizer)

**Filters:**
- `references/hooks/filters-core.md` — Core (option_*, pre_option_*)
- `references/hooks/filters-admin.md` — Admin (manage_*_columns)
- `references/hooks/filters-content.md` — Content (the_content, the_title, posts_where)
- `references/hooks/filters-user.md` — Users (user_has_cap, authenticate)
- `references/hooks/filters-media.md` — Media (wp_get_attachment_url)
- `references/hooks/filters-rest-api.md` — REST (rest_pre/post_dispatch)
- `references/hooks/filters-comment.md` — Comments (comment_text)
- `references/hooks/filters-theme.md` — Themes (stylesheet_*, template_*)
- `references/hooks/filters-multisite.md` — Multisite (network_*, site_*)
- `references/hooks/filters-other.md` — Other (http_request_*, cron_*)

## Why

- **Extensibility:** Hooks are how all WordPress plugins and themes interact with core. Without proper hook usage, code breaks updates and conflicts with other plugins.
- **Context-aware loading:** By categorizing hooks, you only load relevant reference material for the task at hand, reducing noise.
- **Variable hooks mastery:** Understanding variable hooks is essential for post type-specific, screen-specific, and option-specific customization.

Reference: [add_action()](https://developer.wordpress.org/reference/functions/add_action/) | [add_filter()](https://developer.wordpress.org/reference/functions/add_filter/) | [Plugin API](https://developer.wordpress.org/plugins/hooks/) | [Hook Database](https://adambrown.info/p/wp_hooks)
