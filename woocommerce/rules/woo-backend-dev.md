---
title: WooCommerce Backend Development Conventions
impact: CRITICAL
impactDescription: Following WC conventions prevents conflicts and ensures maintainability
tags: woocommerce, backend, conventions, psr-4, di
---

## WooCommerce Backend Development Conventions

**Impact: CRITICAL (ensures code works within WooCommerce's architecture)**

WooCommerce uses PSR-4 autoloading with `Automattic\WooCommerce` namespace. New classes go in `src/Internal/` by default. Use dependency injection via `final public function init()` with `@internal` annotation. No standalone functions — always use class methods.

## Bad Example

```php
function my_wc_modification() {
    add_filter( 'woocommerce_product_get_price', function( $price ) {
        return $price * 1.1;
    } );
}
my_wc_modification();
```

## Good Example

```php
namespace Automattic\WooCommerce\Internal\Product;

use Automattic\WooCommerce\Utilities\StringUtilUtil;

defined( 'ABSPATH' ) || exit;

class PriceModifier {
    public function init(): void {
        add_filter(
            'woocommerce_product_get_price',
            [ $this, 'handle_product_get_price' ],
            10,
            2
        );
    }

    public function handle_product_get_price( float $price, \WC_Product $product ): float {
        return $price * 1.1;
    }
}
```

## Why

- **PSR-4 autoloading** — `Automattic\WooCommerce` namespace, `src/Internal/` for new classes
- **`snake_case` for methods/variables** — WooCommerce convention, not camelCase
- **Methods default to `private`** — pure methods must be `static`; open methods need justification
- **Hook callbacks named `handle_{hook_name}`** — consistent, discoverable naming
- **`@internal` annotation** — blank lines before and after, placed after description before params
- **DI via `init()` method** — `final public function init()` with `@internal` annotation
- **`use` statements** — import namespaced classes, no FQCN inline
- **Yoda conditions** — `if ( true === $result )`, not `if ( $result === true )`
- **`??` over `isset()`** — `$value ?? 'default'` instead of `isset( $value ) ? $value : 'default'`
- **`@since` version** — from WooCommerce `$version` property, strip `-dev` suffix

Reference: [WooCommerce Backend Dev Skill](https://github.com/woocommerce/woocommerce/tree/trunk/.ai/skills/woocommerce-backend-dev)
