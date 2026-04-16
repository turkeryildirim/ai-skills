---
title: Consistent API Response Envelope
impact: MEDIUM
impactDescription: Inconsistent response shapes force every client to handle different formats per endpoint.
tags: api, response-format, express
---

# Consistent API Response Envelope

Use an `ApiResponse` helper class that always returns `{ status, message?, data?, pagination? }` so every endpoint speaks the same structure.

## Bad Example

```typescript
// Every endpoint returns a different shape
router.get("/users", async (req, res) => {
  const users = await userService.listUsers();
  res.json(users); // bare array — no metadata
});

router.post("/users", async (req, res) => {
  const user = await userService.createUser(req.body);
  res.status(201).json({ user, message: "Created" }); // { user, message }
});

router.get("/users/:id", async (req, res) => {
  const user = await userService.getUserById(req.params.id);
  res.json({ data: user }); // { data }
});

router.get("/products", async (req, res) => {
  const products = await productService.list(req.query.page);
  res.json({ items: products, total: 100 }); // { items, total }
});
```

## Good Example

```typescript
// utils/response.ts — single envelope for all responses
import { Response } from "express";

export class ApiResponse {
  static success<T>(res: Response, data: T, message?: string, statusCode = 200) {
    return res.status(statusCode).json({
      status: "success",
      ...(message && { message }),
      data,
    });
  }

  static error(res: Response, message: string, statusCode = 500, errors?: any) {
    return res.status(statusCode).json({
      status: "error",
      message,
      ...(errors && { errors }),
    });
  }

  static paginated<T>(
    res: Response,
    data: T[],
    page: number,
    limit: number,
    total: number,
  ) {
    return res.json({
      status: "success",
      data,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit),
      },
    });
  }
}

// Controllers use the same envelope everywhere
async listUsers(req: Request, res: Response) {
  const { page, limit } = req.query;
  const { users, total } = await this.userService.list(page, limit);
  return ApiResponse.paginated(res, users, Number(page), Number(limit), total);
}

async createUser(req: Request, res: Response) {
  const user = await this.userService.createUser(req.body);
  return ApiResponse.success(res, user, "User created", 201);
}

async getUser(req: Request, res: Response) {
  const user = await this.userService.getUserById(req.params.id);
  return ApiResponse.success(res, user);
}
```

## Why

- **Benefit**: Clients parse one predictable envelope (`status`, `data`, `pagination`) instead of guessing the shape per endpoint.
- **Benefit**: Paginated responses include `pages` and `total`, letting UI components render page controls without extra requests.
- **Benefit**: Error and success responses follow the same top-level structure, simplifying client-side error interceptors and type definitions.
