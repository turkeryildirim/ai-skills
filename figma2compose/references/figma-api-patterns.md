# Figma MCP Tools & API Invocation Patterns

## Overview

This document provides detailed invocation patterns, schema definitions, and best practices for retrieving design specifications using **Figma MCP Tools**.

**Important**: This skill uses **Figma MCP Tools** as the primary choice. Direct API invocation should only be used as a fallback when the MCP connection fails.

---

## Priority of Approaches

### 1. Primary Choice: Figma MCP Tools (Recommended)

✅ **When to Use**:
- In all standard cases.
- When Figma MCP is active and available in the environment.

✅ **Benefits**:
- Simple calls (URL specification only).
- Automatic error handling.
- Optimized framework-specific output parsing.

### 2. Fallback: Direct API Invocation (Exceptional)

⚠️ **When to Use**:
- Only when the MCP connection fails.
- For custom automated API scripts.

⚠️ **Drawbacks**:
- Requires manual token management (`FIGMA_API_TOKEN`).
- Requires manual parsing of raw JSON node trees.
- No automatic framework mapping.

---

## URL Structure & Parsing Rules

### Figma Dev Mode Link Structure
Figma links from the web browser or Dev Mode typically look like this:
```
https://www.figma.com/design/[fileKey]/[fileName]?node-id=[nodeId]&m=dev

Example:
https://www.figma.com/design/abc123XYZ/MainScreen?node-id=29434-393401&m=dev
```

### Critical Node ID Formatting Rule
Figma URLs represent node IDs with **hyphens** (e.g., `29434-393401`), but the Figma API and MCP server tools expect **colon-separated** node IDs (e.g., `29434:393401`).

> [!IMPORTANT]
> **RULE:** Always replace hyphens with colons (`-` -> `:`) in the parsed `node-id` parameter before passing it to any Figma MCP server tool or API call.

---

## Figma MCP Tools

### 1. `get_design_context(node_url, framework)`
**Purpose**: The primary tool used to fetch layout, color, typography, and structure data.

**Parameters**:
- `node_url`: The parsed Figma node URL (e.g., `https://www.figma.com/design/abc123XYZ/MainScreen?node-id=29434:393401`).
- `framework` (Optional): Specify `"Android/Compose"` to get context mapping optimized for Jetpack Compose.

**Example Invocation**:
```
Tool: get_design_context
Arguments: {
  "node_url": "https://www.figma.com/design/abc123XYZ/MainScreen?node-id=29434:393401",
  "framework": "Android/Compose"
}
```

### 2. `get_screenshot(node_url)`
**Purpose**: Captures a visual image preview of the component or screen to serve as the visual source-of-truth.

**Example Invocation**:
```
Tool: get_screenshot
Arguments: {
  "node_url": "https://www.figma.com/design/abc123XYZ/MainScreen?node-id=29434:393401"
}
```

### 3. `get_variable_defs(node_url)`
**Purpose**: Retrieves all defined design variables (e.g., color values, margins, heights, padding tokens) and their corresponding light/dark modes.

**Example Invocation**:
```
Tool: get_variable_defs
Arguments: {
  "node_url": "https://www.figma.com/design/abc123XYZ/MainScreen?node-id=29434:393401"
}
```

### 4. `get_metadata(node_url)`
**Purpose**: Fetches a sparse node tree of the component hierarchy, useful for identifying nested layout wrappers and child elements.

**Example Invocation**:
```
Tool: get_metadata
Arguments: {
  "node_url": "https://www.figma.com/design/abc123XYZ/MainScreen?node-id=29434:393401"
}
```

### 5. `get_code_connect_map(node_url)` & `add_code_connect_map(node_url, code_path)`
**Purpose**: Manages mappings between Figma components and existing Composable functions inside your codebase to promote maximum reusability.

---

## Direct API Fallback Patterns

If the Figma MCP server is offline, fallback to direct API calls using `curl` and environment variables.

### Environment Variable Setup
```bash
export FIGMA_API_TOKEN="your-figma-personal-access-token"
```

### Fetching Node Details via cURL
```bash
curl -H "X-FIGMA-TOKEN: $FIGMA_API_TOKEN" \
  -s "https://api.figma.com/v1/files/abc123XYZ/nodes?ids=29434:393401" | jq '.'
```

### JSON Response Mapping

```json
{
  "nodes": {
    "29434:393401": {
      "document": {
        "id": "29434:393401",
        "name": "ArticleCard",
        "type": "FRAME",
        "backgroundColor": { "r": 0.96, "g": 0.96, "b": 0.96, "a": 1 },
        "cornerRadius": 4,
        "paddingLeft": 10,
        "paddingTop": 20,
        "itemSpacing": 10,
        "style": {
          "fontSize": 17,
          "fontWeight": 700,
          "lineHeightPx": 22.95
        }
      }
    }
  }
}
```

---

## Best Practices & Step-by-Step Flow

1. **Parse & Reformat**: Parse the Figma URL and format the `nodeId` replacing hyphens with colons.
2. **Retrieve Variables First**: Execute `get_variable_defs(node_url)` to identify collections, semantic colors, modes, and reusable spacing tokens.
3. **Retrieve Design Details Second**: Invoke `get_design_context(node_url, framework="Android/Compose")` as the primary Compose-oriented source of truth.
4. **Resolve Hierarchy When Needed**: Use `get_metadata(node_url)` when wrappers, nesting, or child ordering are unclear.
5. **Check Existing Mappings**: Use `get_code_connect_map(node_url)` before creating new components that may already exist in code.
6. **Visual Comparison**: Run `get_screenshot(node_url)` to verify omissions or obvious structural mistakes, not to guess missing values.
7. **Fall Back Elegantly**: In the event of MCP connection failure, fetch using `curl` and parse using native JSON queries.
