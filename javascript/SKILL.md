---
name: javascript
description: Expert JavaScript & TypeScript skill for modern Backend (Node.js), Advanced Testing, TypeScript Type Systems, and ES6+ Patterns. Use for building scalable Node.js services, writing robust Vitest/Jest suites, or designing complex TypeScript type logic.
license: MIT
metadata:
  version: "3.0.0"
---

# JavaScript & TypeScript Best Practices

Modern JavaScript & TypeScript patterns for backend development, testing, advanced types, and ES6+ features. Contains 43 rules organized into 7 categories.

## When to Apply

Reference these guidelines when:
- Building REST APIs, GraphQL servers, or microservices with Node.js
- Writing or reviewing TypeScript code with advanced types
- Setting up test infrastructure (unit, integration, E2E)
- Refactoring legacy JS to modern ES6+ syntax
- Implementing authentication, validation, and middleware patterns

## Rule Categories by Priority

| Priority | Category | Impact | Prefix | Rules |
|----------|----------|--------|--------|-------|
| 1 | TypeScript Types | CRITICAL | `ts-` | 10 |
| 2 | Async Patterns | CRITICAL | `async-` | 2 |
| 3 | Backend Architecture | HIGH | `backend-` | 13 |
| 4 | Testing | HIGH | `test-` | 10 |
| 5 | Functional Programming | HIGH | `func-` | 3 |
| 6 | ES6+ Features | MEDIUM | `es-` | 4 |
| 7 | Performance | MEDIUM | `perf-` | 1 |

## Quick Reference

### 1. TypeScript Types (CRITICAL) - 10 rules

- `ts-generics` - Generic constraints and reusability over `any` and duplicated functions
- `ts-conditional-types` - Conditional types with `infer` over manual runtime checks
- `ts-mapped-types` - Mapped types with key remapping over manual variants
- `ts-template-literal-types` - Template literal types over manual string unions
- `ts-utility-types` - Built-in + Deep utility types over manual copies
- `ts-discriminated-unions` - Discriminated unions over boolean flags and optional fields
- `ts-type-guards` - Type guards and assertions over `as` casts
- `ts-pattern-event-emitter` - Typed EventEmitter over stringly-typed events
- `ts-pattern-api-client` - Type-safe API client over untyped fetch
- `ts-pattern-builder` - Type-safe builder over unchecked build() calls

### 2. Async Patterns (CRITICAL) - 2 rules

- `async-promise-combinators` - Promise.all/allSettled/race/any over sequential awaits
- `async-await-patterns` - try/catch + parallel + retry + timeout over unhandled rejections

### 3. Backend Architecture (HIGH) - 13 rules

- `backend-layered-architecture` - Controller/Service/Repository over logic in routes
- `backend-dependency-injection` - DI container over hardcoded `new`
- `backend-middleware-auth` - Reusable auth middleware over manual token parsing
- `backend-input-validation` - Zod schema validation over manual `if` checks
- `backend-rate-limiting` - Redis-backed rate limiting over no protection
- `backend-custom-errors` - AppError hierarchy over generic `throw new Error()`
- `backend-error-handler` - Global error handler + asyncHandler over try/catch everywhere
- `backend-database-transactions` - BEGIN/COMMIT/ROLLBACK over unprotected operations
- `backend-jwt-auth` - bcrypt + access/refresh tokens over plaintext passwords
- `backend-redis-caching` - CacheService + @Cacheable over always hitting DB
- `backend-api-response` - ApiResponse envelope over inconsistent shapes
- `backend-graceful-shutdown` - SIGTERM handlers over abrupt exit
- `backend-structured-logging` - Pino structured logging over console.log

### 4. Testing (HIGH) - 10 rules

- `test-unit-pure` - AAA pattern + fresh instances over testing implementation details
- `test-async-functions` - resolves/rejects + fake timers over missing await
- `test-mocking-modules` - vi.mock() factories over hitting real services
- `test-di-mocking` - Interface-based DI mocks over vi.mock for everything
- `test-spying-fakes` - vi.spyOn + fake timers over uncontrolled globals
- `test-integration-api` - Supertest HTTP tests over unit-only API testing
- `test-integration-database` - TRUNCATE/rollback cleanup over shared dirty DB
- `test-react-components` - Semantic queries (getByRole) over implementation details
- `test-react-hooks` - renderHook + act over manual wrapper components
- `test-fixtures-factories` - Faker factories over hardcoded test data

### 5. Functional Programming (HIGH) - 3 rules

- `func-array-methods` - map/filter/reduce chaining over for loops
- `func-composition` - pipe/compose + memoization over nested calls
- `func-pure-immutability` - Spread + structuredClone over mutation

### 6. ES6+ Features (MEDIUM) - 4 rules

- `es-modern-syntax` - Destructuring, spread, template literals, arrow functions
- `es-optional-chaining` - `?.` and `??` over verbose && chains and || fallbacks
- `es-generators` - yield + async generators over loading everything into memory
- `es-modules` - Named/default/dynamic imports over CommonJS require

### 7. Performance (MEDIUM) - 1 rule

- `perf-debounce-throttle` - Debounce, throttle, lazy evaluation over firing on every event

## Framework Setup

### Express.js

```typescript
import express from "express";
import helmet from "helmet";
import cors from "cors";
import compression from "compression";

const app = express();
app.use(helmet());
app.use(cors({ origin: process.env.ALLOWED_ORIGINS?.split(",") }));
app.use(compression());
app.use(express.json({ limit: "10mb" }));
```

### Fastify

```typescript
import Fastify from "fastify";
import helmet from "@fastify/helmet";
import cors from "@fastify/cors";

const fastify = Fastify({ logger: true });
await fastify.register(helmet);
await fastify.register(cors, { origin: true });
```

### Vitest

```typescript
import { defineConfig } from "vitest/config";
export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    coverage: { provider: "v8", reporter: ["text", "json", "html"] },
  },
});
```

### Jest

```typescript
const config = {
  preset: "ts-jest",
  testEnvironment: "node",
  coverageThreshold: { global: { branches: 80, functions: 80, lines: 80 } },
};
```

## How to Use

Read individual rule files for detailed Bad/Good examples:

```
rules/ts-generics.md
rules/backend-layered-architecture.md
rules/test-unit-pure.md
```
