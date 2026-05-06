---
title: PHP Framework Pattern Adherence
impact: HIGH
impactDescription: "Fighting the framework creates unmaintainable code that can't benefit from upgrades"
tags: php, laravel, symfony, wordpress, framework, patterns, mvc
---

## PHP Framework Pattern Adherence

**Impact: HIGH (Fighting the framework creates unmaintainable code that can't benefit from upgrades)**

Each PHP framework has idiomatic patterns that, when followed, reduce boilerplate, improve testability, and allow the team to benefit from framework upgrades. When projects fight their framework — ignoring built-in features in favor of custom reinventions — the codebase becomes harder to maintain and harder for new developers to understand.

## Incorrect

```php
// ❌ Laravel — Fat controller doing everything
class OrderController extends Controller
{
    public function store(Request $request): JsonResponse
    {
        // ❌ Manual validation (ignore FormRequest)
        if (!$request->has('user_id') || !$request->has('items')) {
            return response()->json(['error' => 'Missing fields'], 422);
        }

        // ❌ Business logic inline
        $total = 0;
        foreach ($request->items as $item) {
            $product = DB::table('products')->where('id', $item['id'])->first();
            $total += $product->price * $item['quantity'];
            DB::table('products')
                ->where('id', $item['id'])
                ->decrement('stock', $item['quantity']);
        }

        // ❌ Raw DB instead of Eloquent
        $orderId = DB::table('orders')->insertGetId([
            'user_id' => $request->user_id,
            'total' => $total,
        ]);

        // ❌ Email sending inline
        Mail::raw("Your order #{$orderId} has been placed.", function ($m) use ($request) {
            $m->to($request->user()->email)->subject('Order Confirmation');
        });

        return response()->json(['order_id' => $orderId]);
    }
}
```

```php
// ❌ WordPress — No hook system, direct output
// Directly echoing HTML from a plugin with no actions/filters
function my_plugin_display() {
    global $wpdb;
    $results = $wpdb->get_results("SELECT * FROM {$wpdb->prefix}products");
    echo '<div class="products">';
    foreach ($results as $product) {
        echo '<p>' . $product->name . '</p>'; // ❌ No escaping
    }
    echo '</div>';
}
```

## Correct

```php
// ✅ Laravel — Idiomatic thin controller
class OrderController extends Controller
{
    public function store(
        CreateOrderRequest $request,    // ✅ Validation in FormRequest
        CreateOrderAction $action       // ✅ Business logic in Action class
    ): JsonResponse {
        $order = $action->execute($request->validated());
        return new OrderResource($order); // ✅ API Resource for response shaping
    }
}

// ✅ Laravel — Action class with single responsibility
class CreateOrderAction
{
    public function __construct(
        private readonly InventoryService $inventory,
        private readonly OrderRepository $orders,
    ) {}

    public function execute(array $data): Order
    {
        $order = $this->orders->create($data);
        $this->inventory->deductItems($data['items']);
        OrderPlaced::dispatch($order); // ✅ Event for side effects (email, etc.)
        return $order;
    }
}
```

```php
// ✅ WordPress — Proper hook usage with escaping
add_action('init', 'my_plugin_init');
add_shortcode('my_products', 'my_plugin_render_products');

function my_plugin_render_products(): string {
    global $wpdb;
    $results = $wpdb->get_results(
        $wpdb->prepare("SELECT * FROM %i", $wpdb->prefix . 'products')
    );

    ob_start();
    foreach ($results as $product) {
        echo '<p>' . esc_html($product->name) . '</p>'; // ✅ Escaped
    }
    return ob_get_clean();
}
```

## Framework-Specific Pattern Checklist

### Laravel
```
✅ FormRequest classes for all write operations (no inline $request->validate())
✅ API Resources for JSON responses (no manual array construction)
✅ Action or Service classes for business logic (no logic in controllers)
✅ Events + Listeners for side effects (email, notifications, logging)
✅ Eloquent for data access (no raw DB:: in controllers)
✅ Policies for authorization (no inline Gate:: checks in controllers)

❌ Fat controllers (>50 lines of business logic)
❌ Raw DB:: queries in controllers
❌ Inline mail/notification sending in controllers
❌ dd(), var_dump() left in production code
```

### WordPress
```
✅ All output escaped (esc_html, esc_attr, esc_url, wp_kses)
✅ All database queries use $wpdb->prepare()
✅ Custom functionality attached via actions/filters (not direct calls)
✅ Options stored via get_option/update_option (not raw DB)
✅ Nonce verification on all form submissions

❌ Direct SQL without prepare()
❌ Unescaped output
❌ Business logic in template files
❌ Deregistering core hooks without a documented reason
```

## Why

- **Upgrade path**: Idiomatic code benefits from framework improvements automatically
- **Team velocity**: New developers understand idiomatic patterns immediately; custom patterns require documentation
- **Testability**: FormRequests, Action classes, and Events are all independently testable without bootstrapping HTTP
