---
title: Use Template Literal Types Over Manual String Unions
impact: MEDIUM
impactDescription: Manually listing all derived string literals is fragile and misses the connection to the source union.
tags: typescript, template-literals, string-manipulation, types
---

# Use Template Literal Types Over Manual String Unions

Template literal types combine and transform string literal unions programmatically, keeping derived types in sync with their source.

## Bad Example

```typescript
// Manually listing event handler names - must update when events change
type EventName = "click" | "focus" | "blur";
type EventHandler = "onClick" | "onFocus" | "onBlur";

// Manually listing all dot-notation paths for a config object
interface Config {
  server: {
    host: string;
    port: number;
  };
  database: {
    url: string;
  };
}

// Any of these could be missed or misspelled
type ConfigPath =
  | "server"
  | "database"
  | "server.host"
  | "server.port"
  | "database.url";
```

## Good Example

```typescript
// Template literal types derive handler names automatically
type EventName = "click" | "focus" | "blur";
type EventHandler = `on${Capitalize<EventName>}`;
// Type: "onClick" | "onFocus" | "onBlur"

// Built-in string manipulation types
type Upper = Uppercase<"hello">;       // "HELLO"
type Lower = Lowercase<"HELLO">;       // "hello"
type Cap = Capitalize<"john">;         // "John"
type Uncap = Uncapitalize<"John">;     // "john"

// Recursive path building - always complete and in sync
type Path<T> = T extends object
  ? {
      [K in keyof T]: K extends string
        ? `${K}` | `${K}.${Path<T[K]>}`
        : never;
    }[keyof T]
  : never;

interface Config {
  server: { host: string; port: number };
  database: { url: string };
}

type ConfigPath = Path<Config>;
// Type: "server" | "database" | "server.host" | "server.port" | "database.url"
```

## Why

- **Automatic derivation**: Adding `"hover"` to `EventName` automatically adds `"onHover"` to `EventHandler`.
- **String manipulation**: Built-in `Capitalize`, `Uppercase`, `Lowercase`, `Uncapitalize` transform literal strings at the type level.
- **Recursive construction**: Path types recurse into nested objects, generating every valid dot-notation path without manual listing.
- **Compile-time safety**: Misspelled or missing paths become impossible.
