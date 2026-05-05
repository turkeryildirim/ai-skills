---
title: Block Deprecations
impact: CRITICAL
impactDescription: Missing deprecations cause "Invalid block" errors on existing content
tags: block, deprecations, migration, gutenberg
---

## Block Deprecations

**Impact: CRITICAL (prevents "Invalid block" errors on published content)**

When you change a block's saved markup or attributes, existing content using the old markup will show "Invalid block" errors. You must add deprecation entries to handle migration.

## Bad Example

```js
// Changed the wrapper from <div> to <section> — existing blocks break
registerBlockType( 'my-plugin/my-block', {
    edit: Edit,
    save: () => <section><InnerBlocks.Content /></section>,
} );
```

## Good Example

```js
registerBlockType( 'my-plugin/my-block', {
    edit: Edit,
    save: () => <section><InnerBlocks.Content /></section>,
    deprecated: [
        {
            attributes: { content: { type: 'string' } },
            save: () => <div><InnerBlocks.Content /></div>,
            migrate( oldAttrs ) {
                return { ...oldAttrs, migrated: true };
            },
        },
    ],
} );
```

## Why

- **Newest first:** Order `deprecated` entries from newest to oldest
- **Each entry needs:** `attributes`, `supports`, `save` (at minimum), optionally `migrate`
- **Changing `save()` output without deprecation** = guaranteed "Block Invalid" for all existing content
- **Adding attributes without correct `source`/`selector`** = attribute not saving
- **Keep fixtures:** Store example content for each deprecated version for testing
- **`name` is permanent:** Never rename — renaming is un-deprecateable

Reference: [Block Deprecation](https://developer.wordpress.org/block-editor/reference-guides/block-api/block-deprecation/)
