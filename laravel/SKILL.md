---
name: laravel
description: Unified Laravel 13 skill covering architecture patterns, Eloquent, controllers, validation, testing (Pest/PHPUnit), database optimization, caching, queues, and OWASP security for Laravel + React/Inertia apps. Use when building, reviewing, auditing, or refactoring any Laravel codebase — including models, migrations, API resources, form requests, service layers, jobs, factories, tests, or security checks.
model: inherit
---

# Laravel (Unified)

A single, comprehensive skill for Laravel 13 + PHP 8.3 development. Covers architecture, Eloquent, validation, testing, database optimization, caching, queues, routing, API design, and OWASP security for Laravel + React/Inertia stacks.

## Specialized Agents

Specialized personas for Laravel development. Load these from `agents/` to provide expert context.

| Agent | Role | Focus |
|-------|------|-------|
| **laravel-pro** | Laravel Expert | Eloquent, service providers, Inertia, security, queues. |

## When to Use

Apply this skill when working on a Laravel 13 codebase for any of the following:
- Designing or structuring an application (controllers, services, actions, DTOs)
- Creating or modifying Eloquent models, relationships, or scopes
- Writing migrations, indexes, or handling zero-downtime schema changes
- Implementing validation with Form Requests or custom rules
- Building RESTful APIs or Inertia-powered frontends
- Writing tests with Pest or PHPUnit
- Optimizing database performance (N+1, indexes, caching)
- Configuring queues and background jobs
- Performing security audits (OWASP Top 10)

## Step 1: Detect Laravel Environment

**Always check the project's Laravel version and setup before giving advice.**

```bash
php artisan --version
php artisan migrate:status
```

Check `composer.json` for Pest vs PHPUnit and Inertia vs Blade stacks.

## Core Directives

### MUST DO

- Use PHP 8.3 features: readonly properties, constructor promotion, strict types
- Type-hint every parameter and return type explicitly
- Define `$fillable` on every model; never use `$guarded = []`
- Eager-load relationships with `->with([...])` to prevent N+1 queries
- Validate all user input via `FormRequest` classes
- Transform API/Inertia responses using **API Resources**
- Wrap multi-step writes in `DB::transaction()` blocks
- Queue slow or I/O intensive work via `ShouldQueue` jobs
- Index every foreign key and column used in `WHERE`, `ORDER BY`, or `JOIN`
- Follow the **Controller -> Form Request -> Service -> Action -> Model** pattern

### MUST NOT DO

- Put business logic directly in controllers (use Services or Actions)
- Concatenate user input into raw SQL queries (always use bindings)
- Return unpaginated or unbounded results from large tables
- Expose sensitive data (tokens, internal flags) via Inertia props or JSON
- Ship with `APP_DEBUG=true` in production
- Disable CSRF protection except for stateless webhooks

## Category Index — When to Load Which Reference

| # | Category | Impact | Load when… | Reference | Rules |
|--:|----------|:------:|------------|-----------|:-----:|
| 1 | Best Practices | CRITICAL | Architecture, services, actions, DTOs | [`references/best-practices.md`](references/best-practices.md) | `arch-`, `controller-` |
| 2 | DB Optimization | CRITICAL | Fixing N+1, indexing, caching, transactions | [`references/database-optimization.md`](references/database-optimization.md) | `query-`, `index-`, `cache-`, `data-` |
| 3 | Security | CRITICAL | Auth, XSS, CSRF, Inertia exposure, OWASP audit | [`references/security.md`](references/security.md) | `sec-` |
| 4 | Testing | HIGH | Writing Pest/PHPUnit tests, factories, fakes | [`references/testing.md`](references/testing.md) | `http-`, `factory-`, `db-`, `fake-`, `auth-`, `pest-` |
| 5 | Eloquent | HIGH | Relationships, scopes, casts, query builder | [`references/eloquent.md`](references/eloquent.md) | `eloquent-` |
| 6 | Queues | HIGH | Jobs, Horizon, retries, batching | [`references/queues.md`](references/queues.md) | `arch-queue-` |

## Rule Index

Refer to the specific prefixes in `rules/` for concrete bad/good examples:
- `arch-`, `controller-`, `eloquent-`, `validation-`, `query-`, `index-`, `cache-`, `data-`, `lock-`, `migrate-`, `debug-`, `naming-`, `sec-`, `http-`, `factory-`, `db-`, `fake-`, `auth-`, `pest-`.

## Validation Checklist

- [ ] All user input is validated via Form Requests
- [ ] No N+1 queries exist; eager loading is used correctly
- [ ] Business logic is extracted from controllers into Services/Actions
- [ ] Sensitive data is redacted from responses/Inertia props
- [ ] Foreign keys and search columns are properly indexed
- [ ] Multi-step operations are wrapped in transactions
- [ ] Tests exist and pass with `RefreshDatabase`
- [ ] Security audit (OWASP) shows no high/critical vulnerabilities

## External References

- [Laravel Documentation](https://laravel.com/docs)
- [Laracasts](https://laracasts.com)
- [Laravel Security Guide](https://laravel.com/docs/security)
- [Pest PHP](https://pestphp.com)
