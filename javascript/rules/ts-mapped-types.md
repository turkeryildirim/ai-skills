---
title: Use Mapped Types Over Manually Defined Variants
impact: HIGH
impactDescription: Manually defining readonly/partial/getter variants of interfaces creates duplication and drift from the source type.
tags: typescript, mapped-types, keyof, type-transformations
---

# Use Mapped Types Over Manually Defined Variants

Mapped types transform existing types programmatically using `keyof`, key remapping with `as`, and conditional filtering to produce derived types.

## Bad Example

```typescript
// Manually defining a readonly version - must update when User changes
interface User {
  id: number;
  name: string;
  email: string;
}

interface ReadonlyUser {
  readonly id: number;
  readonly name: string;
  readonly email: string;
}

// Manually defining getters - drifts when properties are added
interface UserGetters {
  getName: () => string;
  getEmail: () => string;
}

// Manually picking number fields from a mixed interface
interface Mixed {
  id: number;
  name: string;
  age: number;
  active: boolean;
}

interface OnlyNumbers {
  id: number;
  age: number;
}
```

## Good Example

```typescript
interface User {
  id: number;
  name: string;
  email: string;
}

// Mapped type - always stays in sync with User
type ReadonlyUser = {
  readonly [K in keyof User]: User[K];
};

// Key remapping with `as` to generate getter names
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

type UserGetters = Getters<User>;
// { getName: () => string; getEmail: () => string }

// Filter properties by type - no manual listing needed
type PickByType<T, U> = {
  [K in keyof T as T[K] extends U ? K : never]: T[K];
};

interface Mixed {
  id: number;
  name: string;
  age: number;
  active: boolean;
}

type OnlyNumbers = PickByType<Mixed, number>;
// { id: number; age: number }
```

## Why

- **Single source of truth**: Mapped types derive from the base type, so they update automatically when properties change.
- **Key remapping**: The `as` clause renames keys dynamically, enabling patterns like getter/setter generation.
- **Filtering**: Conditional `as` expressions let you include or exclude properties by type, name pattern, or any criterion.
- **DRY**: One mapped type replaces N manually maintained variants.
