---
title: Type-Safe Builder Over Unchecked build() Calls
impact: MEDIUM
impactDescription: A builder that allows build() without required fields produces partial objects that crash at runtime.
tags: typescript, builder-pattern, conditional-types, generics, pattern
---

# Type-Safe Builder Over Unchecked build() Calls

A generic Builder that tracks which fields have been set can prevent `build()` from being called until all required fields are provided, using conditional types for compile-time completeness checks.

## Bad Example

```typescript
// Builder accepts build() at any time - required fields may be missing
class UserBuilder {
  private id?: string;
  private name?: string;
  private email?: string;
  private age?: number;

  setId(id: string) { this.id = id; return this; }
  setName(name: string) { this.name = name; return this; }
  setEmail(email: string) { this.email = email; return this; }
  setAge(age: number) { this.age = age; return this; }

  build(): User {
    // Runtime crash if required fields are missing
    if (!this.id || !this.name || !this.email) {
      throw new Error("Missing required fields");
    }
    return { id: this.id, name: this.name, email: this.email, age: this.age };
  }
}

// No compile error - bug surfaces only at runtime
const user = new UserBuilder()
  .setId("1")
  .build(); // throws: "Missing required fields"
```

## Good Example

```typescript
type BuilderState<T> = { [K in keyof T]: T[K] | undefined };

type RequiredKeys<T> = {
  [K in keyof T]-?: {} extends Pick<T, K> ? never : K;
}[keyof T];

type IsComplete<T, S> =
  RequiredKeys<T> extends keyof S
    ? S[RequiredKeys<T>] extends undefined
      ? false
      : true
    : false;

class Builder<T, S extends BuilderState<T> = {}> {
  private state: S = {} as S;

  set<K extends keyof T>(key: K, value: T[K]): Builder<T, S & Record<K, T[K]>> {
    this.state[key] = value;
    return this as any;
  }

  // Compile error if required fields are missing
  build(this: IsComplete<T, S> extends true ? this : never): T {
    return this.state as T;
  }
}

interface User {
  id: string;
  name: string;
  email: string;
  age?: number;
}

// OK: all required fields provided
const user = new Builder<User>()
  .set("id", "1")
  .set("name", "John")
  .set("email", "john@example.com")
  .set("age", 30) // optional field
  .build();

// Compile error: build() is not callable - missing required fields
// const incomplete = new Builder<User>()
//   .set("id", "1")
//   .build(); // Error: build cannot be called
```

## Why

- **Compile-time completeness**: The `IsComplete` conditional type makes `build()` uncallable until all required fields are set.
- **No runtime surprises**: Missing required fields are caught at compile time, not as thrown errors in production.
- **Optional fields respected**: Optional properties (like `age?: number`) do not block `build()`.
- **Fluent API preserved**: Each `set()` call returns the builder with an updated tracked state, preserving method chaining.
