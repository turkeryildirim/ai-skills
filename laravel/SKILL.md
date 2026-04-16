---
name: laravel
description: Unified Laravel 13 skill covering architecture patterns, Eloquent, controllers, validation, testing (Pest/PHPUnit), database optimization, caching, queues, and OWASP security for Laravel + React/Inertia apps. Use when building, reviewing, auditing, or refactoring any Laravel codebase — including models, migrations, API resources, form requests, service layers, jobs, factories, tests, or security checks.
license: MIT
metadata:
  author: consolidated (laravel-best-practices, laravel-database-optimization, laravel-owasp-security, laravel-patterns, laravel-specialist, laravel-testing)
  version: "1.0.0"
  laravelVersion: "13.x"
  phpVersion: "8.3+"
  pestVersion: "4.x"
  phpunitVersion: "12.x"
---

# Laravel (Unified)

A single, comprehensive skill for Laravel 13 + PHP 8.3 development. Covers architecture, Eloquent, validation, testing, database optimization, caching, queues, routing, API design, and OWASP security for Laravel + React/Inertia stacks.

Detailed material lives in `references/` — load only the sheet(s) relevant to the current task. Individual rule files (bad/good example format) live in `rules/`.

## When to Use

Apply this skill when working on a Laravel 13 codebase for any of the following:

- Designing or structuring an application (controllers, services, actions, DTOs, repositories, events)
- Creating or modifying Eloquent models, relationships, scopes, casts, or observers
- Writing or reviewing migrations, indexes, foreign keys, or zero-downtime schema changes
- Implementing validation with form requests, custom rules, or conditional rules
- Building RESTful APIs with resource controllers, API resources, and pagination
- Writing tests (feature, unit) with Pest PHP 4 or PHPUnit 12 — factories, fakes, HTTP assertions
- Fixing N+1 queries, slow queries, unbounded result sets, or missing indexes
- Adding Redis caching, cache invalidation, or cache tags
- Configuring queues, jobs, retries, backoff, or Horizon
- Running an OWASP Top 10 security audit or writing secure auth / payment / upload code
- Reviewing React/Inertia.js data exposure, CSRF, or XSS concerns

## Routing to References

Pick the reference(s) that match the task. Do not load everything.

| Task | Reference |
|------|-----------|
| Architecture, controllers, form requests, services, actions, DTOs, value objects | `references/best-practices.md` |
| N+1, indexes, caching, pagination, transactions, slow-query debugging | `references/database-optimization.md` |
| Auth, CSRF, mass assignment, XSS, Inertia data exposure, OWASP audit | `references/security.md` |
| Pest / PHPUnit, factories, fakes, HTTP assertions, auth testing | `references/testing.md` |
| Production patterns, layered boundaries, query objects, scoped bindings | `references/patterns.md` |
| Deep Eloquent reference (relationships, scopes, casts, query builder) | `references/eloquent.md` |
| Jobs, Horizon, batching, retries, failed-job handling | `references/queues.md` |
| Routes, middleware, API resources, scoped model binding | `references/routing.md` |

Each reference links to the individual `rules/<prefix>-*.md` files for concrete bad/good code examples.

## Rule Categories (Quick Index)

Rule files under `rules/` are prefixed by domain. All 94 rules from the six source skills are preserved.

