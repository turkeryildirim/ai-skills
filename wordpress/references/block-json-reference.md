# block.json Complete Reference

> Full reference for block.json metadata fields. WordPress 6.9+ requires apiVersion 3.
> Source: https://developer.wordpress.org/block-editor/reference-guides/block-api/block-metadata/

---

## Minimal block.json

```json
{
    "$schema": "https://schemas.wp.org/trunk/block.json",
    "apiVersion": 3,
    "name": "namespace/block-name",
    "title": "Block Title",
    "category": "text",
    "icon": "smiley",
    "editorScript": "file:./index.js"
}
```

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique identifier (`namespace/block-name`). **Never rename** — breaks existing content. |
| `title` | string | Display title in editor |
| `category` | string | Editor category: `text`, `media`, `design`, `widgets`, `embed`, `reusable` |

## Metadata Fields

| Field | Type | Description |
|-------|------|-------------|
| `apiVersion` | integer | **Must be 3** for WP 6.9+. Required. |
| `description` | string | Block description shown in inspector |
| `icon` | string | Dashicon name or SVG |
| `keywords` | string[] | Search aliases for the inserter |
| `textdomain` | string | Translation text domain |
| `attributes` | object | Block attribute definitions |
| `supports` | object | Feature support declarations |
| `providesContext` | object | Context values this block provides |
| `usesContext` | string[] | Context values this block consumes |
| `example` | object | Preview data for the inserter |
| `styles` | object[] | Named style variations |
| `variations` | object[] | Block variations |
| `allowedBlocks` | string[] | Blocks allowed as children |
| `ancestor` | string[] | Required ancestor blocks |
| `parent` | string[] | Required parent blocks |

## Asset Fields

| Field | Scope | Description |
|-------|-------|-------------|
| `editorScript` | Editor only | JS file for editor: `"file:./editor.js"` or handle |
| `editorStyle` | Editor only | CSS file for editor |
| `script` | Editor + Frontend | Shared JS |
| `style` | Editor + Frontend | Shared CSS |
| `viewScript` | Frontend only | JS loaded when block is present |
| `viewScriptModule` | Frontend only | ES module JS (preferred over viewScript) |
| `viewStyle` | Frontend only | CSS loaded when block is present |
| `render` | Server | PHP render file: `"file:./render.php"` |
| `editorScriptModules` | Editor only | ES module scripts for editor |

## Attributes

```json
{
    "attributes": {
        "content": {
            "type": "string",
            "source": "html",
            "selector": "p",
            "default": ""
        },
        "url": {
            "type": "string",
            "source": "attribute",
            "selector": "a",
            "attribute": "href"
        },
        "columns": {
            "type": "number",
            "default": 3
        },
        "showTitle": {
            "type": "boolean",
            "default": true
        },
        "items": {
            "type": "array",
            "default": []
        }
    }
}
```

### Attribute Types

| Type | Description |
|------|-------------|
| `string` | Text value |
| `number` | Numeric value |
| `boolean` | true/false |
| `array` | List of values |
| `object` | Key-value pairs |

### Attribute Sources

| Source | Description | Example |
|--------|-------------|---------|
| `html` | Inner HTML of selector | `"source": "html", "selector": "p"` |
| `attribute` | HTML attribute value | `"source": "attribute", "selector": "a", "attribute": "href"` |
| `text` | Text content (no HTML) | `"source": "text", "selector": "h2"` |
| `rich-text` | Rich text content | `"source": "rich-text", "selector": "p"` |
| `query` | Multiple elements | `"source": "query", "selector": "li", "query": {...}` |
| `meta` | Post meta | `"source": "meta", "metaKey": "my_meta"` |
| (none) | Stored in block comment | `"type": "number", "default": 3` |

## Supports

```json
{
    "supports": {
        "html": false,
        "align": true,
        "alignWide": true,
        "anchor": true,
        "color": {
            "text": true,
            "background": true,
            "gradients": true,
            "link": true
        },
        "spacing": {
            "margin": true,
            "padding": true,
            "blockGap": true
        },
        "typography": {
            "fontSize": true,
            "lineHeight": true,
            "textAlign": true
        },
        "border": {
            "color": true,
            "radius": true,
            "width": true,
            "style": true
        },
        "shadow": true,
        "layout": true,
        "innerBlocks": {
            "allowedBlocks": ["core/paragraph"]
        }
    }
}
```

Reference: [block.json Metadata](https://developer.wordpress.org/block-editor/reference-guides/block-api/block-metadata/) | [Attributes](https://developer.wordpress.org/block-editor/reference-guides/block-api/block-attributes/)
