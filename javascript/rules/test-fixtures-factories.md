---
title: Use Fixture Factories for Test Data
impact: HIGH
impactDescription: Hardcoded test data scattered across files makes tests brittle and hard to update when schemas change.
tags: testing, fixtures, faker, vitest, jest, best-practices
---

# Use Fixture Factories for Test Data

Generate test data with factory functions powered by `@faker-js/faker` and an `overrides` parameter. Avoid hardcoding values in every test.

## Bad Example

```typescript
// Every test repeats the same hardcoded object
it("creates a user", async () => {
  const user = { id: "1", name: "John", email: "john@example.com", createdAt: new Date() };
  await service.create(user);
});

it("finds a user", async () => {
  const user = { id: "2", name: "Jane", email: "jane@example.com", createdAt: new Date() };
  await service.create(user);
  const found = await service.findById("2");
  expect(found.name).toBe("Jane");
});

// Changing the User schema means updating dozens of hardcoded objects

// Bulk data is manually written
it("lists users", async () => {
  const users = [
    { id: "1", name: "A", email: "a@b.com" },
    { id: "2", name: "B", email: "b@b.com" },
    { id: "3", name: "C", email: "c@b.com" },
  ];
});
```

## Good Example

```typescript
import { faker } from "@faker-js/faker";

// Factory function with faker + overrides
export function createUserFixture(overrides?: Partial<User>): User {
  return {
    id: faker.string.uuid(),
    name: faker.person.fullName(),
    email: faker.internet.email(),
    createdAt: faker.date.past(),
    ...overrides,
  };
}

// Bulk fixture generator
export function createUsersFixture(count: number): User[] {
  return Array.from({ length: count }, () => createUserFixture());
}

// In tests
describe("UserService", () => {
  it("should create a user", async () => {
    const user = createUserFixture();
    await service.create(user);
  });

  it("should find user by specific email", async () => {
    const user = createUserFixture({ email: "target@example.com" });
    await service.create(user);

    const found = await service.findByEmail("target@example.com");
    expect(found.name).toBe(user.name);
  });

  it("should list paginated users", async () => {
    const users = createUsersFixture(25);
    for (const u of users) await service.create(u);

    const page = await service.list({ page: 1, limit: 10 });
    expect(page).toHaveLength(10);
  });
});
```

## Why

- **Benefit**: Faker generates unique realistic data per test run, catching uniqueness-constraint and data-collision bugs.
- **Benefit**: The `overrides` parameter lets tests specify only the fields they care about, keeping test setup minimal and readable.
- **Benefit**: When the schema changes, you update one factory function instead of dozens of hardcoded objects.
