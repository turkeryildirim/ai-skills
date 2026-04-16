---
title: Use Built-in and Custom Utility Types Over Manual Copies
impact: HIGH
impactDescription: Manually creating partial/readonly/pick variants duplicates interfaces and introduces subtle drift bugs.
tags: typescript, utility-types, partial, readonly, deep-types
---

# Use Built-in and Custom Utility Types Over Manual Copies

TypeScript provides built-in utility types for common transformations. For deeper needs, compose custom utility types like `DeepReadonly` and `DeepPartial`.

## Bad Example

```typescript
// Manually creating a partial version - must update when User changes
interface User {
  id: number;
  name: string;
  email: string;
  password: string;
}

interface PartialUser {
  id?: number;
  name?: string;
  email?: string;
  password?: string;
}

// Manually picking fields for an update DTO
interface UserUpdateDTO {
  name: string;
  email: string;
}

// Manually making nested config readonly - only one level deep
interface ReadonlyConfig {
  readonly server: {
    host: string;
    port: number;
    ssl: { enabled: boolean; cert: string };
  };
}
```

## Good Example

```typescript
interface User {
  id: number;
  name: string;
  email: string;
  password: string;
}

// Built-in utility types - always in sync
type PartialUser = Partial<User>;                    // All optional
type RequiredUser = Required<PartialUser>;           // All required again
type ReadonlyUser = Readonly<User>;                  // All readonly
type UserUpdateDTO = Pick<User, "name" | "email">;   // Only name + email
type UserWithoutPw = Omit<User, "password">;         // Everything except password
type UserRecord = Record<"home" | "about", User>;    // Map of Users

// Custom deep utility types for nested objects
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object
    ? T[P] extends Function
      ? T[P]
      : DeepReadonly<T[P]>
    : T[P];
};

type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object
    ? T[P] extends Array<infer U>
      ? Array<DeepPartial<U>>
      : DeepPartial<T[P]>
    : T[P];
};

interface Config {
  server: { host: string; port: number; ssl: { enabled: boolean; cert: string } };
}

type ReadonlyConfig = DeepReadonly<Config>;  // All nested properties readonly
type PartialConfig = DeepPartial<Config>;    // All nested properties optional
```

## Why

- **Zero drift**: Built-in utilities derive from the source type, so they update automatically.
- **Expressiveness**: `Pick<User, "name" | "email">` communicates intent clearly.
- **Deep recursion**: Custom `DeepReadonly` and `DeepPartial` handle nested objects that built-in types only touch one level deep.
- **Composability**: Utility types compose naturally: `Partial<Pick<User, "name" | "email">>`.
