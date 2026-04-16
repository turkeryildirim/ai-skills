---
title: Use Optional Chaining and Nullish Coalescing
impact: MEDIUM
impactDescription: Verbose null guards and || for defaults silently break on falsy values like 0 and ""
tags: es6, optional-chaining, nullish-coalescing, safety
---

# Use Optional Chaining and Nullish Coalescing

Replace verbose chained `&&` checks with `?.` and replace `||` defaults with `??` to avoid silently discarding falsy values like `0` and `""`.

## Bad Example

```javascript
// Verbose and repetitive null checking
const city = user && user.address && user.address.city;

// Throws if user is null/undefined
const zip = user.address.zipCode;

// || discards valid falsy values — count of 0 becomes "N/A"
const displayCount = response.count || "N/A";

// || turns empty string into "Unknown"
const displayName = user.name || "Unknown";

// Manual existence check before method call
let result;
if (obj && obj.method) {
  result = obj.method();
}

// Manual default assignment
let port = config.port;
if (port === null || port === undefined) {
  port = 3000;
}
```

## Good Example

```javascript
// Optional chaining — short-circuits to undefined
const city = user?.address?.city;

// Optional chaining with array index
const first = items?.[0];

// Optional chaining with method call
const result = obj.method?.();

// Nullish coalescing — only triggers on null/undefined, not 0 or ""
const displayCount = response.count ?? "N/A";   // 0 stays as 0
const displayName = user.name ?? "Unknown";     // "" stays as ""
const port = config.port ?? 3000;

// Combined: safe navigation with default
const zip = user?.address?.zipCode ?? "00000";

// Logical assignment — assign default only if null/undefined
config.port ??= 3000;    // assign if null/undefined
config.host ??= "localhost";

// || vs ?? — choose intentionally
const enabled = flags.enabled || true;   // false becomes true (usually wrong)
const enabled2 = flags.enabled ?? true;  // false stays false (usually right)
```

## Why

- **Safety**: `?.` prevents "Cannot read property of undefined" crashes without verbose guard clauses. It short-circuits safely to `undefined`.
- **Correctness**: `??` only triggers on `null`/`undefined`, so valid falsy values like `0`, `""`, and `false` are preserved — unlike `||` which replaces them.
- **Readability**: `user?.address?.city ?? "unknown"` is one line vs three lines of `if` checks, and the intent is immediately clear.
