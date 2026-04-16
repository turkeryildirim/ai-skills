---
title: Use Discriminated Unions Over Boolean Flags
impact: CRITICAL
impactDescription: Optional fields and boolean flags create impossible states and require defensive null checks everywhere.
tags: typescript, discriminated-unions, state-machines, exhaustive-switch
---

# Use Discriminated Unions Over Boolean Flags

Discriminated unions use a shared literal property to narrow types exhaustively, making invalid states unrepresentable.

## Bad Example

```typescript
// Boolean flags allow impossible states
interface ApiState<T> {
  data: T | null;
  error: string | null;
  isLoading: boolean;
}

// Impossible but legal: loading AND error AND data all set
const bad: ApiState<string> = {
  data: "result",
  error: "something failed",
  isLoading: true, // What is true here?
};

// Defensive null checks everywhere
function render(state: ApiState<User>) {
  if (state.isLoading) return "Loading...";
  if (state.error !== null) return state.error; // still nullable after check
  if (state.data !== null) return state.data.name; // still nullable
  return "No data";
}
```

## Good Example

```typescript
// Discriminated union - each state has exactly the right fields
type Success<T> = { status: "success"; data: T };
type Error = { status: "error"; error: string };
type Loading = { status: "loading" };

type AsyncState<T> = Success<T> | Error | Loading;

// Impossible states are not representable
const good: AsyncState<User> = { status: "loading" };
// Cannot access .data or .error here - compile error

// Exhaustive switch with automatic narrowing
function handleState<T>(state: AsyncState<T>): string {
  switch (state.status) {
    case "success":
      return state.data; // Type: T, no null check needed
    case "error":
      return state.error; // Type: string, no null check needed
    case "loading":
      return "Loading...";
  }
}

// Type-safe state machine with reducer
type State =
  | { type: "idle" }
  | { type: "fetching"; requestId: string }
  | { type: "success"; data: any }
  | { type: "error"; error: Error };

type Event =
  | { type: "FETCH"; requestId: string }
  | { type: "SUCCESS"; data: any }
  | { type: "ERROR"; error: Error }
  | { type: "RESET" };

function reducer(state: State, event: Event): State {
  switch (state.type) {
    case "idle":
      return event.type === "FETCH"
        ? { type: "fetching", requestId: event.requestId }
        : state;
    case "fetching":
      if (event.type === "SUCCESS") return { type: "success", data: event.data };
      if (event.type === "ERROR") return { type: "error", error: event.error };
      return state;
    case "success":
    case "error":
      return event.type === "RESET" ? { type: "idle" } : state;
  }
}
```

## Why

- **Impossible states eliminated**: Each variant carries only its relevant fields, so you cannot construct nonsensical combinations.
- **Exhaustive narrowing**: Switching on the discriminant narrows the type without null checks or type assertions.
- **State machines**: Discriminated unions model valid transitions naturally in reducers.
- **Refactoring safety**: Adding a new variant causes compile errors in every unchecked switch, ensuring completeness.
