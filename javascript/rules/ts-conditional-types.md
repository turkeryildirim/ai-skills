---
title: Use Conditional Types Over Manual Type Checking
impact: HIGH
impactDescription: Runtime type checks and manual branching cannot express type-level logic, leading to unsafe casts.
tags: typescript, conditional-types, infer, type-logic
---

# Use Conditional Types Over Manual Type Checking

Conditional types let you express type-level decisions, extract inner types with `infer`, and build utility types that adapt based on input.

## Bad Example

```typescript
// Runtime checking for what should be a type-level concern
function getResult(value: unknown) {
  if (typeof value === "string") {
    return value.toUpperCase(); // still typed as unknown outside this block
  }
  return value;
}

// Manually defining return types instead of extracting them
function getUser() {
  return { id: 1, name: "John" };
}
type UserReturn = { id: number; name: string }; // duplicated manually

// No way to convert a union to an array at the type level
type Items = string | number; // want string[] | number[]
```

## Good Example

```typescript
// Conditional type branches at the type level
type IsString<T> = T extends string ? true : false;
type A = IsString<string>;  // true
type B = IsString<number>;  // false

// Extract return types with infer instead of duplicating
type ReturnOf<T> = T extends (...args: any[]) => infer R ? R : never;

function getUser() {
  return { id: 1, name: "John" };
}
type User = ReturnOf<typeof getUser>; // { id: number; name: string }

// Distributive conditional types - operates on each union member
type ToArray<T> = T extends any ? T[] : never;
type StrOrNumArray = ToArray<string | number>; // string[] | number[]

// Nested conditions for type-level matching
type TypeName<T> = T extends string
  ? "string"
  : T extends number
    ? "number"
    : T extends boolean
      ? "boolean"
      : T extends Function
        ? "function"
        : "object";

type T1 = TypeName<string>;     // "string"
type T2 = TypeName<() => void>; // "function"
```

## Why

- **Compile-time logic**: Conditional types express type relationships without runtime cost.
- **Inference**: The `infer` keyword extracts nested types (return types, array elements, Promise values) without manual duplication.
- **Distribution**: Distributive conditional types automatically map over union members.
- **Safety**: Type-level branching catches mismatches at compile time, not at runtime.
