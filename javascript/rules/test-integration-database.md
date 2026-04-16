---
title: Write Database Integration Tests with Cleanup
impact: MEDIUM
impactDescription: Shared test databases without cleanup cause test pollution; mocking the DB for all tests hides real SQL bugs.
tags: testing, integration, database, vitest, best-practices
---

# Write Database Integration Tests with Cleanup

Integration tests against a real database must truncate or roll back data between tests. Do not mock the database layer for every test -- let real SQL reveal constraint and query bugs.

## Bad Example

```typescript
// Shared database with no cleanup -- tests pollute each other
const repository = new UserRepository(pool);

it("creates a user", async () => {
  await repository.create({ email: "john@test.com", name: "John" });
  // Row stays in the DB forever
});

it("finds by email", async () => {
  // Might find the user from the previous test, or from a past run
  const user = await repository.findByEmail("john@test.com");
  expect(user).toBeDefined(); // flaky
});

// Over-mocking: never exercises real SQL
vi.mock("./user.repository");
it("creates a user", async () => {
  mockRepo.create.mockResolvedValue({ id: 1 });
  const user = await mockRepo.create({ email: "a@b.com" });
  expect(user.id).toBe(1); // proves nothing about real queries
});
```

## Good Example

```typescript
import { describe, it, expect, beforeAll, afterAll, beforeEach } from "vitest";
import { Pool } from "pg";
import { UserRepository } from "../../src/repositories/user.repository";

describe("UserRepository Integration Tests", () => {
  let pool: Pool;
  let repository: UserRepository;

  beforeAll(async () => {
    pool = new Pool({ host: "localhost", database: "test_db", user: "test_user" });
    repository = new UserRepository(pool);

    await pool.query(`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
  });

  afterAll(async () => {
    await pool.query("DROP TABLE IF EXISTS users");
    await pool.end();
  });

  // Clean slate before every test
  beforeEach(async () => {
    await pool.query("TRUNCATE TABLE users CASCADE");
  });

  it("should create a user", async () => {
    const user = await repository.create({
      name: "John Doe",
      email: "john@example.com",
      password: "hashed_password",
    });

    expect(user).toHaveProperty("id");
    expect(user.email).toBe("john@example.com");
  });

  it("should find user by email", async () => {
    await repository.create({
      name: "John Doe",
      email: "john@example.com",
      password: "hashed_password",
    });

    const user = await repository.findByEmail("john@example.com");
    expect(user?.name).toBe("John Doe");
  });

  it("should return null for missing email", async () => {
    const user = await repository.findByEmail("nobody@example.com");
    expect(user).toBeNull();
  });
});
```

## Why

- **Benefit**: `TRUNCATE ... CASCADE` in `beforeEach` guarantees every test starts with a clean database, eliminating test pollution.
- **Benefit**: Running real SQL against a test database catches constraint violations, typos in queries, and type mismatches that mocks hide.
- **Benefit**: `beforeAll`/`afterAll` lifecycle manages schema creation and teardown, keeping the test environment self-contained.
