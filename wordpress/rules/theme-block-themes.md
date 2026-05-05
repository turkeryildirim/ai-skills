---
title: Block Theme Structure
impact: CRITICAL
impactDescription: Correct block theme structure is required for WordPress 6.9+ themes
tags: theme, block-theme, structure, theme-json
---

## Block Theme Structure

**Impact: CRITICAL (incorrect structure prevents theme from being recognized)**

Block themes use `theme.json` + `templates/` directory. Style hierarchy: core defaults → theme.json → child theme → user customizations. Templates in `templates/`, parts in `parts/`, patterns in `patterns/`, style variations in `styles/`.

## Bad Example

```
my-theme/
├── style.css
├── functions.php
├── header.php
├── footer.php
├── index.php
└── sidebar.php
```

## Good Example

```
my-theme/
├── style.css           (theme header only)
├── theme.json          (settings + styles)
├── templates/
│   ├── index.html      (required minimum)
│   ├── single.html
│   ├── page.html
│   ├── archive.html
│   └── 404.html
├── parts/
│   ├── header.html
│   └── footer.html
├── patterns/
│   └── hero-section.php
└── styles/
    └── dark.json       (style variation)
```

## Why

- **`theme.json` required** — without it, WordPress treats it as a classic theme
- **`templates/index.html` is minimum** — every block theme must have this
- **Template parts must not be nested** — `parts/header.html` is valid, `parts/layout/header.html` is not
- **User customizations override theme** — edits in Site Editor are stored in DB and override `theme.json`
- **Use "Create Block Theme" plugin** — preferred method for scaffolding new block themes
- **Schema version** — pick highest matching your minimum supported WP version

Reference: [Block Themes](https://developer.wordpress.org/themes/block-themes/) | [Create Block Theme](https://wordpress.org/plugins/create-block-theme/)
