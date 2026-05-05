---
title: Templates and Template Parts
impact: HIGH
impactDescription: Templates define the HTML structure of every page in a block theme
tags: theme, templates, parts, html
---

## Templates and Template Parts

**Impact: HIGH (templates define how every page renders in block themes)**

Templates live in `templates/*.html`. Template parts in `parts/*.html`. Parts must not be nested in subdirectories. Reference parts via `<!-- wp:pattern -->` or `<!-- wp:template-part -->` blocks.

## Bad Example

```html
<!-- templates/index.html — flat, no structure -->
<!-- wp:paragraph -->
<p>Welcome to my site</p>
<!-- /wp:paragraph -->
```

## Good Example

```html
<!-- templates/index.html -->
<!-- wp:template-part {"slug":"header","tagName":"header"} /-->

<!-- wp:group {"tagName":"main","layout":{"type":"constrained"}} -->
<main>
    <!-- wp:query {"queryId":1,"query":{"inherit":true}} -->
    <!-- wp:query-loop -->
        <!-- wp:post-title {"isLink":true} /-->
        <!-- wp:post-excerpt /-->
    <!-- /wp:query-loop -->
    <!-- /wp:query -->
</main>
<!-- /wp:group -->

<!-- wp:template-part {"slug":"footer","tagName":"footer"} /-->
```

```html
<!-- parts/header.html -->
<!-- wp:group {"layout":{"type":"constrained"}} -->
<header>
    <!-- wp:site-title /-->
    <!-- wp:navigation {"ref":1} /-->
</header>
<!-- /wp:group -->
```

## Why

- **`templates/` directory** — block HTML files for each template type (index, single, page, archive, 404)
- **`parts/` directory** — reusable template sections (header, footer, sidebar)
- **Parts must not be nested** — `parts/header.html` only, no subdirectories
- **`<!-- wp:template-part -->`** — includes a part by slug
- **`<!-- wp:pattern -->`** — includes a registered pattern
- **Block markup uses HTML comments** — `<!-- wp:block-name {"attrs":...} /-->` for self-closing, paired for wrapping

Reference: [Templates](https://developer.wordpress.org/themes/block-themes/templates-and-template-parts/)
