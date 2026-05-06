---
name: node-architecture-guide
description: Node.js backend architecture patterns, layering benchmarks, middleware stack reference, and common anti-patterns for architectural analysis.
type: reference
---

# Node.js Architecture Guide

Reference for analyzing Node.js backend projects (Express, Fastify, NestJS, Hono).

## Maturity Levels

| Level | Signals |
|-------|---------|
| **Level 1** | All logic in `app.js`, no folder structure |
| **Level 2** | Route files, but business logic in route handlers |
| **Level 3** | Controller → Service → Repository separation |
| **Level 4** | Typed (TypeScript), dependency injection, centralized error handling |
| **Level 5** | DI container, queue workers, full test suite, graceful shutdown |

---

## Framework-Specific Assessment

### Express
```
✅ Healthy Express structure:
src/
├── app.ts              → Express instance, middleware registration
├── server.ts           → HTTP server, graceful shutdown
├── routes/             → Route definitions only
├── controllers/        → HTTP in/out
├── services/           → Business logic
├── repositories/       → Data access
├── middlewares/        → Auth, validation, error handling
├── config/             → Environment validation (zod)
└── types/              → TypeScript types/interfaces

⚠️ Watch for: no middleware structure, all in one app.js
```

### NestJS
```
✅ Healthy NestJS: follows module-per-feature pattern
src/
├── app.module.ts
├── orders/
│   ├── orders.module.ts
│   ├── orders.controller.ts   → HTTP only
│   ├── orders.service.ts      → Business logic
│   ├── orders.repository.ts   → Data access
│   └── dto/                   → DTOs with class-validator
├── users/
└── shared/

⚠️ Watch for: Services with >10 methods (God Service), 
              logic in controllers, no module separation
```

### Fastify
```
✅ Healthy Fastify: plugin-based structure
src/
├── server.ts           → Fastify instance + plugin registration
├── plugins/            → Fastify plugins (auth, db, redis)
├── routes/             → Route handlers (thin)
├── services/           → Business logic
└── schemas/            → JSON schemas (Fastify's native validation)
```

---

## Middleware Stack Order (Critical for Express)

```typescript
// ✅ Correct middleware order — MATTERS for security and functionality

app.use(helmet())                    // 1. Security headers — FIRST
app.use(cors(corsOptions))           // 2. CORS — before routes
app.use(express.json({ limit: '10kb' })) // 3. Body parsing with size limit
app.use(requestIdMiddleware())       // 4. Request ID for tracing
app.use(rateLimiter)                 // 5. Rate limiting

// 6. Routes
app.use('/v1', apiRoutes)

// 7. Error handler — LAST
app.use(globalErrorHandler)
```

---

## Environment Configuration Patterns

### ❌ Raw process.env (scattered access)
```typescript
// In service file:
const dbUrl = process.env.DATABASE_URL; // undefined if not set — silent failure
const maxRetries = parseInt(process.env.MAX_RETRIES || '3'); // no validation
```

### ✅ Validated config module (Zod)
```typescript
// src/config/index.ts — read and validate once at startup
import { z } from 'zod';

const schema = z.object({
    DATABASE_URL: z.string().url(),
    REDIS_URL: z.string().url(),
    JWT_SECRET: z.string().min(32),
    MAX_RETRIES: z.coerce.number().int().min(1).max(10).default(3),
    NODE_ENV: z.enum(['development', 'staging', 'production']).default('development'),
});

export const config = schema.parse(process.env);
// Throws at startup if required env vars are missing — fail fast
```

---

## Database Access Benchmarks

### ORM Selection Guide
| ORM | Best For | Avoid When |
|-----|----------|------------|
| **Prisma** | TypeScript projects, rapid development | Need fine-grained SQL control |
| **TypeORM** | Complex entity relationships, migrations | Simple CRUD (too much boilerplate) |
| **Drizzle** | TypeScript, SQL-first, type-safe queries | Teams unfamiliar with SQL |
| **Sequelize** | Legacy projects | New TypeScript projects |
| **Knex** | Query builder without full ORM | Need entity management |

### Connection Pool Benchmarks
```typescript
// ✅ Appropriate pool sizing
// Development: min 1, max 5
// Production: min 2, max (CPU_CORES * 2 + 1) — typically 9-17

const pool = new Pool({
    connectionString: config.DATABASE_URL,
    max: parseInt(process.env.DB_POOL_MAX || '10'),
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000,
});
```

---

## Error Handling Patterns

### Typed Error Classes
```typescript
// ✅ Domain errors extend AppError
export class AppError extends Error {
    constructor(
        public readonly message: string,
        public readonly statusCode: number,
        public readonly code: string,
    ) { super(message); }
}

export class NotFoundError extends AppError {
    constructor(resource: string) {
        super(`${resource} not found`, 404, 'NOT_FOUND');
    }
}

export class ValidationError extends AppError {
    constructor(details: unknown[]) {
        super('Validation failed', 422, 'VALIDATION_ERROR');
        this.details = details;
    }
}
```

---

## Common Anti-Patterns

| Anti-Pattern | Signs | Impact |
|-------------|-------|--------|
| **Fat Route Handler** | >30 lines, SQL in handler | Untestable, duplicated in workers |
| **Raw process.env** | `process.env.X` scattered in 20 files | Silent failures, no validation |
| **No global error handler** | Try/catch in every route | Inconsistent error shapes |
| **Synchronous I/O in handlers** | `fs.readFileSync` in request path | Event loop blocking |
| **No request timeout** | Handlers can run forever | Slow endpoints drain connections |
| **Long task inline** | >2s operations in request handler | HTTP timeout, no retry on failure |
| **Missing graceful shutdown** | No SIGTERM handler | In-flight requests dropped on deploy |
