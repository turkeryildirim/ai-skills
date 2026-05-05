---
title: WooCommerce Product Development
impact: CRITICAL
impactDescription: Products are the core data model; incorrect handling breaks pricing and inventory
tags: woocommerce, product, pricing, inventory, variations
---

## WooCommerce Product Development

**Impact: CRITICAL (pricing and inventory errors directly impact revenue)**

Use `wc_get_product()` to load products. Access data via getter methods (`get_price()`, `get_stock_quantity()`). Use WooCommerce hooks for price modifications. Extend `WC_Product` for custom product types.

## Bad Example

```php
$price = get_post_meta( $product_id, '_price', true );
$stock = get_post_meta( $product_id, '_stock', true );
$title = get_the_title( $product_id );
```

## Good Example

```php
$product = wc_get_product( $product_id );
if ( ! $product ) {
    return;
}

$price      = $product->get_price();
$stock      = $product->get_stock_quantity();
$title      = $product->get_name();
$regular    = $product->get_regular_price();
$sale       = $product->get_sale_price();
$type       = $product->get_type();
$manage_stock = $product->managing_stock();

// Price modification via hook
add_filter( 'woocommerce_product_get_price', function( $price, $product ) {
    if ( 'my_custom_type' === $product->get_type() ) {
        return my_calculate_price( $product );
    }
    return $price;
}, 10, 2 );
```

## Why

- **`wc_get_product()` over `get_post_meta()`** — uses WooCommerce's data layer with caching and hooks
- **Getter methods** — `$product->get_price()` respects tax, sale pricing, and filters
- **Product types** — simple, variable, grouped, external, and custom types via `WC_Product` extension
- **Variations** — use `$product->get_available_variations()` for variable products
- **Price hooks** — `woocommerce_product_get_price`, `woocommerce_product_get_regular_price`, `woocommerce_product_get_sale_price`
- **Inventory** — `wc_update_product_stock()` for atomic stock changes
- **`woocommerce_product_data_store_cpt_get_products_query`** — filter product queries

Reference: [WC_Product](https://woocommerce.github.io/code-reference/classes/WC-Product.html) | [Product Hooks](https://woocommerce.github.io/code-reference/hooks/hooks.html)