| Prefix | Domain | Examples |
|--------|--------|----------|
| `arch-` | Architecture (services, actions, DTOs, repos, events, feature folders) | `arch-service-classes`, `arch-action-classes`, `arch-dto-pattern` |
| `controller-` | Controllers (resource, single-action, form requests, DI, middleware) | `controller-resource-controllers`, `controller-form-requests` |
| `eloquent-` | Eloquent models, scopes, casts, eager loading, subqueries | `eloquent-eager-loading`, `eloquent-with-count-aggregates` |
| `validation-` | Form requests, custom rules, arrays, conditional, after hooks | `validation-form-requests`, `validation-custom-rules` |
| `query-` | Query performance, N+1 prevention, select columns | `query-eager-loading`, `query-prevent-lazy-loading` |
| `index-` | FK, composite, covering, full-text indexes | `index-composite-indexes`, `index-foreign-keys` |
| `cache-` | Redis cache: remember, invalidation, tags, TTL | `cache-remember`, `cache-invalidation` |
| `data-` | Pagination, cursor iteration, chunking, unbounded queries | `data-cursor-pagination`, `data-chunk-by-id` |
| `lock-` | Transactions, pessimistic locking, deadlock retry | `lock-short-transactions`, `lock-deadlock-retry` |
| `migrate-` | Zero-downtime, concurrent indexes, safe column additions | `migrate-zero-downtime`, `migrate-concurrent-indexes` |
| `debug-` | EXPLAIN, Debugbar, slow query log | `debug-explain-analyze`, `debug-laravel-debugbar` |
| `naming-` | Tables, columns, relationships, migrations | `naming-tables`, `naming-columns` |
| `sec-` | OWASP Top 10: access control, crypto, injection, CSRF, Inertia | `sec-broken-access-control`, `sec-injection-prevention` |
| `http-` | HTTP feature tests, JSON assertions, RefreshDatabase | `http-test-structure`, `http-assert-json-fluent` |
| `factory-` | Define, states, sequences, relationships | `factory-define`, `factory-states` |
| `db-` | DB assertions (has, missing, soft-deleted) | `db-assert-has`, `db-assert-missing` |
| `fake-` | Facade fakes (Mail, Queue, Event, Storage, Notification, AI) | `fake-mail`, `fake-queue`, `fake-ai-agent` |
| `auth-` | `actingAs`, Sanctum | `auth-acting-as`, `auth-sanctum` |
| `pest-` | Test organisation (describe/it, datasets, hooks) | `pest-describe-it`, `pest-datasets` |

## Core Directives

### MUST DO

- Use PHP 8.3 features: readonly properties, constructor promotion, typed enums, strict types
- Type-hint every parameter and return type
- Define `$fillable` explicitly on every model (never `$guarded = []`)
- Eager-load relationships with `->with([...])` at call sites; enable `Model::preventLazyLoading()` outside production
- Validate all user input via `FormRequest` classes; never pass `$request->all()` to `create()`/`update()`
- Transform API responses with API Resources — never return raw `toArray()` to Inertia or JSON
- Wrap multi-step writes in short `DB::transaction()` blocks
- Queue slow or external-IO work (mail, HTTP, reports) via `ShouldQueue` jobs
- Write tests with `RefreshDatabase`; fake external services (`Mail::fake()`, `Queue::fake()`, etc.)
- Index every foreign key column and every column used in `WHERE`, `ORDER BY`, or `JOIN`
- Hash passwords with bcrypt/argon2 via `Hash::make()` or the `'hashed'` cast
- Use `Crypt::encryptString()` or `'encrypted'` casts for sensitive at-rest data
- Regenerate the session (`session()->regenerate()`) after login

### MUST NOT DO

- Concatenate user input into `whereRaw`/`selectRaw`/`orderByRaw` — always use `?` bindings
- Use `$guarded = []` or `forceFill()`/`forceCreate()` with unvalidated input
- Put business logic in controllers (belongs in services or action classes)
- Return unpaginated or unbounded queries on large tables
- Cause N+1 queries — never loop and touch a relation without eager loading
- Use `dangerouslySetInnerHTML` without `DOMPurify.sanitize()` on user content
- Expose passwords, tokens, or internal flags via Inertia props — they render into `data-page`
- Disable CSRF except for stateless webhooks / external callbacks
- Ship with `APP_DEBUG=true` in production or commit `.env`
- Run raw `exec()`/`shell_exec()`/`system()`/`passthru()` on user input
- Rely on React UI role checks — always re-enforce on the server

## Essential Patterns

### Controller → Form Request → Service → Action → Model

```php
// Controller — thin, delegates to action/service
final class PostController extends Controller
{
    public function __construct(private readonly PublishPostAction $publishPost) {}

    public function store(StorePostRequest $request): JsonResponse
    {
        $post = $this->publishPost->handle($request->toDto());

        return response()->json(['data' => PostResource::make($post)], 201);
    }
}

// Form Request — validation + authorization + DTO transform
final class StorePostRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user()->can('create', Post::class);
    }

    public function rules(): array
    {
        return [
            'title' => ['required', 'string', 'max:255'],
            'body'  => ['required', 'string', 'min:100'],
        ];
    }

    public function toDto(): PublishPostData
    {
        return new PublishPostData(...$this->validated());
    }
}

// Action — single-purpose, idempotent
final class PublishPostAction
{
    public function handle(PublishPostData $data): Post
    {
        return DB::transaction(fn () => Post::create([
            'title'        => $data->title,
            'body'         => $data->body,
            'user_id'      => auth()->id(),
            'published_at' => now(),
        ]));
    }
}
```

