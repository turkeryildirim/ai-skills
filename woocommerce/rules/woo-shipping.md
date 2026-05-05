---
title: WooCommerce Shipping Methods
impact: HIGH
impactDescription: Shipping calculations affect checkout accuracy and customer trust
tags: woocommerce, shipping, zones, rates, methods
---

## WooCommerce Shipping Methods

**Impact: HIGH (incorrect shipping costs cause order disputes)**

Extend `WC_Shipping_Method` for custom shipping. Register on `woocommerce_shipping_init`. Implement `calculate_shipping()` for rate calculation. Use shipping zones for location-based methods.

## Bad Example

```php
add_filter( 'woocommerce_package_rates', function( $rates ) {
    foreach ( $rates as $rate ) {
        $rate->cost = 10;
    }
    return $rates;
} );
```

## Good Example

```php
class My_Shipping_Method extends \WC_Shipping_Method {
    public function __construct( $instance_id = 0 ) {
        parent::__construct( $instance_id );
        $this->id                 = 'my_shipping';
        $this->method_title       = 'My Custom Shipping';
        $this->method_description = 'Custom shipping rate calculation';
        $this->init();
    }

    public function init(): void {
        $this->init_form_fields();
        $this->init_settings();
        add_action( 'woocommerce_update_options_shipping_' . $this->id, [ $this, 'process_admin_options' ] );
    }

    public function calculate_shipping( $package = [] ): void {
        $weight = 0;
        foreach ( $package['contents'] as $item ) {
            $product = wc_get_product( $item['product_id'] );
            if ( $product && $product->get_weight() ) {
                $weight += $product->get_weight() * $item['quantity'];
            }
        }

        $rate = [
            'id'    => $this->get_rate_id(),
            'label' => $this->title,
            'cost'  => $this->calculate_cost( $weight ),
        ];
        $this->add_rate( $rate );
    }

    private function calculate_cost( float $weight ): float {
        return max( 5.0, $weight * 0.5 );
    }
}

add_action( 'woocommerce_shipping_init', function() {
    new My_Shipping_Method();
} );

add_filter( 'woocommerce_shipping_methods', function( $methods ) {
    $methods['my_shipping'] = 'My_Shipping_Method';
    return $methods;
} );
```

## Why

- **Extend `WC_Shipping_Method`** — integrates with WooCommerce shipping zones and settings
- **Register on `woocommerce_shipping_init`** — ensures WooCommerce is loaded before registration
- **`calculate_shipping($package)`** — receives cart contents, destination, and shipping zone info
- **`$this->add_rate()`** — add one or more rates for the customer to choose from
- **`init_form_fields()`** — admin settings for the shipping method
- **`woocommerce_package_rates` filter** — modify existing rates (use cautiously)
- **Shipping zones** — methods are scoped to zones via `$instance_id`

Reference: [WC_Shipping_Method](https://woocommerce.github.io/code-reference/classes/WC-Shipping-Method.html)
