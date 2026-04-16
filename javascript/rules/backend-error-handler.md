---
title: Centralized Error Handler Middleware
impact: HIGH
impactDescription: Try/catch in every controller method is repetitive and easy to forget, causing unhandled promise rejections.
tags: error-handling, middleware, express
---

# Centralized Error Handler Middleware

Use a global error handler middleware paired with an `asyncHandler` wrapper so that route handlers never need their own try/catch blocks.

## Bad Example

```typescript
// Every method wraps logic in try/catch — easy to forget
export class UserController {
  async createUser(req: Request, res: Response, next: NextFunction) {
    try {
      const user = await this.userService.createUser(req.body);
      res.status(201).json(user);
    } catch (error) {
      next(error);
    }
  }

  async getUser(req: Request, res: Response, next: NextFunction) {
    try {
      const user = await this.userService.getUserById(req.params.id);
      res.json(user);
    } catch (error) {
      // Oops — forgot next(error), error is swallowed
      res.status(500).json({ error: "Something went wrong" });
    }
  }

  async deleteUser(req: Request, res: Response, next: NextFunction) {
    // Forgot try/catch entirely — unhandled promise rejection crashes the process
    const result = await this.userService.deleteUser(req.params.id);
    res.status(204).send();
  }
}
```

## Good Example

```typescript
// middleware/error-handler.ts — one place for all error responses
export const errorHandler = (
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction,
) => {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      status: "error",
      message: err.message,
      ...(err instanceof ValidationError && { errors: err.errors }),
    });
  }

  logger.error({ error: err.message, stack: err.stack, url: req.url, method: req.method });

  const message = process.env.NODE_ENV === "production"
    ? "Internal server error"
    : err.message;

  res.status(500).json({ status: "error", message });
};

// asyncHandler eliminates try/catch from every handler
export const asyncHandler = (
  fn: (req: Request, res: Response, next: NextFunction) => Promise<any>,
) => {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};

// Controllers are now clean — no try/catch needed
export class UserController {
  async createUser(req: Request, res: Response) {
    const user = await this.userService.createUser(req.body);
    res.status(201).json(user);
  }

  async getUser(req: Request, res: Response) {
    const user = await this.userService.getUserById(req.params.id);
    res.json(user);
  }
}

// Route wiring
router.post("/users", asyncHandler(controller.createUser));
router.get("/users/:id", asyncHandler(controller.getUser));

app.use(errorHandler); // must be registered last
```

## Why

- **Benefit**: A single error handler guarantees consistent error response shapes across every endpoint, even for unexpected exceptions.
- **Benefit**: `asyncHandler` catches rejected promises automatically, so forgetting a try/catch never causes an unhandled rejection crash.
- **Benefit**: Controllers become shorter and focused on the happy path, while logging and status-code mapping live in one maintainable place.