### Eloquent — Eager Loading + Scopes + Casts

```php
final class Post extends Model
{
    use HasFactory, SoftDeletes;

    protected $fillable = ['title', 'body', 'user_id', 'published_at'];

    protected $casts = [
        'published_at' => 'immutable_datetime',
        'status'       => PostStatus::class,
    ];

    public function author(): BelongsTo { return $this->belongsTo(User::class, 'user_id'); }

    public function scopePublished(Builder $q): Builder
    {
        return $q->whereNotNull('published_at')->where('published_at', '<=', now());
    }
}

// Call site — eager load, paginate, use withCount
$posts = Post::query()
    ->published()
    ->with(['author', 'tags'])
    ->withCount('comments')
    ->cursorPaginate(15);
```

### Test — Pest feature test with RefreshDatabase + fakes

```php
uses(RefreshDatabase::class);

it('publishes a post and queues follower notifications', function (): void {
    Queue::fake();
    $user = User::factory()->create();

    $this->actingAs($user)
        ->postJson('/api/posts', ['title' => 'Hello', 'body' => str_repeat('x', 100)])
        ->assertCreated()
        ->assertJsonPath('data.title', 'Hello');

    $this->assertDatabaseHas('posts', ['title' => 'Hello', 'user_id' => $user->id]);
    Queue::assertPushed(NotifyFollowers::class);
});
```

### OWASP Audit Output Format

When running a security audit, for every checklist item output one of:
- **PASS** `path/file.php` — brief confirmation
- **FAIL** `path/file.php:line` — description of the vulnerability (never reproduce secrets / tokens / .env content) + fix recommendation
- **N/A** — when the check does not apply

See `references/security.md` for the full OWASP Top 10 checklist, React/Inertia checks, and report template.

## Framework Detection (Testing)

Before writing test code, detect the project's testing framework:

1. Check `composer.json` under `require-dev`:
   - `pestphp/pest` present → **Pest syntax**
   - only `phpunit/phpunit` → **PHPUnit syntax**
   - both → **Pest wins** (it runs on PHPUnit)
2. If `tests/Pest.php` exists → Pest is configured
3. If still unclear → ask the user

Core assertions (`assertStatus`, `assertJson`, `assertDatabaseHas`, `actingAs`, `Mail::fake`, `Queue::fake`, …) are identical in both frameworks — only test declaration, hooks, grouping, and datasets differ. See `references/testing.md` for the side-by-side syntax table.

## Stack Detection (Security)

When running `references/security.md` audits, first detect React + Inertia.js:

- `app/Http/Middleware/HandleInertiaRequests.php` exists
- `resources/js/*.{tsx,jsx}` files present
- `inertiajs/inertia-laravel` in `composer.json`
- `@inertiajs/react` in `package.json`

If detected, apply both the Laravel OWASP checklist and the R1–R6 React/Inertia checks. Otherwise apply Laravel OWASP only.

## Validation Checkpoints

Run these at each workflow stage before considering the step complete:

| Stage | Command | Expected |
|-------|---------|----------|
| After migration | `php artisan migrate:status` | All show `Ran` |
| After routing | `php artisan route:list --path=api` | New routes appear |
| After job dispatch | `php artisan queue:work --once` | Processes without exception |
| After implementation | `php artisan test --coverage` | >85% coverage, 0 failures |
| Before PR | `./vendor/bin/pint --test` | PSR-12 passes |
| Security gate | `composer audit && npm audit` | No high/critical CVEs |

## How to Use the Rule Files

Each `rules/<name>.md` file contains:
- YAML frontmatter (title, impact, tags)
- Why it matters in Laravel 13 context
- **Bad Example** with explanation
- **Good Example** with explanation
- Laravel 13 / PHP 8.3 specific context and upstream documentation links

Open the matching rule file when you need a concrete before/after for a specific directive.
