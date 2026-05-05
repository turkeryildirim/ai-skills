---
title: block.json as Source of Truth
impact: CRITICAL
impactDescription: Prevents "Invalid block" errors and ensures correct block registration
tags: block, block-json, gutenberg, registration
---

## block.json as Source of Truth

**Impact: CRITICAL (prevents Invalid block errors and registration failures)**

`block.json` is the canonical metadata source for WordPress blocks. All block definition should live here, not scattered across PHP and JS. WordPress 6.9+ requires `apiVersion: 3`.

## Bad Example

```php
register_block_type( 'my-plugin/my-block', [
    'attributes'      => [ 'content' => [ 'type' => 'string' ] ],
    'editor_script'   => 'my-block-editor',
    'editor_style'    => 'my-block-editor-style',
    'style'           => 'my-block-style',
    'render_callback' => function( $attrs ) { return '<div>' . $attrs['content'] . '</div>'; },
] );
```

## Good Example

```json
{
    "$schema": "https://schemas.wp.org/trunk/block.json",
    "apiVersion": 3,
    "name": "my-plugin/my-block",
    "title": "My Block",
    "category": "text",
    "attributes": {
        "content": { "type": "string", "source": "html", "selector": "p" }
    },
    "editorScript": "file:./editor.js",
    "editorStyle": "file:./editor.css",
    "style": "file:./style.css",
    "render": "file:./render.php"
}
```

## Why

- **Single source of truth:** All metadata in one file; PHP and JS read from it automatically
- **apiVersion 3 required:** WP 6.9 enforces this; WP 7.0 will iframe the editor regardless
- **Asset scoping:** `editorScript`/`editorStyle` load only in editor; `viewScript`/`viewStyle` load on frontend
- **Modern asset loading:** Prefer `viewScriptModule` over `viewScript` for module-based frontend scripts
- **Stable API:** `name` is permanent — renaming breaks existing content. Never rename.

Reference: [Block JSON Reference](https://developer.wordpress.org/block-editor/reference-guides/block-api/block-metadata/) | [apiVersion 3](https://make.wordpress.org/core/2024/10/16/edit-site-editor-iframe/)
