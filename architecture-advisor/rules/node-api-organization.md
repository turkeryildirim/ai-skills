---
title: Node.js API Organization and Middleware Analysis
impact: HIGH
impactDescription: "Missing validation, error handling, and security middleware creates exploitable APIs"
tags: node, api, middleware, validation, error-handling, security, helmet
---

## Node.js API Organization and Middleware Analysis

**Impact: HIGH (Missing validation, error handling, and security middleware creates exploitable APIs)**

A well-organized Node.js API has a predictable middleware stack, consistent error responses, validated inputs, and security headers on every response. When these are absent or inconsistently applied, the API is both unreliable and insecure.

## Incorrect

```typescript
// ❌ No global error handler — each route catches differently

app.post('/users', async (req, res) => {
    try {
        const user = await UserService.create(req.body);
        res.json(user);
    } catch (e) {
        res.status(500).send(e.message); // ❌ Leaks internal error message
    }
});

app.get('/orders', async (req, res) => {
    const orders = await OrderService.list(); // ❌ No try/catch at all
    res.json(orders);
});

app.delete('/products/:id', async (req, res) => {
    try {
        await ProductService.delete(req.params.id);
        res.json({ ok: true }); // ❌ Inconsistent response shape
    } catch (e) {
        console.log(e);
        res.sendStatus(500); // ❌ Different error format again
    }
});
```

```typescript
// ❌ No input validation — trusting req.body directly

app.post('/users', async (req, res) => {
    // ❌ req.body.email could be undefined, an array, or a SQL injection string
    const user = await db.query(
        `INSERT INTO users (email) VALUES ('${req.body.email}')` // ❌ SQL injection
    );
    res.json(user);
});
```

## Correct

```typescript
// ✅ Proper middleware stack — ordered and consistent

import express from 'express';
import helmet from 'helmet';           // ✅ Security headers
import cors from 'cors';              // ✅ CORS configuration
import rateLimit from 'express-rate-limit'; // ✅ Rate limiting

const app = express();

// ✅ Security middleware first
app.use(helmet());
app.use(cors({ origin: process.env.ALLOWED_ORIGINS?.split(',') }));
app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 100 }));

// ✅ Body parsing with size limits
app.use(express.json({ limit: '10kb' })); // Prevent large payload attacks

// ✅ Routes
app.use('/v1/users', userRoutes);
app.use('/v1/orders', orderRoutes);

// ✅ Global error handler — LAST middleware
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
    const status = err instanceof AppError ? err.statusCode : 500;
    const message = err instanceof AppError ? err.message : 'Internal Server Error';

    // ✅ Never leak stack traces to clients
    res.status(status).json({
        error: {
            code: err instanceof AppError ? err.code : 'INTERNAL_ERROR',
            message,
            request_id: req.id, // ✅ Traceable
        }
    });

    if (status === 500) {
        logger.error(err); // Log full error server-side only
    }
});
```

```typescript
// ✅ Input validation with Zod on every write endpoint

import { z } from 'zod';

const CreateUserSchema = z.object({
    email: z.string().email(),
    name: z.string().min(1).max(100),
    role: z.enum(['admin', 'user']),
});

// ✅ Validation middleware
function validateBody(schema: ZodSchema) {
    return (req: Request, res: Response, next: NextFunction) => {
        const result = schema.safeParse(req.body);
        if (!result.success) {
            return res.status(422).json({
                error: { code: 'VALIDATION_ERROR', details: result.error.issues }
            });
        }
        req.body = result.data; // ✅ Typed and sanitized
        next();
    };
}

router.post('/users', validateBody(CreateUserSchema), UserController.create);
```

## Middleware Stack Checklist

```
Security:
[ ] helmet() installed and active
[ ] CORS configured with explicit origin allowlist (not *)
[ ] Rate limiting applied (at minimum to auth endpoints)
[ ] Body size limits set (express.json({ limit: '10kb' }))
[ ] Request ID middleware for tracing

Validation:
[ ] All POST/PUT/PATCH endpoints have input validation middleware
[ ] Validation library used (Zod, Joi, class-validator) — not manual if/else
[ ] Path params validated (req.params.id is a valid UUID, not arbitrary string)

Error Handling:
[ ] One global error handler registered as last middleware
[ ] Typed error classes (AppError extends Error with statusCode)
[ ] Stack traces NEVER returned to client (only logged server-side)
[ ] Consistent error response shape across all endpoints

API Organization:
[ ] Routes versioned (/v1/, /v2/ or header-based)
[ ] Route files organized by resource (userRoutes, orderRoutes — not one giant routes.ts)
[ ] Auth middleware applied per-router, not copy-pasted per-route
```

## Why

- **Security**: Missing Helmet allows clickjacking, XSS via headers; unvalidated input enables injection attacks
- **Debuggability**: Global error handler with request IDs makes tracing production errors possible
- **Consistency**: Clients can rely on one error shape — not guess between `{error}`, `{message}`, and bare status codes
