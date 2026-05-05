---
title: Dynamic Block Rendering
impact: HIGH
impactDescription: Correct dynamic rendering ensures server-side content displays properly
tags: block, dynamic, rendering, php
---

## Dynamic Block Rendering

**Impact: HIGH (dynamic blocks render on every page load; mistakes break frontend output)**

Dynamic blocks generate content at render time via PHP instead of saving static HTML. Use `render` in `block.json` pointing to a PHP file, or `render_callback` in PHP registration.

## Bad Example

```php
register_block_type_from_metadata( __DIR__ . '/blocks/latest-posts', [
    'render_callback' => function( $attrs ) {
        $posts = get_posts();
        $html = '<ul>';
        foreach ( $posts as $p ) {
            $html .= '<li>' . $p->post_title . '</li>';
        }
        $html .= '</ul>';
        return $html;
    },
] );
```

## Good Example

```json
// block.json
{
    "name": "my-plugin/latest-posts",
    "render": "file:./render.php"
}
```

```php
// render.php
$posts = get_posts( [
    'numberposts' => $attributes['count'] ?? 5,
] );
?>
<div <?php echo get_block_wrapper_attributes(); ?>>
    <ul>
    <?php foreach ( $posts as $p ) : ?>
        <li><?php echo esc_html( $p->post_title ); ?></li>
    <?php endforeach; ?>
    </ul>
</div>
```

## Why

- **`render` field in block.json** is the preferred approach — no extra PHP registration args needed
- **Always use `get_block_wrapper_attributes()`** — preserves support-generated classes, styles, and anchors
- **Keep `save()` empty or null** for fully dynamic blocks — no static HTML to deprecate
- **Registration runs on every request** — don't gate behind `is_admin()` or `admin_init`
- **Escape output** — use `esc_html()`, `esc_url()`, `esc_attr()` in render templates

Reference: [Dynamic Rendering](https://developer.wordpress.org/block-editor/reference-guides/block-api/block-dynamic-rendering/)
