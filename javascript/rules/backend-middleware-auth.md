---
title: Reusable Auth Middleware
impact: HIGH
impactDescription: Manual token parsing in every route is error-prone and violates DRY.
tags: authentication, middleware, jwt, express
---

# Reusable Auth Middleware

Extract authentication and authorization into reusable middleware instead of duplicating JWT parsing and role checks across route handlers.

## Bad Example

```typescript
// Every route manually parses the token — easy to forget or get wrong
router.get("/profile", async (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ error: "Missing token" });

  try {
    const token = authHeader.replace("Bearer ", "");
    const payload = jwt.verify(token, "my-secret-key");
    const user = await pool.query("SELECT * FROM users WHERE id = $1", [payload.userId]);

    if (!user.rows[0]) return res.status(404).json({ error: "User not found" });
    res.json(user.rows[0]);
  } catch {
    res.status(401).json({ error: "Invalid token" });
  }
});

router.delete("/admin/users/:id", async (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ error: "Missing token" });

  try {
    const token = authHeader.replace("Bearer ", "");
    const payload = jwt.verify(token, "my-secret-key"); // duplicated logic
    if (payload.role !== "admin") return res.status(403).json({ error: "Forbidden" });
    // ... delete logic
  } catch {
    res.status(401).json({ error: "Invalid token" });
  }
});
```

## Good Example

```typescript
// middleware/auth.middleware.ts — written once, used everywhere
export const authenticate = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const token = req.headers.authorization?.replace("Bearer ", "");
    if (!token) throw new UnauthorizedError("No token provided");

    const payload = jwt.verify(token, process.env.JWT_SECRET!) as JWTPayload;
    req.user = payload;
    next();
  } catch {
    next(new UnauthorizedError("Invalid token"));
  }
};

export const authorize = (...roles: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) return next(new UnauthorizedError("Not authenticated"));
    if (!roles.some((role) => req.user?.roles?.includes(role))) {
      return next(new UnauthorizedError("Insufficient permissions"));
    }
    next();
  };
};

// routes — clean, declarative protection
router.get("/profile", authenticate, userController.getProfile);
router.delete("/admin/users/:id", authenticate, authorize("admin"), userController.deleteUser);
```

## Why

- **Benefit**: Auth logic is written once in middleware, eliminating copy-paste bugs and ensuring every protected route follows the same flow.
- **Benefit**: Route declarations become declarative -- `authenticate, authorize("admin")` reads as documentation of access requirements.
- **Benefit**: Changing token verification (e.g., rotating secrets, adding revocation) only requires editing the middleware, not dozens of handlers.
