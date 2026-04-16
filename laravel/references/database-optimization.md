# Laravel Database Optimization

Performance, indexing, caching, pagination, transactions, and migration safety for Laravel 13 + PHP 8.3. 33 rules across 9 categories.

## When to Load

- Writing Eloquent queries or query builder calls
- Diagnosing N+1 problems
- Adding or reviewing indexes
- Implementing Redis caching
- Paginating or processing large datasets
- Wrapping operations in transactions
- Writing production migrations
- Debugging slow queries (EXPLAIN, Debugbar, slow log)

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Query Performance & N+1 | CRITICAL | `query-` |
| 2 | Indexing Strategies | CRITICAL | `index-` |
| 3 | Eloquent Optimization | HIGH | `eloquent-` |
| 4 | Caching with Redis | HIGH | `cache-` |
| 5 | Pagination & Large Datasets | HIGH | `data-` |
| 6 | Transactions & Locking | HIGH | `lock-` |
| 7 | Migrations | HIGH | `migrate-` |
| 8 | Query Debugging | MEDIUM | `debug-` |
| 9 | Naming & Structure | HIGH | `naming-` |

## Rule Index

### 1. Query Performance & N+1 (CRITICAL)

- [`query-eager-loading`](../rules/query-eager-loading.md) — Eliminate N+1
- [`query-prevent-lazy-loading`](../rules/query-prevent-lazy-loading.md) — Prevent lazy loading outside production
- [`query-auto-eager-loading`](../rules/query-auto-eager-loading.md) — Auto-eager loading on models
- [`query-select-columns`](../rules/query-select-columns.md) — Select only needed columns

### 2. Indexing Strategies (CRITICAL)

- [`index-foreign-keys`](../rules/index-foreign-keys.md)
- [`index-composite-indexes`](../rules/index-composite-indexes.md)
- [`index-covering-indexes`](../rules/index-covering-indexes.md)
- [`index-full-text`](../rules/index-full-text.md)

### 3. Eloquent Optimization (HIGH)

- [`eloquent-query-builder-hot-paths`](../rules/eloquent-query-builder-hot-paths.md)
- [`eloquent-with-count-aggregates`](../rules/eloquent-with-count-aggregates.md)
- [`eloquent-subquery-selects`](../rules/eloquent-subquery-selects.md)
- [`eloquent-where-has-optimization`](../rules/eloquent-where-has-optimization.md)

### 4. Caching with Redis (HIGH)

- [`cache-remember`](../rules/cache-remember.md)
- [`cache-invalidation`](../rules/cache-invalidation.md)
- [`cache-tags`](../rules/cache-tags.md)
- [`cache-ttl`](../rules/cache-ttl.md)

### 5. Pagination & Large Datasets (HIGH)

- [`data-cursor-pagination`](../rules/data-cursor-pagination.md)
- [`data-chunk-by-id`](../rules/data-chunk-by-id.md)
- [`data-cursor-iteration`](../rules/data-cursor-iteration.md)
- [`data-avoid-unbounded`](../rules/data-avoid-unbounded.md)

### 6. Transactions & Locking (HIGH)

- [`lock-short-transactions`](../rules/lock-short-transactions.md)
- [`lock-deadlock-retry`](../rules/lock-deadlock-retry.md)
- [`lock-pessimistic-locking`](../rules/lock-pessimistic-locking.md)

### 7. Migrations (HIGH)

- [`migrate-zero-downtime`](../rules/migrate-zero-downtime.md)
- [`migrate-concurrent-indexes`](../rules/migrate-concurrent-indexes.md)
- [`migrate-safe-column-additions`](../rules/migrate-safe-column-additions.md)

### 8. Query Debugging (MEDIUM)

- [`debug-explain-analyze`](../rules/debug-explain-analyze.md)
- [`debug-laravel-debugbar`](../rules/debug-laravel-debugbar.md)
- [`debug-slow-query-log`](../rules/debug-slow-query-log.md)

### 9. Naming & Structure (HIGH)

- [`naming-tables`](../rules/naming-tables.md) — plural snake_case, pivot alphabetical
- [`naming-columns`](../rules/naming-columns.md) — FKs, booleans, timestamps, polymorphic
- [`naming-relationships`](../rules/naming-relationships.md) — singular/plural matching
- [`naming-migrations`](../rules/naming-migrations.md) — migration and index naming

## Essential Patterns

### Prevent Lazy Loading Outside Production

```php
public function boot(): void
{
    Model::preventLazyLoading(!app()->isProduction());
}
```

### Cache Expensive Queries

```php
$popularPosts = Cache::remember('posts:popular', 3600, fn () =>
    Post::query()->withCount('comments')->orderByDesc('comments_count')->take(10)->get()
);
```

### Cursor Pagination

```php
$posts = Post::query()
    ->where('published_at', '<=', now())
    ->orderByDesc('published_at')
    ->cursorPaginate(15);
```

### Aggregate Counts

```php
$users = User::withCount('posts')->get();
foreach ($users as $user) {
    echo "{$user->name}: {$user->posts_count} posts";
}
```

### Chunked Processing

```php
User::query()
    ->where('last_login_at', '<', now()->subYear())
    ->chunkById(1000, fn ($chunk) => $chunk->each->update(['status' => 'inactive']));
```

### Short Transactions

```php
DB::transaction(function () {
    $order = Order::create(['user_id' => auth()->id(), 'total' => $this->total()]);
    $order->items()->createMany($this->cartItems());
    $order->user->decrement('credits', $order->total);
});
```

## References

- [Eloquent](https://laravel.com/docs/13.x/eloquent) · [Queries](https://laravel.com/docs/13.x/queries) · [Cache](https://laravel.com/docs/13.x/cache) · [Pagination](https://laravel.com/docs/13.x/pagination) · [Migrations](https://laravel.com/docs/13.x/migrations) · [Redis](https://laravel.com/docs/13.x/redis)
