---
title: PHP Coupling and Dependency Analysis
impact: HIGH
impactDescription: "Tight coupling to framework internals and concrete classes makes code untestable and brittle"
tags: php, coupling, dependency-injection, interfaces, solid, testability
---

## PHP Coupling and Dependency Analysis

**Impact: HIGH (Tight coupling to framework internals and concrete classes makes code untestable and brittle)**

PHP projects commonly suffer from invisible coupling: static facade calls buried deep in domain classes, concrete services instantiated with `new` inside business logic, and direct database access scattered across layers. These patterns feel convenient but make the code impossible to test in isolation and fragile to change.

## Incorrect

```php
// ❌ Domain class tightly coupled to framework and external services

class OrderService
{
    public function createOrder(array $data): Order
    {
        // ❌ Static facade call — cannot mock in unit test
        \Illuminate\Support\Facades\Log::info('Creating order', $data);

        // ❌ Static DB call — cannot test without database
        $user = \DB::table('users')->where('id', $data['user_id'])->first();

        // ❌ Concrete class instantiation — cannot inject mock
        $payment = new StripePaymentService();
        $result = $payment->charge($data['amount']);

        // ❌ Static cache call — cannot control cache in tests
        \Cache::forget('user_orders_' . $user->id);

        // ❌ Direct Eloquent on concrete model — hard to swap
        return Order::create([...]);
    }
}
```

```php
// ❌ No interface for external services
// 6 different files all do:
$stripe = new StripePaymentService();
// Swapping to PayPal requires changing 6 files
```

## Correct

```php
// ✅ Domain class with injected dependencies

class OrderService
{
    public function __construct(
        private readonly PaymentGateway $payment,       // ✅ Interface, not concrete class
        private readonly OrderRepositoryInterface $orders, // ✅ Repository interface
        private readonly LoggerInterface $logger,       // ✅ PSR-3 logger interface
        private readonly CacheInterface $cache,         // ✅ PSR-6/PSR-16 cache interface
    ) {}

    public function createOrder(array $data): Order
    {
        $this->logger->info('Creating order', $data);

        $result = $this->payment->charge($data['amount']); // ✅ Interface call

        $order = $this->orders->create([...]); // ✅ Repository call

        $this->cache->delete('user_orders_' . $data['user_id']); // ✅ Injected cache

        return $order;
    }
}

// ✅ Interface definition
interface PaymentGateway
{
    public function charge(int $amountCents): PaymentResult;
    public function refund(string $transactionId): RefundResult;
}

// ✅ Bound in AppServiceProvider
$this->app->bind(PaymentGateway::class, StripePaymentService::class);
```

## Coupling Red Flags to Detect

```
CRITICAL coupling signals:
├── Raw SQL (DB::select('SELECT...')) in business logic classes
├── new ConcreteService() inside domain classes
├── Static calls to HTTP/mail/payment services in domain classes
│
HIGH coupling signals:
├── Missing interface for: email, payment, file storage, queue, cache
├── Eloquent Model referenced directly in service constructors
├── Framework-specific Request object passed into domain services
├── Facade calls (Mail::, Queue::, Storage::) inside Action/Service classes
│
MEDIUM coupling signals:
├── Helper functions (app(), resolve()) inside domain classes
├── config() called directly inside domain logic
└── No contracts/ or interfaces/ directory in a medium+ size project
```

## What to Look For During Analysis

```bash
# Check for static facade usage in service/domain classes
grep -r "Facades\\" app/Services/ app/Actions/ app/Domain/
grep -r "::class" app/Services/ | grep -v "::class)"  # Static class references

# Check for concrete instantiation
grep -r "new [A-Z]" app/Services/ app/Actions/

# Check for interface directory
ls app/Contracts/ || ls app/Interfaces/  # If absent, coupling is likely

# Check AppServiceProvider for bindings
cat app/Providers/AppServiceProvider.php
```

## Why

- **Testability**: Constructor-injected interfaces can be replaced with mocks in unit tests — static calls cannot
- **Swap-ability**: Changing from Stripe to PayPal requires one line in `AppServiceProvider`, not grep-and-replace across 10 files
- **Dependency direction**: Domain classes should depend on abstractions (interfaces), not on infrastructure (concrete implementations)
