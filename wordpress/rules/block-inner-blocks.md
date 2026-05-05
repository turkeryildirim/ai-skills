---
title: InnerBlocks and Block Composition
impact: HIGH
impactDescription: Correct InnerBlocks usage enables block nesting and composition
tags: block, inner-blocks, composition, gutenberg
---

## InnerBlocks and Block Composition

**Impact: HIGH (enables block nesting; misuse causes editor errors)**

InnerBlocks allows blocks to contain other blocks. Only one InnerBlocks per block. Use `useInnerBlocksProps` to combine wrapper attributes with inner block area.

## Bad Example

```jsx
function Edit() {
    return (
        <div { ...useBlockProps() }>
            <InnerBlocks allowedBlocks={ [ 'core/paragraph' ] } />
        </div>
    );
}

function Save() {
    return (
        <div { ...useBlockProps.save() }>
            <InnerBlocks.Content />
        </div>
    );
}
```

## Good Example

```jsx
function Edit() {
    const blockProps = useBlockProps();
    const innerBlocksProps = useInnerBlocksProps( blockProps, {
        allowedBlocks: [ 'core/paragraph', 'core/heading' ],
        template: [ [ 'core/paragraph', { placeholder: 'Add content...' } ] ],
    } );
    return <div { ...innerBlocksProps } />;
}

function Save() {
    const blockProps = useBlockProps.save();
    const innerBlocksProps = useInnerBlocksProps.save( blockProps );
    return <div { ...innerBlocksProps } />;
}
```

## Why

- **`useInnerBlocksProps`** combines wrapper props + inner blocks area into a single element — avoids extra wrapper divs
- **Only one InnerBlocks per block** — multiple cause errors
- **`allowedBlocks`** restricts which blocks can be inserted — use sparingly, over-constraining frustrates users
- **`template`** provides default content — helpful for structured layouts
- **Changing wrapper structure containing InnerBlocks** may invalidate existing content — add deprecations
- **`useInnerBlocksProps.save()`** for save — must use `.save()` variant

Reference: [InnerBlocks](https://developer.wordpress.org/block-editor/reference-guides/block-api/block-inner-blocks/)
