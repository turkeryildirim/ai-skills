---
title: Custom Error Class Hierarchy
impact: HIGH
impactDescription: Generic Error objects carry no HTTP status code, forcing handlers to guess response codes.
tags: error-handling, express, typescript
---

# Custom Error Class Hierarchy

Define an `AppError` base class with a `statusCode` property and create specific subclasses so that every error carries its own HTTP status and the error handler can respond correctly.

## Bad Example

```typescript
// Generic errors — no status code, no structure
export class UserService {
  async getUserById(id: string) {
    const user = await this.userRepo.findById(id);
    if (!user) throw new Error("User not found");           // 404? 500? Caller must decide.
    return user;
  }

  async createUser(data: CreateUserDTO) {
    const existing = await this.userRepo.findByEmail(data.email);
    if (existing) throw new Error("Email already exists");   // 409? 400? Who knows.
    return this.userRepo.create(data);
  }

  async adminAction(userId: string) {
    const user = await this.getUserById(userId);
    if (!user.isAdmin) throw new Error("Not allowed");       // 403? 401? Ambiguous.
  }
}
```

## Good Example

```typescript
// utils/errors.ts — structured hierarchy
export class AppError extends Error {
  constructor(
    public message: string,
    public statusCode: number = 500,
    public isOperational: boolean = true,
  ) {
    super(message);
    Object.setPrototypeOf(this, AppError.prototype);
    Error.captureStackTrace(this, this.constructor);
  }
}

export class ValidationError extends AppError {
  constructor(message: string, public errors?: any[]) {
    super(message, 400);
  }
}

export class NotFoundError extends AppError {
  constructor(message: string = "Resource not found") {
    super(message, 404);
  }
}

export class UnauthorizedError extends AppError {
  constructor(message: string = "Unauthorized") {
    super(message, 401);
  }
}

export class ForbiddenError extends AppError {
  constructor(message: string = "Forbidden") {
    super(message, 403);
  }
}

export class ConflictError extends AppError {
  constructor(message: string) {
    super(message, 409);
  }
}

// Usage — status code travels with the error
async getUserById(id: string) {
  const user = await this.userRepo.findById(id);
  if (!user) throw new NotFoundError("User not found");
  return user;
}
```

## Why

- **Benefit**: Every thrown error carries its HTTP status code, so the centralized error handler can respond correctly without inspecting error messages.
- **Benefit**: `isOperational` distinguishes expected business errors from unexpected programming bugs, letting you alert only on the latter.
- **Benefit**: Subclass names like `NotFoundError` and `ConflictError` make throw sites self-documenting -- readers immediately understand intent.
