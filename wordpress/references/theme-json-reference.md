# theme.json Complete Reference

> Full reference for theme.json configuration in WordPress block themes.
> Source: https://developer.wordpress.org/themes/global-settings-and-styles/

---

## Minimal theme.json

```json
{
    "$schema": "https://schemas.wp.org/trunk/theme.json",
    "version": 3,
    "settings": {},
    "styles": {}
}
```

## Top-Level Structure

| Key | Description |
|-----|-------------|
| `$schema` | JSON Schema URL for editor validation |
| `version` | Schema version (2 for WP 6.0+, 3 for WP 6.9+) |
| `settings` | What the editor UI exposes to users |
| `styles` | Default visual appearance |
| `customTemplates` | Custom page templates |
| `templateParts` | Registered template parts |
| `custom` | Custom CSS custom properties |

## Settings (Editor Controls)

### Color

```json
{
    "settings": {
        "color": {
            "palette": [
                { "slug": "primary", "color": "#0073aa", "name": "Primary" },
                { "slug": "dark", "color": "#23282d", "name": "Dark" }
            ],
            "gradients": [
                { "slug": "custom", "gradient": "linear-gradient(to right, #0073aa, #00a0d2)", "name": "Custom" }
            ],
            "duotone": [
                { "slug": "dark", "colors": ["#000000", "#ffffff"], "name": "Dark" }
            ],
            "custom": true,
            "customDuotone": true,
            "customGradient": true,
            "defaultDuotone": true,
            "defaultGradients": true,
            "defaultPalette": true,
            "text": true,
            "background": true,
            "link": true
        }
    }
}
```

### Typography

```json
{
    "settings": {
        "typography": {
            "fontFamilies": [
                { "slug": "primary", "fontFamily": "Georgia, serif", "name": "Primary" }
            ],
            "fontSizes": [
                { "slug": "small", "size": "0.875rem", "name": "Small" },
                { "slug": "large", "size": "2rem", "name": "Large" }
            ],
            "fontStyle": true,
            "fontWeight": true,
            "letterSpacing": true,
            "lineHeight": true,
            "textDecoration": true,
            "textTransform": true,
            "dropCap": true
        }
    }
}
```

### Spacing

```json
{
    "settings": {
        "spacing": {
            "units": ["px", "em", "rem", "%", "vw", "vh"],
            "padding": true,
            "margin": true,
            "blockGap": true,
            "customSpacingSize": true,
            "spacingSizes": [
                { "slug": "small", "size": "0.5rem", "name": "Small" },
                { "slug": "medium", "size": "1rem", "name": "Medium" },
                { "slug": "large", "size": "2rem", "name": "Large" }
            ]
        }
    }
}
```

### Border (WP 6.9+)

```json
{
    "settings": {
        "border": {
            "color": true,
            "radius": true,
            "style": true,
            "width": true,
            "radiusSizes": [
                { "slug": "small", "name": "Small", "size": "4px" },
                { "slug": "medium", "name": "Medium", "size": "8px" },
                { "slug": "large", "name": "Large", "size": "16px" }
            ]
        }
    }
}
```

### Layout

```json
{
    "settings": {
        "layout": {
            "contentSize": "800px",
            "wideSize": "1200px"
        }
    }
}
```

### Per-Block Settings

```json
{
    "settings": {
        "blocks": {
            "core/paragraph": {
                "color": {
                    "text": false,
                    "background": false
                },
                "typography": {
                    "dropCap": false
                }
            },
            "core/button": {
                "color": {
                    "palette": [
                        { "slug": "btn-primary", "color": "#0073aa", "name": "Primary" }
                    ]
                }
            }
        }
    }
}
```

## Styles (Default Appearance)

### Global Styles

```json
{
    "styles": {
        "color": {
            "background": "var(--wp--preset--color--dark)",
            "text": "var(--wp--preset--color--light)"
        },
        "typography": {
            "fontFamily": "var(--wp--preset--font-family--primary)",
            "fontSize": "var(--wp--preset--font-size--normal)",
            "lineHeight": "1.6"
        },
        "spacing": {
            "padding": { "top": "0", "right": "var(--wp--style--root--padding-right)", "bottom": "0", "left": "var(--wp--style--root--padding-left)" }
        }
    }
}
```

### Element Styles

```json
{
    "styles": {
        "elements": {
            "button": {
                "color": { "background": "var(--wp--preset--color--primary)", "text": "#ffffff" },
                "border": { "radius": "4px" },
                "typography": { "fontWeight": "600" },
                ":hover": { "color": { "background": "#0056b3" } },
                ":focus": { "outline": { "offset": "2px", "width": "2px", "color": "#0073aa" } },
                ":visited": { "color": { "text": "#ffffff" } }
            },
            "link": {
                "color": { "text": "var(--wp--preset--color--primary)" },
                ":hover": { "color": { "text": "#0056b3" } }
            },
            "heading": {
                "color": { "text": "var(--wp--preset--color--dark)" },
                "typography": { "fontWeight": "700" }
            },
            "input": {
                "border": { "radius": "4px", "color": "#cccccc", "width": "1px" },
                "color": { "text": "#333333" },
                "spacing": { "padding": "0.5rem" }
            },
            "select": {
                "border": { "radius": "4px" }
            },
            "h1": { "typography": { "fontSize": "var(--wp--preset--font-size--x-large)" } },
            "h2": { "typography": { "fontSize": "var(--wp--preset--font-size--large)" } },
            "h3": { "typography": { "fontSize": "var(--wp--preset--font-size--medium)" } }
        }
    }
}
```

### Per-Block Styles

```json
{
    "styles": {
        "blocks": {
            "core/post-title": {
                "typography": { "fontSize": "var(--wp--preset--font-size--x-large)", "fontWeight": "700" },
                "color": { "text": "var(--wp--preset--color--dark)" },
                "elements": {
                    "link": {
                        "color": { "text": "var(--wp--preset--color--dark)" },
                        ":hover": { "color": { "text": "var(--wp--preset--color--primary)" } }
                    }
                }
            },
            "core/button": {
                "border": { "radius": "0" },
                "color": { "background": "var(--wp--preset--color--primary)" }
            }
        }
    }
}
```

## Custom CSS Properties

```json
{
    "settings": {
        "custom": {
            "base-font-size": "1rem",
            "max-width": "1200px",
            "border-radius": "4px"
        }
    }
}
```

Access via CSS: `var(--wp--custom--base-font-size)`

## Style Hierarchy

```
1. WordPress core defaults
2. theme.json (current theme)
3. theme.json (child theme, overrides parent)
4. User customizations (stored in DB, always wins)
```

**Important:** User customizations in Site Editor are stored in the database and always override theme.json values. If your changes seem "ignored," check for user customizations.

Reference: [theme.json](https://developer.wordpress.org/themes/global-settings-and-styles/) | [CSS Custom Properties](https://developer.wordpress.org/themes/global-settings-and-styles/styles/)
