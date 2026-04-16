---
title: Test React Hooks with renderHook and act
impact: MEDIUM
impactDescription: Manually rendering dummy components to test hooks is verbose, error-prone, and misses state update timing.
tags: testing, react, hooks, testing-library, vitest, best-practices
---

# Test React Hooks with renderHook and act

Use `renderHook` and `act` from Testing Library to test custom hooks. This handles React's rendering cycle correctly and avoids manual dummy component setup.

## Bad Example

```typescript
// Manually rendering a dummy component to test a hook
function DummyComponent({ initialValue }: { initialValue?: number }) {
  const { count, increment, reset } = useCounter(initialValue);
  return (
    <div data-testid="count">{count}</div>
    <button data-testid="increment" onClick={increment}>+</button>
    <button data-testid="reset" onClick={reset}>Reset</button>
  );
}

it("increments count", () => {
  render(<DummyComponent />);
  fireEvent.click(screen.getByTestId("increment"));

  // Fragile: reads from DOM instead of accessing hook return value
  expect(screen.getByTestId("count").textContent).toBe("1");
});

// Calling hook outside a component
it("returns initial count", () => {
  const { count } = useCounter(5); // Error: hooks can only be called inside a component
  expect(count).toBe(5);
});
```

## Good Example

```typescript
import { renderHook, act } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { useCounter } from "./useCounter";

describe("useCounter", () => {
  it("should initialize with default value", () => {
    const { result } = renderHook(() => useCounter());

    expect(result.current.count).toBe(0);
  });

  it("should initialize with custom value", () => {
    const { result } = renderHook(() => useCounter(10));

    expect(result.current.count).toBe(10);
  });

  it("should increment count", () => {
    const { result } = renderHook(() => useCounter());

    act(() => {
      result.current.increment();
    });

    expect(result.current.count).toBe(1);
  });

  it("should reset to initial value", () => {
    const { result } = renderHook(() => useCounter(10));

    act(() => {
      result.current.increment();
      result.current.increment();
    });

    act(() => {
      result.current.reset();
    });

    expect(result.current.count).toBe(10);
  });
});
```

## Why

- **Benefit**: `renderHook` wraps the hook in a proper React component, avoiding "hooks can only be called inside a component" errors.
- **Benefit**: `act` ensures all state updates are flushed before assertions, preventing stale reads and act warnings.
- **Benefit**: Direct access to `result.current` is cleaner and less fragile than reading hook values from the DOM.
