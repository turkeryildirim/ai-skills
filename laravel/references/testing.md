# Laravel 13 Testing — Pest PHP 4 & PHPUnit 12

24 rules across 6 categories. Supports both Pest PHP 4 and PHPUnit 12 (Laravel 13 ships with `phpunit/phpunit: ^12.5.12`).

See `testing-deep.md` for the long-form Pest-specialist guide (factories, coverage, mocking, data providers).

## When to Load

- Writing feature or unit tests
- Testing HTTP endpoints or API responses
- Creating factories / test data
- Asserting database state
- Faking Mail, Queue, Notification, Event, Storage, or AI facades
- Testing authenticated routes / Sanctum tokens
- Organising tests with describe / datasets / hooks

## Framework Detection

1. Check `composer.json` under `require-dev`:
   - `pestphp/pest` → **Pest**
   - only `phpunit/phpunit` → **PHPUnit**
   - both → **Pest wins** (runs on PHPUnit)
2. `tests/Pest.php` exists → Pest
3. Otherwise ask the user

## Syntax Reference

| | Pest | PHPUnit |
|--|------|---------|
| Test function | `test('...', fn() => ...)` | `public function test_...(): void` |
| Readable | `it('...', fn() => ...)` | `#[Test] public function it_...()` |
| Grouping | `describe('...', fn() => ...)` | Test class / nested classes |
| Traits | `uses(RefreshDatabase::class)` | `use RefreshDatabase;` |
| Before each | `beforeEach(fn() => ...)` | `setUp(): void` |
| After each | `afterEach(fn() => ...)` | `tearDown(): void` |
| Parameterised | `->with([...])` | `#[DataProvider]` |
| Global setup | `uses(...)->in('Feature')` | Base `TestCase` |

Core assertions (`assertStatus`, `assertJson`, `assertJsonPath`, `assertDatabaseHas`, `assertModelExists`, `actingAs`, `Mail::fake`, `Queue::fake`, `Event::fake`, `Notification::fake`, `Storage::fake`) are identical in both frameworks.

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | HTTP & Feature Tests | CRITICAL | `http-` |
| 2 | Model Factories | CRITICAL | `factory-` |
| 3 | Database Assertions | HIGH | `db-` |
| 4 | Faking Services | HIGH | `fake-` |
| 5 | Authentication Testing | HIGH | `auth-` |
| 6 | Test Organisation | MEDIUM | `pest-` |

## Rule Index

### 1. HTTP & Feature Tests

- [`http-test-structure`](../rules/http-test-structure.md) — AAA with factories
- [`http-assert-response`](../rules/http-assert-response.md)
- [`http-assert-json-fluent`](../rules/http-assert-json-fluent.md)
- [`http-refresh-database`](../rules/http-refresh-database.md) — RefreshDatabase vs DatabaseTransactions

### 2. Model Factories

- [`factory-define`](../rules/factory-define.md)
- [`factory-states`](../rules/factory-states.md)
- [`factory-sequences`](../rules/factory-sequences.md)
- [`factory-relationships`](../rules/factory-relationships.md)

### 3. Database Assertions

- [`db-assert-has`](../rules/db-assert-has.md)
- [`db-assert-missing`](../rules/db-assert-missing.md)
- [`db-assert-soft-deletes`](../rules/db-assert-soft-deletes.md)

### 4. Faking Services

- [`fake-mail`](../rules/fake-mail.md)
- [`fake-queue`](../rules/fake-queue.md)
- [`fake-notification`](../rules/fake-notification.md)
- [`fake-event`](../rules/fake-event.md)
- [`fake-storage`](../rules/fake-storage.md)
- [`fake-ai-agent`](../rules/fake-ai-agent.md) (Laravel 13+)
- [`fake-ai-media`](../rules/fake-ai-media.md) (Laravel 13+)
- [`fake-ai-data`](../rules/fake-ai-data.md) (Laravel 13+)

### 5. Authentication Testing

- [`auth-acting-as`](../rules/auth-acting-as.md)
- [`auth-sanctum`](../rules/auth-sanctum.md)

### 6. Test Organisation

- [`pest-describe-it`](../rules/pest-describe-it.md)
- [`pest-datasets`](../rules/pest-datasets.md)
- [`pest-hooks`](../rules/pest-hooks.md)

## Essential Patterns

### Pest

```php
uses(RefreshDatabase::class);

test('authenticated user can create a post', function () {
    $user = User::factory()->create();

    $this->actingAs($user)
        ->postJson('/api/posts', ['title' => 'Hello', 'body' => 'Content.'])
        ->assertStatus(201)
        ->assertJsonPath('data.title', 'Hello');

    $this->assertDatabaseHas('posts', ['title' => 'Hello', 'user_id' => $user->id]);
});
```

### PHPUnit

```php
class PostControllerTest extends TestCase
{
    use RefreshDatabase;

    public function test_authenticated_user_can_create_a_post(): void
    {
        $user = User::factory()->create();

        $this->actingAs($user)
            ->postJson('/api/posts', ['title' => 'Hello', 'body' => 'Content.'])
            ->assertStatus(201)
            ->assertJsonPath('data.title', 'Hello');

        $this->assertDatabaseHas('posts', ['title' => 'Hello', 'user_id' => $user->id]);
    }
}
```

### Faking External Services

```php
Queue::fake();
Mail::fake();
Notification::fake();
Storage::fake('avatars');

// ... run the code ...

Queue::assertPushed(PublishPost::class);
Mail::assertSent(WelcomeEmail::class);
Notification::assertSentTo($user, OrderShipped::class);
Storage::disk('avatars')->assertExists('user-1.png');
```

## References

- [Laravel Testing](https://laravel.com/docs/13.x/testing) · [Pest](https://pestphp.com) · [PHPUnit](https://phpunit.de)
