---
title: Block Registration with PHP
impact: CRITICAL
impactDescription: Correct registration ensures blocks appear in editor and render properly
tags: block, registration, php, init
---

## Block Registration with PHP

**Impact: CRITICAL (blocks fail silently when registered incorrectly)**

Prefer PHP registration via `register_block_type_from_metadata()`. Register on the `init` hook. Registration must run on every request, not only in admin.

## Bad Example

```php
register_block_type( 'my-plugin/my-block', [
    'render_callback' => 'my_render',
] );

add_action( 'admin_init', function() {
    register_block_type_from_metadata( __DIR__ . '/blocks/my-block' );
} );
```

## Good Example

```php
add_action( 'init', function() {
    register_block_type_from_metadata( __DIR__ . '/blocks/my-block' );
} );
```

## Why

- **`register_block_type_from_metadata()`** reads `block.json` automatically — keeps metadata authoritative
- **`init` hook** fires on every request (frontend + admin + REST) — blocks must be registered everywhere
- **`admin_init` only fires in admin** — block would be missing from REST API and frontend
- **`render` field in block.json** points to a PHP file for dynamic blocks — no separate `render_callback` needed

### Inside render.php

```php
<div <?php echo get_block_wrapper_attributes(); ?>>
    <p><?php echo esc_html( $attributes['content'] ); ?></p>
</div>
```

Always use `get_block_wrapper_attributes()` in render output — it preserves support-generated classes and styles.

Reference: [register_block_type_from_metadata()](https://developer.wordpress.org/reference/functions/register_block_type_from_metadata/) | [Block Registration](https://developer.wordpress.org/block-editor/reference-guides/block-api/block-metadata/)
