---
name: javascript
description: Expert JavaScript & TypeScript skill for modern Backend (Node.js), Advanced Testing, TypeScript Type Systems, and ES6+ Patterns. Use for building scalable Node.js services, writing robust Vitest/Jest suites, or designing complex TypeScript type logic.
model: inherit
---

# JavaScript & TypeScript Best Practices

Modern JavaScript & TypeScript patterns for backend development, testing, advanced types, and ES6+ features. Contains 43 rules organized into 7 categories.

## Specialized Agents

Specialized personas for different JS/TS roles. Load these from `agents/` to provide expert context.

| Agent | Role | Focus |
|-------|------|-------|
| **javascript-pro** | JS Expert | Node.js, async patterns, ES6+, performance. |
| **typescript-pro** | TS Master | Advanced types, generics, strict safety, enterprise patterns. |

## When to Use

Reference these guidelines when:
- Building REST APIs, GraphQL servers, or microservices with Node.js
- Writing or reviewing TypeScript code with advanced types
- Setting up test infrastructure (unit, integration, E2E)
- Refactoring legacy JS to modern ES6+ syntax
- Implementing authentication, validation, and middleware patterns

## Basic Coverage

```typescript
// Async/Await with Error Handling ← async-await-patterns
async function fetchData() {
  try {
    const data = await Promise.all([task1(), task2()]); // ← async-promise-combinators
  } catch (err) {
    throw new AppError('FETCH_FAILED', 500); // ← backend-custom-errors
  }
}

// Discriminated Unions ← ts-discriminated-unions
type Result = { status: 'success'; data: string } | { status: 'error'; error: Error };

// Zod Validation ← backend-input-validation
const UserSchema = z.object({ id: z.string().uuid(), email: z.string().email() });
```

## Core Directives

### MUST DO

- Use `async/await` and handle errors with `try/catch` or global error handlers
- Leverage `Promise.all()` for independent concurrent operations
- Use **Strict TypeScript** mode and avoid `any` at all costs
- Implement **Zod/Valibot** for runtime input validation
- Follow **Layered Architecture** (Controller -> Service -> Repository)
- Use **Discriminated Unions** for complex state or response types
- Write **AAA (Arrange-Act-Assert)** style tests with Vitest or Jest
- Use **Structured Logging** (e.g., Pino) and capture `request_id`

### MUST NOT DO

- Use sequential `await` for independent operations (causing bottlenecks)
- Cast types with `as` unless absolutely necessary (prefer type guards)
- Put business logic directly into controllers or route handlers
- Mutate objects/arrays directly (prefer spread or `structuredClone`)
- Use `require()` in modern projects (prefer ES Modules)
- Log sensitive data like passwords or full authorization tokens
- Ignore `unhandledRejection` or `uncaughtException` events

## Category Index — When to Load Which Reference

| # | Category | Impact | Load when… | Reference | Prefix | Rules |
|--:|----------|:------:|------------|-----------|--------|:-----:|
| 1 | TypeScript Types | CRITICAL | Designing complex types, generics, or type-safe APIs | (Implicit) | `ts-` | 10 |
| 2 | Async Patterns | CRITICAL | Managing concurrent tasks, timeouts, or retries | (Implicit) | `async-` | 2 |
| 3 | Backend Architecture | HIGH | Structuring Node.js apps, DI, middleware, or DB transactions | (Implicit) | `backend-` | 13 |
| 4 | Testing | HIGH | Writing unit/integration tests, mocking, or fixtures | (Implicit) | `test-` | 10 |
| 5 | Functional Programming | HIGH | Chaining array methods, composition, or immutability | (Implicit) | `func-` | 3 |
| 6 | ES6+ Features | MEDIUM | Using destructuring, spread, or modules | (Implicit) | `es-` | 4 |
| 7 | Performance | MEDIUM | Implementing debouncing, throttling, or lazy loading | (Implicit) | `perf-` | 1 |

## Rule Index

### 1. TypeScript Types (`ts-`) — CRITICAL
`ts-generics` · `ts-conditional-types` · `ts-mapped-types` · `ts-template-literal-types` · `ts-utility-types` · `ts-discriminated-unions` · `ts-type-guards` · `ts-pattern-event-emitter` · `ts-pattern-api-client` · `ts-pattern-builder`

### 2. Async Patterns (`async-`) — CRITICAL
`async-promise-combinators` · `async-await-patterns`

### 3. Backend Architecture (`backend-`) — HIGH
`backend-layered-architecture` · `backend-dependency-injection` · `backend-middleware-auth` · `backend-input-validation` · `backend-rate-limiting` · `backend-custom-errors` · `backend-error-handler` · `backend-database-transactions` · `backend-jwt-auth` · `backend-redis-caching` · `backend-api-response` · `backend-graceful-shutdown` · `backend-structured-logging`

### 4. Testing (`test-`) — HIGH
`test-unit-pure` · `test-async-functions` · `test-mocking-modules` · `test-di-mocking` · `test-spying-fakes` · `test-integration-api` · `test-integration-database` · `test-react-components` · `test-react-hooks` · `test-fixtures-factories`

## Validation Checklist

- [ ] `strict: true` is enabled in `tsconfig.json`
- [ ] No `any` types are used; prefer generics or `unknown`
- [ ] Input validation is performed at the boundary (e.g., Zod)
- [ ] Async operations are handled correctly (no missing awaits or sequential bottlenecks)
- [ ] Layered architecture is respected (logic in Services, not Controllers)
- [ ] Tests follow the AAA pattern and provide >80% coverage
- [ ] Sensitive data is redacted from logs
- [ ] Graceful shutdown is implemented for SIGTERM/SIGINT

## External References

- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)
- [Vitest Documentation](https://vitest.dev)
- [Zod Documentation](https://zod.dev)
