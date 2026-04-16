---
title: Write API Integration Tests with Supertest
impact: HIGH
impactDescription: Unit tests alone cannot catch routing, middleware, auth, or status-code bugs in API endpoints.
tags: testing, integration, supertest, express, best-practices
---

# Write API Integration Tests with Supertest

Integration tests should exercise the full HTTP request lifecycle -- routing, middleware, validation, authentication, and response serialization -- using `supertest`.

## Bad Example

```typescript
// Only unit testing the handler function in isolation
describe("createUser handler", () => {
  it("creates a user", async () => {
    const req = { body: { name: "John", email: "john@test.com" } };
    const res = { status: vi.fn().mockReturnThis(), json: vi.fn() };

    await createUserHandler(req as any, res as any);

    expect(res.status).toHaveBeenCalledWith(201);
    // Misses: validation middleware, auth guard, JSON parsing, error formatter
  });
});
```

## Good Example

```typescript
import request from "supertest";
import { app } from "../../src/app";
import { pool } from "../../src/config/database";

describe("User API Integration Tests", () => {
  beforeAll(async () => {
    await pool.query("CREATE TABLE IF NOT EXISTS users (...)");
  });

  afterAll(async () => {
    await pool.query("DROP TABLE IF EXISTS users");
    await pool.end();
  });

  beforeEach(async () => {
    await pool.query("TRUNCATE TABLE users CASCADE");
  });

  describe("POST /api/users", () => {
    it("should create a new user and return 201", async () => {
      const response = await request(app)
        .post("/api/users")
        .send({ name: "John Doe", email: "john@example.com", password: "pass" })
        .expect(201);

      expect(response.body).toMatchObject({
        name: "John Doe",
        email: "john@example.com",
      });
      expect(response.body).toHaveProperty("id");
      expect(response.body).not.toHaveProperty("password");
    });

    it("should return 400 for invalid email", async () => {
      const response = await request(app)
        .post("/api/users")
        .send({ name: "John", email: "invalid", password: "pass" })
        .expect(400);

      expect(response.body).toHaveProperty("error");
    });

    it("should require authentication for protected routes", async () => {
      await request(app).get("/api/users/me").expect(401);
    });
  });
});
```

## Why

- **Benefit**: Supertest hits the real Express app stack, catching routing, middleware, and auth bugs that unit tests miss.
- **Benefit**: Proper `beforeAll`/`afterAll`/`beforeEach` lifecycle keeps the database schema stable while resetting data between tests.
- **Benefit**: Testing the full request lifecycle validates status codes, response shape, and error formatting end to end.
