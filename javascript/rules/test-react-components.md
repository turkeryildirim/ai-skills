---
title: Test React Components with Testing Library
impact: MEDIUM
impactDescription: Testing implementation details or using shallow rendering hides real user-facing bugs.
tags: testing, react, testing-library, vitest, best-practices
---

# Test React Components with Testing Library

Test user-visible behavior with semantic queries (`getByRole`, `getByPlaceholderText`) and `fireEvent`. Avoid testing internal state or using shallow rendering.

## Bad Example

```typescript
import { shallow } from "enzyme";

it("manages name state", () => {
  const wrapper = shallow(<UserForm onSubmit={vi.fn()} />);

  // Testing internal state - breaks on any refactor
  expect(wrapper.state("name")).toBe("");

  wrapper.find("input").first().simulate("change", {
    target: { value: "John" },
  });
  expect(wrapper.state("name")).toBe("John");
});

// Using data-testid when a semantic query exists
it("has email input", () => {
  render(<UserForm onSubmit={vi.fn()} />);
  expect(screen.getByTestId("email-input")).toBeInTheDocument();
});
```

## Good Example

```typescript
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { UserForm } from "./UserForm";

describe("UserForm", () => {
  it("should render form inputs", () => {
    render(<UserForm onSubmit={vi.fn()} />);

    // Semantic queries reflect how users find elements
    expect(screen.getByPlaceholderText("Name")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Email")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Submit" })).toBeInTheDocument();
  });

  it("should call onSubmit with form data", () => {
    const onSubmit = vi.fn();
    render(<UserForm onSubmit={onSubmit} />);

    // Simulate real user interactions
    fireEvent.change(screen.getByPlaceholderText("Name"), {
      target: { value: "John Doe" },
    });
    fireEvent.change(screen.getByPlaceholderText("Email"), {
      target: { value: "john@example.com" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Submit" }));

    expect(onSubmit).toHaveBeenCalledWith({
      name: "John Doe",
      email: "john@example.com",
    });
  });
});
```

## Why

- **Benefit**: Semantic queries (`getByRole`, `getByPlaceholderText`) mirror how real users interact, so tests catch actual UX breakage.
- **Benefit**: Testing user-visible behavior instead of internal state means tests survive refactors of state management.
- **Benefit**: Testing Library's full render catches composition bugs that shallow rendering silently hides.
