---
title: Use Type Guards Over Type Assertions
impact: HIGH
impactDescription: Type assertions (as Type) bypass the compiler and hide bugs that only surface at runtime.
tags: typescript, type-guards, type-narrowing, assertion-functions
---

# Use Type Guards Over Type Assertions

User-defined type guards and assertion functions narrow types safely through actual runtime checks, unlike `as` which silences the compiler without verification.

## Bad Example

```typescript
// Type assertion - no runtime check, just silences the compiler
function processValue(value: unknown) {
  const str = value as string;
  console.log(str.toUpperCase()); // crashes at runtime if value is not a string
}

// Repeated typeof checks without reuse
function formatItems(items: unknown) {
  if (typeof items !== "object" || !Array.isArray(items)) {
    throw new Error("Expected array");
  }
  // items is still unknown[], no element type safety
  items.forEach((item) => console.log((item as string).toUpperCase()));
}

// Casting nested data from API without validation
const response = JSON.parse(body) as { user: { name: string } };
// No actual validation - typo in key name fails silently
```

## Good Example

```typescript
// User-defined type guard - runtime check + compile-time narrowing
function isString(value: unknown): value is string {
  return typeof value === "string";
}

function processValue(value: unknown) {
  if (isString(value)) {
    console.log(value.toUpperCase()); // TypeScript knows: string
  }
}

// Generic array guard - reusable, composable
function isArrayOf<T>(
  value: unknown,
  guard: (item: unknown) => item is T,
): value is T[] {
  return Array.isArray(value) && value.every(guard);
}

const data: unknown = ["a", "b", "c"];
if (isArrayOf(data, isString)) {
  data.forEach((s) => s.toUpperCase()); // TypeScript knows: string[]
}

// Assertion function - throws instead of returning boolean
function assertIsString(value: unknown): asserts value is string {
  if (typeof value !== "string") {
    throw new Error(`Expected string, got ${typeof value}`);
  }
}

function processInput(value: unknown) {
  assertIsString(value);
  // After this line, value is typed as string
  console.log(value.toUpperCase());
}
```

## Why

- **Verified narrowing**: Type guards perform a real runtime check that the compiler trusts for narrowing.
- **Reusability**: A single guard function replaces repeated `typeof` checks and `as` casts throughout the codebase.
- **Assertion functions**: `asserts value is T` throws on mismatch and narrows afterward, ideal for validation boundaries.
- **Generic guards**: `isArrayOf<T>` composes with element guards to validate entire collections safely.
