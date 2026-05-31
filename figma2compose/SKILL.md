---
name: figma2compose
description: Converts Figma MCP design data into production-ready Jetpack Compose UI components for Android with strict spec fidelity and no guesswork.
model: inherit
---

# Figma2Compose

Generate Jetpack Compose UI from Figma by reading exact design data from the Figma MCP server, then converting that data into Android-ready composables without inventing missing values.

## When To Use

Use this skill when:
- The user provides a Figma URL and wants Android UI output.
- The target output is Jetpack Compose code.
- The task is to translate an existing Figma screen, section, or component into Kotlin UI code.

Do not use this skill for:
- Manual visual recreation based only on screenshots.
- XML Views or SwiftUI output.
- Tasks where Figma MCP access is unavailable and the user did not provide usable exported specs.

## Core Contract

This skill exists to produce **Compose code that is traceable to Figma data**.

Non-negotiable rules:
- Do not guess spacing, radii, typography, shadows, or colors.
- Do not add visual polish that is not present in Figma.
- Do not drop child nodes because they are inconvenient to map.
- Do not replace exact tokens with “close enough” Compose defaults.
- Do not hardcode derived offsets when they can be expressed from verified layout values.

If a value is missing from Figma MCP output, state that it is missing and ask for clarification instead of inventing it.

## Load Order

Read these files only as needed:
1. [`references/figma-api-patterns.md`](references/figma-api-patterns.md) for MCP tool calling and URL parsing rules.
2. [`references/compose-conversion-rules.md`](references/compose-conversion-rules.md) for token-to-Compose mapping.
3. [`references/compliance-checklist.md`](references/compliance-checklist.md) for validation criteria.
4. [`scripts/compliance-calculator.py`](scripts/compliance-calculator.py) after generation to score the result.

## Required Workflow

### Phase 0: Audit The Android Codebase First

Before touching Figma:
- Search the target project for similar screens, cards, rows, dialogs, or shared wrappers.
- Reuse existing design-system tokens, typography objects, icon pipelines, scaffold wrappers, and status/navigation bar handling.
- Match established function signatures and project architecture.

Minimum audit targets:
- `ui/`, `designsystem/`, `components/`, `theme/`, `feature/*/ui/`
- Existing `TopAppBar`, `Scaffold`, status bar handling, image loaders, button variants, and typography definitions

### Phase 1: Parse The Figma URL Correctly

Extract:
- `fileKey`
- `node-id`

Critical rule:
- Figma URLs usually expose `node-id=29434-393401`
- MCP calls must use `29434:393401`
- Always normalize hyphens to colons before any Figma MCP tool call

### Phase 2: Call Figma MCP Tools In This Order

1. `get_variable_defs(node_url)`
   - Collect variables, collections, modes, semantic color tokens, and reusable spacing definitions.
2. `get_design_context(node_url, framework="Android/Compose")`
   - Primary source for layout, text, colors, strokes, fills, sizing, and hierarchy.
3. `get_metadata(node_url)`
   - Use when hierarchy or wrapper structure is ambiguous.
4. `get_screenshot(node_url)`
   - Use as a visual verification artifact, not as a source for guessing values.
5. `get_code_connect_map(node_url)`
   - Use to discover reusable existing code mappings before generating new components.

If MCP fails, fall back to direct API only when the environment and task allow it. Follow [`references/figma-api-patterns.md`](references/figma-api-patterns.md).

### Phase 3: Produce A Short Figma Spec Artifact

Before writing Compose code, summarize the verified design inputs in a compact markdown block or file:

```markdown
## Figma Design Spec
Component: PaymentSummaryCard
Node ID: 29434:393401

Colors
- surface: rgba(245, 245, 245, 1.0) -> Color(0xFFF5F5F5)
- title: rgba(51, 51, 51, 1.0) -> Color(0xFF333333)

Typography
- title: 17px / 700 / 22.95px
- body: 15px / 500 / 21px

Layout
- padding: 20px
- gap: 10px
- cornerRadius: 4px
```

This step prevents silent drift between fetched design data and generated code.

### Phase 4: Generate Compose From Verified Tokens

Preferred structure:
- `ComponentNameColors`
- `ComponentNameTypography`
- `ComponentNameDimensions`
- one or more focused composables

Implementation rules:
- Convert Figma RGBA to exact `Color(0xAARRGGBB)`.
- Use exact `sp` and `FontWeight` values from Figma.
- Keep layout math explicit for derived offsets.
- Prefer `statusBarsPadding()`, `navigationBarsPadding()`, or `safeDrawingPadding()` over brittle hardcoded spacer heights.
- Place background and padding modifiers in the correct order so container fills remain edge-to-edge.
- Reuse project wrappers when they already solve scaffold/system bar concerns.

Example:

```kotlin
private object PaymentSummaryCardDimensions {
    val contentPadding = 20.dp
    val rowGap = 10.dp
    val cornerRadius = 4.dp
}
```

### Phase 5: Validate Before Delivering

Run the compliance script when you have:
- a JSON representation of the verified Figma spec
- the generated Kotlin file

Example:

```bash
python figma2compose/scripts/compliance-calculator.py \
  --figma-spec payment-summary-card.json \
  --compose-impl PaymentSummaryCard.kt \
  --output payment-summary-card-compliance.md
```

Expected outcome:
- overall compliance `>= 95%`
- mismatches listed with exact fields to fix

## Compose Mapping Rules

### Colors

```kotlin
rgba(0, 116, 196, 1.0) -> Color(0xFF0074C4)
```

### Typography

```kotlin
TextStyle(
    fontSize = 17.sp,
    fontWeight = FontWeight.Bold,
    lineHeight = 22.95.sp
)
```

### Layout Tokens

```kotlin
private object CardDimensions {
    val imagePadding = 10.dp
    val imageWidth = 72.dp
    val imageGap = 10.dp
    val dividerStartPadding = imagePadding + imageWidth + imageGap
}
```

### Insets

```kotlin
Column(
    modifier = Modifier
        .fillMaxSize()
        .statusBarsPadding()
)
```

Avoid this:

```kotlin
Spacer(modifier = Modifier.height(52.dp))
```

## Delivery Checklist

- [ ] Existing Android codebase was audited first.
- [ ] Figma `node-id` was normalized from `-` to `:`.
- [ ] Variables and design context were fetched from MCP.
- [ ] Compose output reuses existing project patterns where appropriate.
- [ ] No guessed values or visual embellishments were introduced.
- [ ] Derived offsets are explained with named layout tokens.
- [ ] System UI spacing uses Compose insets instead of hardcoded status/nav bar spacers.
- [ ] Compliance report was produced or manually verified against the same criteria.

## Output Expectations

The final result should give the user:
- production-ready Kotlin Compose code
- a short mapping explanation when useful
- compliance findings if mismatches remain

If exact parity cannot be achieved because data is missing from Figma or the target app has architectural constraints, state that explicitly and isolate the unresolved fields.
