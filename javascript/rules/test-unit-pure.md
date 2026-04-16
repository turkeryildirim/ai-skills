---
title: Test Unit Pure Functions and Classes Correctly
impact: HIGH
impactDescription: Tests that rely on shared state or probe private internals break on refactors and give false confidence.
tags: testing, unit-test, vitest, jest, best-practices
---

# Test Unit Pure Functions and Classes Correctly

Unit tests should verify public behavior through the Arrange-Act-Assert pattern, using fresh instances per test and avoiding shared mutable state.

## Bad Example

```typescript
// Shared mutable instance leaks state between tests
let service: UserService;

// Created once for the entire describe block
service = new UserService();

it("creates a user", () => {
  service.create({ id: "1", name: "John" });
  // State persists to next test!
});

it("finds the user", () => {
  // Passes only because previous test left data behind
  expect(service.findById("1")).toBeDefined();
});

// Testing private internals instead of public API
it("stores in internal map", () => {
  expect((service as any).users.size).toBe(1);
});
```

## Good Example

```typescript
describe("UserService", () => {
  let service: UserService;

  // Fresh instance before every test - no leaked state
  beforeEach(() => {
    service = new UserService();
  });

  describe("create", () => {
    it("should create a new user", () => {
      // Arrange
      const user = { id: "1", name: "John", email: "john@example.com" };

      // Act
      const created = service.create(user);

      // Assert - only public API
      expect(created).toEqual(user);
      expect(service.findById("1")).toEqual(user);
    });

    it("should throw error if user already exists", () => {
      const user = { id: "1", name: "John", email: "john@example.com" };
      service.create(user);

      expect(() => service.create(user)).toThrow("User already exists");
    });
  });
});
```

## Why

- **Benefit**: Fresh instances in `beforeEach` eliminate test-order dependency and flaky failures caused by leaked state.
- **Benefit**: Testing only the public API means tests survive internal refactors without breaking.
- **Benefit**: The AAA (Arrange-Act-Assert) structure makes each test's purpose immediately clear to readers.
