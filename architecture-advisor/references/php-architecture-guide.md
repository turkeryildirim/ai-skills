---
name: php-architecture-guide
description: PHP/Laravel/Symfony/WordPress architecture patterns, benchmarks, and anti-patterns for architectural analysis.
type: reference
---

# PHP Architecture Guide

Reference patterns and benchmarks for PHP project architecture analysis. Covers Laravel, Symfony, and WordPress.

## Maturity Levels

| Level | Description | Signals |
|-------|-------------|---------|
| **Level 1** | Ad-hoc | No framework conventions, global functions, raw SQL everywhere |
| **Level 2** | Framework Aware | Uses framework routing and ORM, but fat controllers |
| **Level 3** | Layered | Controller → Service/Action → Repository separation |
| **Level 4** | Domain-Oriented | Domain objects, value objects, events, CQRS patterns |
| **Level 5** | Fully Testable | All dependencies injected, interfaces used, >70% test coverage |

Most projects should target Level 3-4. Level 5 is appropriate for complex domains.

---

## Laravel Architecture Benchmarks

### Healthy Controller
```php
// ✅ Thin controller — max 30 lines
class OrderController extends Controller
{
    public function store(CreateOrderRequest $request, CreateOrderAction $action): JsonResponse
    {
        $order = $action->execute($request->validated());
        return new OrderResource($order);
    }
}
```

### Healthy Service / Action Class
```php
// ✅ Single-purpose, injectable, no HTTP dependencies
class CreateOrderAction
{
    public function __construct(
        private readonly PaymentGateway $payment,
        private readonly OrderRepository $orders,
    ) {}

    public function execute(array $data): Order
    {
        // Business logic only — no Request, no Response
    }
}
```

### Healthy Repository
```php
// ✅ Data access only, returns domain objects
interface OrderRepository
{
    public function findById(int $id): ?Order;
    public function create(array $data): Order;
    public function findByUser(int $userId): Collection;
}
```

---

## Laravel Pattern Reference

| Pattern | When to Use | When NOT to Use |
|---------|------------|-----------------|
| **Action Class** | Single-purpose operations (RegisterUser, CreateOrder) | Simple CRUD with no logic |
| **Service Class** | Multi-step business workflows, stateful operations | Simple pass-through to repository |
| **Repository** | Complex query logic, multiple data sources | Simple Eloquent CRUD |
| **Form Request** | ALL write endpoints (POST, PUT, PATCH) | Never skip — always use |
| **API Resource** | All JSON responses | Never return raw Model::toArray() |
| **Events + Listeners** | Side effects (email, notification, audit log) | Core business logic |
| **Policies** | Authorization for model operations | Authentication |
| **Observers** | Cross-cutting model lifecycle concerns | Business logic |

---

## Symfony Architecture Benchmarks

```
Healthy Symfony structure:
src/
├── Command/          → CLI commands
├── Controller/       → Thin, HTTP only
├── DataTransferObject/  → DTOs for input/output
├── Entity/           → Doctrine entities
├── EventListener/    → Symfony event system
├── Repository/       → Doctrine repositories
├── Service/          → Business logic
└── Validator/        → Custom constraints
```

---

## WordPress Architecture Benchmarks

### Plugin Structure
```
my-plugin/
├── my-plugin.php          → Main file: register autoloader, hooks
├── includes/
│   ├── class-plugin.php   → Main plugin class, hook registration
│   ├── class-settings.php → Settings API
│   └── class-ajax.php     → AJAX handlers
├── admin/                 → Admin-specific code
├── public/                → Frontend-specific code
└── languages/             → .pot translation files
```

### Hook Organization
```php
// ✅ All hooks registered in one place (main plugin class)
class MyPlugin {
    public function init(): void {
        add_action('init', [$this, 'register_post_types']);
        add_filter('the_content', [$this, 'modify_content']);
        add_action('wp_ajax_my_action', [$this, 'handle_ajax']);
    }
}
```

---

## PHP Version Feature Usage Guide

| Feature | Available Since | Signal When Absent |
|---------|----------------|-------------------|
| Constructor Property Promotion | PHP 8.0 | Boilerplate in constructors |
| Named Arguments | PHP 8.0 | Long positional argument lists |
| Enums | PHP 8.1 | String/int constants for states |
| Readonly Properties | PHP 8.1 | Manual immutability patterns |
| Intersection Types | PHP 8.1 | Workaround interfaces |
| Property Hooks | PHP 8.4 | Custom get/set methods |
| Fibers (async) | PHP 8.1 | Callback-based async patterns |

When a PHP 8.x project doesn't use enums for domain states, or readonly for value objects — note as a MEDIUM issue.

---

## PSR Compliance Quick Reference

| Standard | What It Covers | Key Check |
|----------|----------------|-----------|
| PSR-4 | Autoloading | Namespace == directory path |
| PSR-12 | Code style | Line length, spacing, braces |
| PSR-3 | Logging | LoggerInterface injection |
| PSR-6/16 | Caching | CacheInterface injection |
| PSR-7 | HTTP Messages | Request/Response interfaces |
| PSR-11 | Container | ContainerInterface |

---

## Common Anti-Patterns

| Anti-Pattern | Signs | Impact |
|-------------|-------|--------|
| **Fat Controller** | >50 lines of business logic | Untestable, duplicated across CLI/HTTP |
| **God Service** | Service with 15+ public methods | Multiple responsibilities, hard to test |
| **Repository-less Eloquent** | Model queries directly in controllers | Cannot swap ORM, scattered query logic |
| **Static Facade in Domain** | `Mail::`, `Queue::`, `Cache::` in service | Cannot mock, tight framework coupling |
| **Anemic Domain Model** | Models with only getters/setters, no behavior | Logic scattered across services |
| **Missing Interface** | Concrete class used across 5+ files | Cannot mock, cannot swap implementation |
