# Laravel 13 Best Practices

Architecture, Eloquent, controllers, validation, and security directives for Laravel 13 + PHP 8.3. 31 rules across 7 categories.

## When to Load

- Creating controllers, models, services, or actions
- Writing migrations or designing schema
- Implementing validation / form requests
- Building APIs
- Making architectural decisions

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Architecture & Structure | CRITICAL | `arch-` |
| 2 | Eloquent & Database | CRITICAL | `eloquent-` |
| 3 | Controllers & Routing | HIGH | `controller-` |
| 4 | Validation & Requests | HIGH | `validation-` |
| 5 | Security | HIGH | `sec-` |

## Rule Index

### 1. Architecture & Structure (CRITICAL)

- [`arch-service-classes`](../rules/arch-service-classes.md) — Extract business logic to services
- [`arch-action-classes`](../rules/arch-action-classes.md) — Single-purpose action classes
- [`arch-repository-pattern`](../rules/arch-repository-pattern.md) — When to use repositories
- [`arch-dto-pattern`](../rules/arch-dto-pattern.md) — Data transfer objects
- [`arch-value-objects`](../rules/arch-value-objects.md) — Encapsulate domain concepts
- [`arch-event-driven`](../rules/arch-event-driven.md) — Decouple with events and listeners
- [`arch-feature-folders`](../rules/arch-feature-folders.md) — Organise by domain / feature
- [`arch-queue-routing`](../rules/arch-queue-routing.md) — Centralised queue routing (Laravel 13+)

### 2. Eloquent & Database (CRITICAL)

- [`eloquent-eager-loading`](../rules/eloquent-eager-loading.md) — Prevent N+1 queries
- [`eloquent-chunking`](../rules/eloquent-chunking.md) — Process large datasets
- [`eloquent-query-scopes`](../rules/eloquent-query-scopes.md) — Reusable query logic
- [`eloquent-model-events`](../rules/eloquent-model-events.md) — Observers for side effects
- [`eloquent-relationships`](../rules/eloquent-relationships.md) — Define relationships properly
- [`eloquent-casts`](../rules/eloquent-casts.md) — Automatic attribute casting
- [`eloquent-accessors-mutators`](../rules/eloquent-accessors-mutators.md) — Transform attributes
- [`eloquent-soft-deletes`](../rules/eloquent-soft-deletes.md) — Safe deletion
- [`eloquent-pruning`](../rules/eloquent-pruning.md) — Automatic cleanup
- [`eloquent-vector-search`](../rules/eloquent-vector-search.md) — Semantic search (Laravel 13+)

### 3. Controllers & Routing (HIGH)

- [`controller-resource-controllers`](../rules/controller-resource-controllers.md)
- [`controller-single-action`](../rules/controller-single-action.md)
- [`controller-resource-methods`](../rules/controller-resource-methods.md)
- [`controller-form-requests`](../rules/controller-form-requests.md)
- [`controller-api-resources`](../rules/controller-api-resources.md)
- [`controller-middleware`](../rules/controller-middleware.md)
- [`controller-dependency-injection`](../rules/controller-dependency-injection.md)

### 4. Validation & Requests (HIGH)

- [`validation-form-requests`](../rules/validation-form-requests.md)
- [`validation-custom-rules`](../rules/validation-custom-rules.md)
- [`validation-conditional-rules`](../rules/validation-conditional-rules.md)
- [`validation-array-validation`](../rules/validation-array-validation.md)
- [`validation-after-hooks`](../rules/validation-after-hooks.md)

### 5. Security (HIGH)

- [`sec-mass-assignment`](../rules/sec-mass-assignment.md) — Protect against mass assignment (see also `references/security.md` for the full OWASP set)

## Essential Patterns

### Controller with Form Request

```php
final class PostController extends Controller
{
    public function store(StorePostRequest $request): RedirectResponse
    {
        $post = Post::create($request->validated());

        return redirect()->route('posts.show', $post)->with('success', 'Post created.');
    }
}
```

### Form Request

```php
final class StorePostRequest extends FormRequest
{
    public function authorize(): bool { return $this->user()->can('create', Post::class); }

    public function rules(): array
    {
        return [
            'title'        => ['required', 'string', 'max:255'],
            'body'         => ['required', 'string', 'min:100'],
            'category_id'  => ['required', 'exists:categories,id'],
            'tags'         => ['nullable', 'array'],
            'tags.*'       => ['exists:tags,id'],
            'published_at' => ['nullable', 'date', 'after:now'],
        ];
    }
}
```

### Service Class

```php
final class PostService
{
    public function __construct(private readonly NotificationService $notifications) {}

    public function publish(Post $post): Post
    {
        return DB::transaction(function () use ($post) {
            $post->update(['published_at' => now(), 'status' => 'published']);
            event(new PostPublished($post));
            $this->notifications->notifyFollowers($post->author, $post);
            return $post->fresh();
        });
    }
}
```

### Eloquent Model

```php
final class Post extends Model
{
    use HasFactory;

    protected $fillable = ['title', 'slug', 'body', 'category_id', 'published_at'];

    protected $casts = ['published_at' => 'datetime'];

    public function author(): BelongsTo { return $this->belongsTo(User::class, 'user_id'); }
    public function tags(): BelongsToMany { return $this->belongsToMany(Tag::class)->withTimestamps(); }

    public function scopePublished(Builder $q): Builder
    {
        return $q->whereNotNull('published_at')->where('published_at', '<=', now());
    }
}
```

### Migration

```php
return new class extends Migration {
    public function up(): void {
        Schema::create('posts', function (Blueprint $t) {
            $t->id();
            $t->foreignId('user_id')->constrained()->cascadeOnDelete();
            $t->foreignId('category_id')->constrained()->cascadeOnDelete();
            $t->string('title');
            $t->string('slug')->unique();
            $t->text('body');
            $t->timestamp('published_at')->nullable();
            $t->timestamps();
            $t->index(['user_id', 'published_at']);
            $t->index('category_id');
        });
    }

    public function down(): void { Schema::dropIfExists('posts'); }
};
```

### Eager Loading

```php
$posts = Post::with(['author', 'category', 'tags'])->get();

$posts = Post::with([
    'author.profile',
    'comments' => fn ($q) => $q->latest()->limit(5),
])->get();
```

## References

- [Laravel 13 docs](https://laravel.com/docs/13.x)
- [PHP 8.3 release notes](https://www.php.net/releases/8.3/en.php)
