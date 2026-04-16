---
title: Use Generics Over Any or Duplicated Functions
impact: CRITICAL
impactDescription: Using any or duplicating functions per type destroys type safety and creates unmaintainable code.
tags: typescript, generics, type-safety
---

# Use Generics Over Any or Duplicated Functions

Generics let you write reusable, type-safe functions that work across multiple types without sacrificing compile-time checks.

## Bad Example

```typescript
// Using any - loses all type information
function identity(value: any): any {
  return value;
}

const num = identity(42); // Type: any, not number

// Duplicating functions per type
function logString(item: string): string {
  console.log(item.length);
  return item;
}

function logArray(item: string[]): string[] {
  console.log(item.length);
  return item;
}

// No constraint - accepts anything silently
function merge(obj1: any, obj2: any): any {
  return { ...obj1, ...obj2 };
}
```

## Good Example

```typescript
// Generic function - preserves the exact type
function identity<T>(value: T): T {
  return value;
}

const num = identity(42);    // Type: number
const str = identity("hi");  // Type: string

// Generic with constraint - enforces shape at compile time
interface HasLength {
  length: number;
}

function logLength<T extends HasLength>(item: T): T {
  console.log(item.length);
  return item;
}

logLength("hello");          // OK
logLength([1, 2, 3]);       // OK
// logLength(42);            // Error: number has no length

// Multiple type parameters preserve both sides
function merge<T, U>(obj1: T, obj2: U): T & U {
  return { ...obj1, ...obj2 };
}

const merged = merge({ name: "John" }, { age: 30 });
// Type: { name: string } & { age: number }
```

## Why

- **Type safety**: Generics preserve exact types through function calls instead of widening to `any`.
- **Reusability**: One generic function replaces multiple duplicated per-type implementations.
- **Constraints**: `extends` lets you enforce required shape without losing the specific type.
- **Inference**: TypeScript infers generic parameters from arguments, reducing annotation overhead.
