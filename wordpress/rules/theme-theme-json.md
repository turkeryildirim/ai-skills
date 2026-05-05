---
title: theme.json Configuration
impact: CRITICAL
impactDescription: theme.json controls all visual settings, styles, and editor defaults
tags: theme, theme-json, settings, styles, presets
---

## theme.json Configuration

**Impact: CRITICAL (theme.json is the single source of truth for theme appearance)**

Top-level keys: `version`, `settings` (what UI exposes), `styles` (default appearance), `customTemplates`, `templateParts`. Use `settings` for editor controls, `styles` for consistent defaults.

## Bad Example

```css
/* style.css — all styling via CSS */
body { font-family: Georgia, serif; color: #333; }
h1, h2, h3 { font-weight: bold; }
.wp-block-button__link { background: #0073aa; }
```

## Good Example

```json
{
    "$schema": "https://schemas.wp.org/trunk/theme.json",
    "version": 3,
    "settings": {
        "color": {
            "palette": [
                { "slug": "primary", "color": "#0073aa", "name": "Primary" },
                { "slug": "secondary", "color": "#23282d", "name": "Secondary" }
            ]
        },
        "typography": {
            "fontSizes": [
                { "slug": "small", "size": "0.875rem", "name": "Small" },
                { "slug": "normal", "size": "1rem", "name": "Normal" },
                { "slug": "large", "size": "1.5rem", "name": "Large" }
            ]
        },
        "spacing": {
            "units": [ "px", "em", "rem", "%", "vw", "vh" ]
        },
        "border": {
            "radiusSizes": [
                { "slug": "small", "name": "Small", "size": "4px" },
                { "slug": "large", "name": "Large", "size": "16px" }
            ]
        }
    },
    "styles": {
        "color": { "background": "var(--wp--preset--color--secondary)", "text": "#ffffff" },
        "typography": { "fontFamily": "var(--wp--preset--font-family--primary)", "fontSize": "var(--wp--preset--font-size--normal)" },
        "elements": {
            "button": {
                "color": { "background": "var(--wp--preset--color--primary)" },
                ":hover": { "color": { "background": "#0056b3" } }
            },
            "input": {
                "border": { "radius": "4px" }
            }
        }
    }
}
```

## Why

- **`settings` controls the editor UI** — what colors, fonts, spacing users can pick
- **`styles` sets defaults** — consistent appearance without user action
- **CSS custom properties** — `var(--wp--preset--color--primary)` for reusable values
- **User customizations override theme** — DB-stored styles always win
- **WP 6.9 additions:** Form element styling, border radius presets, button hover/focus pseudo-classes
- **Schema version matters** — newer versions have more features but require newer WP

Reference: [theme.json](https://developer.wordpress.org/themes/global-settings-and-styles/)
