---
title: Pattern Registration
impact: MEDIUM
impactDescription: Patterns enable reusable content blocks across the theme
tags: theme, patterns, registration, style-variations
---

## Pattern Registration

**Impact: MEDIUM (patterns provide reusable content blocks for the editor)**

Patterns go in `patterns/*.php`. WordPress registers them automatically via file headers. Keep pattern markup stable. Style variations in `styles/*.json`.

## Bad Example

```php
// Registering patterns manually via functions.php
register_block_pattern( 'my-theme/hero', [
    'title'   => 'Hero Section',
    'content' => '<!-- wp:heading --><h2>Welcome</h2><!-- /wp:heading -->',
] );
```

## Good Example

```php
<?php
// patterns/hero-section.php
/**
 * Title: Hero Section
 * Slug: my-theme/hero-section
 * Categories: featured
 * Keywords: hero, banner
 * Inserter: true
 */
?>
<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"8rem","bottom":"8rem"}}}} -->
<div class="wp-block-group alignfull" style="padding-top:8rem;padding-bottom:8rem">
    <!-- wp:heading {"textAlign":"center","level":1} -->
    <h1 class="wp-block-heading has-text-align-center">Welcome to Our Site</h1>
    <!-- /wp:heading -->
    <!-- wp:paragraph {"align":"center"} -->
    <p class="has-text-align-center">A brief description of what we do.</p>
    <!-- /wp:paragraph -->
    <!-- wp:buttons {"layout":{"type":"flex","justifyContent":"center"}} -->
    <div class="wp-block-buttons">
        <!-- wp:button -->
        <div class="wp-block-button"><a class="wp-block-button__link wp-element-button">Get Started</a></div>
        <!-- /wp:button -->
    </div>
    <!-- /wp:buttons -->
</div>
<!-- /wp:group -->
```

```json
// styles/dark.json
{
    "$schema": "https://schemas.wp.org/trunk/theme.json",
    "version": 3,
    "title": "Dark",
    "styles": {
        "color": { "background": "#1a1a1a", "text": "#ffffff" }
    }
}
```

## Why

- **File-based registration** — WordPress auto-discovers patterns from `patterns/` directory via file headers
- **File headers are required** — `Title`, `Slug`, `Categories` at minimum
- **`Inserter: false`** — hide from inserter for internal/utility patterns
- **Keep markup stable** — changing block names inside patterns breaks older content
- **Style variations** — `styles/*.json` lets users pick visual presets without editing theme
- **User selection is stored in DB** — changing the JSON file won't update already-selected variations

Reference: [Patterns](https://developer.wordpress.org/themes/block-themes/block-patterns/) | [Style Variations](https://developer.wordpress.org/themes/block-themes/style-variations/)
