---
title: WooCommerce Hook Callback Conventions
impact: CRITICAL
impactDescription: Consistent hook naming and registration prevents conflicts and aids debugging
tags: woocommerce, hooks, conventions, callbacks
---

## WooCommerce Hook Callback Conventions

**Impact: CRITICAL (consistent hooks prevent conflicts with 600K+ WooCommerce extensions)**

Name hook callbacks `handle_{hook_name}`. Register via `init()` method with `@internal` annotation. Always declare accepted_args matching the hook's do_action/apply_filters signature.

## Bad Example

```php
add_filter( 'woocommerce_product_get_price', 'my_price', 10, 2 );
function my_price( $price, $product ) {
    return $price * 1.1;
}

add_action( 'woocommerce_order_status_completed', function( $order_id ) {
    $order = wc_get_order( $order_id );
    $order->add_order_note( 'Completed!' );
} );
```

## Good Example

```php
class My_Plugin_Hooks {
    public function init(): void {
        add_filter(
            'woocommerce_product_get_price',
            [ $this, 'handle_product_get_price' ],
            10,
            2
        );
        add_action(
            'woocommerce_order_status_completed',
            [ $this, 'handle_order_status_completed' ],
            10,
            1
        );
    }

    /**
     * Modify product price.
     *
     * @internal
     *
     * @param float      $price   Product price.
     * @param WC_Product $product Product instance.
     * @return float
     */
    public function handle_product_get_price( float $price, \WC_Product $product ): float {
        return $price * 1.1;
    }

    /**
     * Handle order completion.
     *
     * @internal
     *
     * @param int $order_id Order ID.
     */
    public function handle_order_status_completed( int $order_id ): void {
        $order = wc_get_order( $order_id );
        if ( ! $order ) {
            return;
        }
        $order->add_order_note( 'Completed!' );
    }
}
```

## Why

- **`handle_{hook_name}` naming** — consistent, searchable, maps directly to hook name
- **`@internal` annotation** — marks callback as internal implementation detail
- **Always verify return values** — `wc_get_order()` can return `false`
- **Declare `accepted_args`** — must match the hook's actual argument count
- **Class-based registration** — enables `remove_filter()` / `remove_action()` by reference
- **No closures for distributable code** — closures cannot be removed by other plugins
- **Type-hint parameters** — `float $price`, `WC_Product $product`, `int $order_id`

Reference: [WooCommerce Hooks](https://woocommerce.github.io/code-reference/hooks/hooks.html)
