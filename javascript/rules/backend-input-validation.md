---
title: Schema-Based Input Validation
impact: CRITICAL
impactDescription: Manual validation checks are incomplete, scattered, and let malformed data reach business logic.
tags: validation, zod, security, express
---

# Schema-Based Input Validation

Use Zod schemas with a validation middleware to validate body, query, and params at the API boundary instead of scattering manual checks across handlers.

## Bad Example

```typescript
// Manual, incomplete, error-prone validation in every handler
router.post("/users", async (req, res) => {
  const { name, email, password, age } = req.body;

  if (!name) return res.status(400).json({ error: "Name is required" });
  if (!email) return res.status(400).json({ error: "Email is required" });
  if (!email.includes("@")) return res.status(400).json({ error: "Invalid email" });
  if (!password) return res.status(400).json({ error: "Password is required" });
  if (password.length < 8) return res.status(400).json({ error: "Password too short" });
  // Forgot to validate age type — a string slips through

  const user = await userService.createUser(req.body);
  res.status(201).json(user);
});

router.get("/users/:id", async (req, res) => {
  // No params validation — any string accepted as id
  const user = await userService.getUserById(req.params.id);
  res.json(user);
});
```

## Good Example

```typescript
// middleware/validation.middleware.ts — reusable for any schema
export const validate = (schema: AnyZodObject) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      await schema.parseAsync({
        body: req.body,
        query: req.query,
        params: req.params,
      });
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const errors = error.errors.map((err) => ({
          field: err.path.join("."),
          message: err.message,
        }));
        next(new ValidationError("Validation failed", errors));
      } else {
        next(error);
      }
    }
  };
};

// schemas — single source of truth for shape and constraints
const createUserSchema = z.object({
  body: z.object({
    name: z.string().min(1, "Name is required"),
    email: z.string().email("Invalid email format"),
    password: z.string().min(8, "Password must be at least 8 characters"),
    age: z.number().int().min(0).optional(),
  }),
});

const getUserSchema = z.object({
  params: z.object({ id: z.string().uuid("Invalid user ID") }),
});

// routes — validation is a one-liner
router.post("/users", validate(createUserSchema), userController.createUser);
router.get("/users/:id", validate(getUserSchema), userController.getUser);
```

## Why

- **Benefit**: Schemas act as a single source of truth for input shape -- the same schema can generate Swagger docs or shared client types.
- **Benefit**: Every field is validated consistently, with clear error messages returned in a uniform structure that clients can parse.
- **Benefit**: Malformed or malicious data is rejected at the middleware layer before it ever reaches business logic or database queries.
